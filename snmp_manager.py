from flask import Flask, request, jsonify
from pysnmp.hlapi import *
from db import mongo, init_db
import time
from bson import ObjectId
import nmap

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize MongoDB connection
init_db(app)

def scan_network(network):
    nm = nmap.PortScanner()
    nm.scan(hosts=network, arguments='-sn')
    live_hosts = [host for host in nm.all_hosts() if nm[host].state() == 'up']
    return live_hosts

def discover_devices(live_hosts):
    devices = []

    for ip in live_hosts:
        try:
            # SNMP GET to discover devices using sysDescr OID
            for (errorIndication, errorStatus, errorIndex, varBinds) in getCmd(
                SnmpEngine(),
                CommunityData('public'),
                UdpTransportTarget((ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))
            ):
                if errorIndication:
                    print(f"Error discovering devices at {ip}: {errorIndication}")
                elif errorStatus:
                    print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
                else:
                    for varBind in varBinds:
                        device = {'ip': ip, 'oid': varBind[0].prettyPrint(), 'value': varBind[1].prettyPrint()}
                        devices.append(device)
                        mongo.db.devices.update_one({'ip': device['ip']}, {'$set': device}, upsert=True)
        except Exception as e:
            print(f"Exception for IP {ip}: {e}")

    return {'devices': devices}

def configure_device(device_id, data):
    try:
        device = mongo.db.devices.find_one({'_id': ObjectId(device_id)})
        if not device:
            return {'error': 'Device not found'}

        # Update configurations collection
        configuration = {
            'device_id': device_id,
            'hostname': data.get('hostname'),
            'ip_address': data.get('ip_address'),
            'timestamp': time.time()
        }
        mongo.db.configurations.insert_one(configuration)

        # Update devices collection
        update_fields = {}
        if 'hostname' in data:
            update_fields['name'] = data['hostname']
        if 'ip_address' in data:
            update_fields['ip_address'] = data['ip_address']
        mongo.db.devices.update_one({'_id': ObjectId(device_id)}, {'$set': update_fields})

        # SNMP SET operations
        snmp_errors = []

        if 'hostname' in data:
            hostname_target = ObjectIdentity('1.3.6.1.2.1.1.5.0')
            hostname_var_binds = (ObjectType(hostname_target, OctetString(data['hostname'])),)

            hostname_errorIndication, hostname_errorStatus, hostname_errorIndex, hostname_varBinds = setCmd(
                SnmpEngine(),
                CommunityData('private'),
                UdpTransportTarget((device['ip'], 161)),  # Send to the device's IP
                ContextData(),
                *hostname_var_binds
            )

            if hostname_errorIndication:
                snmp_errors.append(f"Hostname Error: {hostname_errorIndication}")
            elif hostname_errorStatus:
                snmp_errors.append(f"Hostname Error: {hostname_errorStatus.prettyPrint()}")

        if 'ip_address' in data:
            ip_target = ObjectIdentity('1.3.6.1.4.1.9.2.1.1.7.0')
            ip_var_binds = (ObjectType(ip_target, IpAddress(data['ip_address'])),)

            ip_errorIndication, ip_errorStatus, ip_errorIndex, ip_varBinds = setCmd(
                SnmpEngine(),
                CommunityData('private'),
                UdpTransportTarget((device['ip'], 161)),  # Send to the device's IP
                ContextData(),
                *ip_var_binds
            )

            if ip_errorIndication:
                snmp_errors.append(f"IP Address Error: {ip_errorIndication}")
            elif ip_errorStatus:
                snmp_errors.append(f"IP Address Error: {ip_errorStatus.prettyPrint()}")

        if snmp_errors:
            return {'error': ' ; '.join(snmp_errors)}

        return {'message': 'Device configuration updated successfully'}

    except Exception as e:
        return {'error': str(e)}

@app.route('/discover_devices', methods=['GET'])
def discover():
    network = '0.0.0.0/0'
    live_hosts = scan_network(network)
    result = discover_devices(live_hosts)
    return jsonify(result), 200

@app.route('/receive_metrics', methods=['POST'])
def receive_metrics():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    try:
        device_details = data.get('details', {})
        metrics = data.get('metrics', {})

        device_entry = mongo.db.devices.find_one_and_update(
            {'sysName': device_details.get('sysName')},
            {'$set': device_details},
            upsert=True,
            return_document=True
        )

        performance_metric = {
            'device_id': device_entry['_id'],
            'cpu_usage': metrics.get('cpu_usage'),
            'memory_usage': metrics.get('memory_usage'),
            'disk_usage': metrics.get('disk_usage'),
            'timestamp': time.time()
        }
        mongo.db.performance_metrics.insert_one(performance_metric)

        return jsonify({"message": "Metrics received successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/configure_device/<device_id>', methods=['POST'])
def configure(device_id):
    try:
        data = request.get_json()
        if not data or 'hostname' not in data or 'ip_address' not in data:
            return jsonify({"error": "Invalid data"}), 400

        result = configure_device(device_id, data)
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/register_user', methods=['POST'])
def register_user():
    try:
        user_data = request.get_json()
        if not user_data or 'username' not in user_data or 'email' not in user_data:
            return jsonify({"error": "Invalid user data"}), 400

        mongo.db.users.insert_one(user_data)
        return jsonify({"message": "User registered successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
