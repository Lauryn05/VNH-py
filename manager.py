from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from pysnmp.hlapi import *

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/network_manager'
mongo = PyMongo(app)

@app.route('/api/device', methods=['GET'])
def get_devices():
    devices = mongo.db.devices.find()
    return jsonify({'devices': [device['name'] for device in devices]})

@app.route('/api/device/<name>', methods=['GET'])
def get_device(name):
    device = mongo.db.devices.find_one({'name': name})
    return jsonify(device)

@app.route('/api/device', methods=['POST'])
def add_device():
    name = request.json['name']
    ip = request.json['ip']
    community = request.json['community']
    version = request.json['version']
    mongo.db.devices.insert_one({'name': name, 'ip': ip, 'community': community, 'version': version})
    return jsonify({'message': 'Device added successfully'})

def send_trap(ip, community, version, oid, value):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        sendNotification(SnmpEngine(),
                         CommunityData(community),
                         UdpTransportTarget((ip, 162)),
                         ContextData(),
                         'trap',
                         NotificationType(ObjectIdentity(oid), (value,))
                         )
    )
    if errorIndication:
        print('Error:', errorIndication)

if __name__ == '__main__':
    app.run(debug=True)
