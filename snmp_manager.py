from flask import Flask, request, jsonify
from pysnmp.hlapi import *
from db import mongo, init_db
import time
from bson import ObjectId
import nmap

# Initialize Flask application
app = Flask(__name__)
# Load configuration from config
app.config.from_object('config.Config')

# Initialize MongoDB connection
init_db(app)

# Function to scan the network and find live hosts
def scan_network(network):
    nm = nmap.PortScanner()  # Initialize nmap PortScanner
    nm.scan(hosts=network, arguments='-sn')  # Perform a network scan with no port scanning
    # Get list of live hosts
    live_hosts = [host for host in nm.all_hosts() if nm[host].state() == 'up']
    return live_hosts

# Function to discover devices using SNMP GET
def discover_devices(live_hosts):
    devices = []

    for ip in live_hosts:
        try:
            # SNMP GET to discover devices using sysDescr OID
            for (errorIndication, errorStatus, errorIndex, varBinds) in getCmd(
                SnmpEngine(),  # SNMP engine instance
                CommunityData('public'),  # SNMP community
                UdpTransportTarget((ip, 161)),  # Target IP and SNMP port
                ContextData(),  # SNMP context
                ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))  # OID for system description
            ):
                if errorIndication:  # Handle SNMP error indication
                    print(f"Error discovering devices at {ip}: {errorIndication}")
                elif errorStatus:  # Handle SNMP error status
                    print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
                else:
                    for varBind in varBinds:
                        # Create device dictionary
                        device = {'ip': ip, 'oid': varBind[0].prettyPrint(), 'value': varBind[1].prettyPrint()}
                        devices.append(device)  # Add device to list
                        # Update MongoDB with device information
                        mongo.db.devices.update_one({'ip': device['ip']}, {'$set': device}, upsert=True)
        except Exception as e:  # Handle exceptions
            print(f"Exception for IP {ip}: {e}")

    return {'devices': devices}  # Return discovered devices

# Function to configure device settings via SNMP SET
def configure_device(device_id, data):
    try:
        # Find device by ID in MongoDB
        device = mongo.db.devices.find_one({'_id': ObjectId(device_id)})
        if not device:
            return {'error': 'Device not found'}

        # Create configuration dictionary
        configuration = {
            'device_id': device_id,
            'hostname': data.get('hostname'),
            'ip_address': data.get('ip_address'),
            'timestamp': time.time()
        }
        # Insert configuration into MongoDB
        mongo.db.configurations.insert_one(configuration)

        # Prepare fields for device update
        update_fields = {}
        if 'hostname' in data:
            update_fields['name'] = data['hostname']
        if 'ip_address' in data:
            update_fields['ip_address'] = data['ip_address']
        # Update device information in MongoDB
        mongo.db.devices.update_one({'_id': ObjectId(device_id)}, {'$set': update_fields})

        # Perform SNMP SET operations
        snmp_errors = []

        if 'hostname' in data:
            hostname_target = ObjectIdentity('1.3.6.1.2.1.1.5.0')  # OID for hostname
            hostname_var_binds = (ObjectType(hostname_target, OctetString(data['hostname'])),)

            hostname_errorIndication, hostname_errorStatus, hostname_errorIndex, hostname_varBinds = setCmd(
                SnmpEngine(),  # SNMP engine instance
                CommunityData('private'),  # SNMP community
                UdpTransportTarget((device['ip'], 161)),  # Target device IP and SNMP port
                ContextData(),  # SNMP context
                *hostname_var_binds  # Variable bindings for SNMP SET
            )

            if hostname_errorIndication:  # Handle SNMP error indication
                snmp_errors.append(f"Hostname Error: {hostname_errorIndication}")
            elif hostname_errorStatus:  # Handle SNMP error status
                snmp_errors.append(f"Hostname Error: {hostname_errorStatus.prettyPrint()}")

        if 'ip_address' in data:
            ip_target = ObjectIdentity('1.3.6.1.4.1.9.2.1.1.7.0')  # OID for IP address
            ip_var_binds = (ObjectType(ip_target, IpAddress(data['ip_address'])),)

            ip_errorIndication, ip_errorStatus, ip_errorIndex, ip_varBinds = setCmd(
                SnmpEngine(),  # SNMP engine instance
                CommunityData('private'),  # SNMP community
                UdpTransportTarget((device['ip'], 161)),  # Target device IP and SNMP port
                ContextData(),  # SNMP context
                *ip_var_binds  # Variable bindings for SNMP SET
            )

            if ip_errorIndication:  # Handle SNMP error indication
                snmp_errors.append(f"IP Address Error: {ip_errorIndication}")
            elif ip_errorStatus:  # Handle SNMP error status
                snmp_errors.append(f"IP Address Error: {ip_errorStatus.prettyPrint()}")

        if snmp_errors:  # Return errors if any occurred
            return {'error': ' ; '.join(snmp_errors)}

        return {'message': 'Device configuration updated successfully'}  # Success message

    except Exception as e:  # Handle exceptions
        return {'error': str(e)}

# Route to discover devices on the network
@app.route('/discover_devices', methods=['GET'])
def discover():
    network = '0.0.0.0/0'  # Define network range
    live_hosts = scan_network(network)  # Scan network for live hosts
    result = discover_devices(live_hosts)  # Discover devices
    return jsonify(result), 200  # Return discovered devices as JSON

# Route to receive performance metrics from devices
@app.route('/receive_metrics', methods=['POST'])
def receive_metrics():
    data = request.get_json()  # Get JSON data from request
    if not data:
        return jsonify({"error": "Invalid data"}), 400  # Return error if data is invalid

    try:
        device_details = data.get('details', {})  # Get device details
        metrics = data.get('metrics', {})  # Get performance metrics

        # Find and update device in MongoDB
        device_entry = mongo.db.devices.find_one_and_update(
            {'sysName': device_details.get('sysName')},
            {'$set': device_details},
            upsert=True,
            return_document=True
        )

        # Create performance metric dictionary
        performance_metric = {
            'device_id': device_entry['_id'],
            'cpu_usage': metrics.get('cpu_usage'),
            'memory_usage': metrics.get('memory_usage'),
            'disk_usage': metrics.get('disk_usage'),
            'timestamp': time.time()
        }
        # Insert performance metric into MongoDB
        mongo.db.performance_metrics.insert_one(performance_metric)

        return jsonify({"message": "Metrics received successfully"}), 200  # Success message
    
    except Exception as e:  # Handle exceptions
        return jsonify({"error": str(e)}), 500

# Route to configure device settings
@app.route('/configure_device/<device_id>', methods=['POST'])
def configure(device_id):
    try:
        data = request.get_json()  # Get JSON data from request
        if not data or 'hostname' not in data or 'ip_address' not in data:
            return jsonify({"error": "Invalid data"}), 400  # Return error if data is invalid

        result = configure_device(device_id, data)  # Configure device
        return jsonify(result), 200  # Return result as JSON
    
    except Exception as e:  # Handle exceptions
        return jsonify({"error": str(e)}), 500

# Main entry point to run the Flask application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Run the app on all available IP addresses on port 5000
