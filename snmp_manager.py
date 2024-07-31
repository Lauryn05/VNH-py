from flask import Flask, request, jsonify, render_template
from pysnmp.hlapi import *  # Importing necessary modules
from db import mongo, init_db  # Importing MongoDB related modules
from bson import ObjectId  # Importing ObjectId for MongoDB queries
import time  # Importing time module for timestamping

app = Flask(__name__)  # Creating a Flask application instance
app.config.from_object('config.Config')  # Loading configuration from Config class in config.py

# Initialize MongoDB connection
init_db(app)

@app.route('/')
def home():
    # Fetch all performance metrics from MongoDB and render them in dashboard.html
    performance_metrics = list(mongo.db.performance_metrics.find())
    return render_template('dashboard.html', performance_metrics=performance_metrics)

def discover_devices():
    devices = []  # Initializing an empty list to store discovered devices

    # SNMP walk to discover devices using DEMO-MIB and demoString OID
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget(('demo.snmplabs.com', 161)),
        ContextData(),
        ObjectType(ObjectIdentity('DEMO-MIB', 'demoString', 0))
    ):
        if errorIndication:
            print(f"Error discovering devices: {errorIndication}")  # Print error if SNMP operation fails
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            # Print error status and index if SNMP operation fails
        else:
            for varBind in varBinds:
                device = {'oid': varBind[0].prettyPrint(), 'value': varBind[1].prettyPrint()}
                devices.append(device)  # Add discovered device to devices list
                mongo.db.devices.update_one({'oid': device['oid']}, {'$set': device}, upsert=True)
                # Update MongoDB with discovered device information

    return {'devices': devices}  # Return discovered devices as a dictionary

def configure_device(device_id, data):
    try:
        # Perform SNMP set operation for hostname
        if 'hostname' in data:
            hostname_target = ObjectIdentity('1.3.6.1.2.1.1.5.0')  # OID for sysName
            hostname_var_binds = (ObjectType(hostname_target, OctetString(data['hostname'])),)  # Set hostname value

            hostname_errorIndication, hostname_errorStatus, hostname_errorIndex, hostname_varBinds = setCmd(
                SnmpEngine(),
                CommunityData('private'),
                UdpTransportTarget(('demo.snmplabs.com', 161)),
                ContextData(),
                *hostname_var_binds
            )

            if hostname_errorIndication or hostname_errorStatus:
                return {'error': str(hostname_errorIndication or hostname_errorStatus)}  # Return error if SNMP operation fails

        # Perform SNMP set operation for IP address
        if 'ip_address' in data:
            ip_target = ObjectIdentity('1.3.6.1.4.1.9.2.1.1.7.0')  # Example OID for IP address
            ip_var_binds = (ObjectType(ip_target, IpAddress(data['ip_address'])),)  # Set IP address value

            ip_errorIndication, ip_errorStatus, ip_errorIndex, ip_varBinds = setCmd(
                SnmpEngine(),
                CommunityData('private'),
                UdpTransportTarget(('demo.snmplabs.com', 161)),
                ContextData(),
                *ip_var_binds
            )

            if ip_errorIndication or ip_errorStatus:
                return {'error': str(ip_errorIndication or ip_errorStatus)}  # Return error if SNMP operation fails

        # Update MongoDB with configured value for the device
        mongo.db.devices.update_one({'_id': ObjectId(device_id)}, {'$set': {'configured_value': data}})

        return {'message': f'Device {device_id} configured successfully'}  # Return success message
    
    except Exception as e:
        return {'error': f'Failed to configure device {device_id}: {e}'}  # Return error if exception occurs


@app.route('/receive_metrics', methods=['POST'])
def receive_metrics():
    data = request.get_json()  # Retrieve JSON data from POST request
    if not data:
        return jsonify({"error": "Invalid data"}), 400  # Return error if data is not provided

    try:
        device_details = data.get('details', {})  # Retrieve device details from JSON data
        metrics = data.get('metrics', {})  # Retrieve metrics from JSON data

        # Store or update device details in MongoDB
        device_entry = mongo.db.devices.find_one_and_update(
            {'sysName': device_details.get('sysName')},
            {'$set': device_details},
            upsert=True,
            return_document=True
        )

        # Prepare performance metric data to store in MongoDB
        performance_metric = {
            'device_id': device_entry['_id'],
            'cpu_usage': metrics.get('cpu_usage'),
            'memory_usage': metrics.get('memory_usage'),
            'disk_usage': metrics.get('disk_usage'),
            'timestamp': time.time()  # Timestamp when metrics are received
        }
        mongo.db.performance_metrics.insert_one(performance_metric)  # Insert performance metrics into MongoDB

        return jsonify({"message": "Metrics received successfully"}), 200  # Return success message
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if exception occurs

@app.route('/discover_devices', methods=['GET'])
def discover():
    result = discover_devices()  # Discover devices using SNMP
    return jsonify(result), 200  # Return discovered devices as JSON

@app.route('/configure_device/<device_id>', methods=['POST'])
def configure(device_id):
    try:
        data = request.get_json()  # Retrieve JSON data from POST request
        if not data or 'hostname' not in data or 'ip_address' not in data or 'oid' not in data:
            return jsonify({"error": "Invalid data"}), 400  # Return error if data is invalid

        result = configure_device(device_id, data)  # Configure device using received data
        return jsonify(result), 200  # Return result as JSON
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if exception occurs

@app.route('/register_user', methods=['POST'])
def register_user():
    try:
        user_data = request.get_json()  # Retrieve JSON user data from POST request
        if not user_data or 'username' not in user_data or 'email' not in user_data:
            return jsonify({"error": "Invalid user data"}), 400  # Return error if user data is invalid

        mongo.db.users.insert_one(user_data)  # Insert user data into MongoDB

        return jsonify({"message": "User registered successfully"}), 200  # Return success message
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if exception occurs

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Run Flask app on all available network interfaces, port 5000