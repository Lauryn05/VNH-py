# snmp_manager.py
from pysnmp.hlapi import *
from db import mongo
from bson import ObjectId

def discover_devices():
    devices = []

    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget(('demo.snmplabs.com', 161)),
        ContextData(),
        ObjectType(ObjectIdentity('DEMO-MIB', 'demoString', 0))
    ):
        if errorIndication:
            print(f"Error discovering devices: {errorIndication}")
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
        else:
            for varBind in varBinds:
                device = {'oid': varBind[0].prettyPrint(), 'value': varBind[1].prettyPrint()}
                devices.append(device)
                mongo.db.devices.update_one({'oid': device['oid']}, {'$set': device}, upsert=True)

    return {'devices': devices}

def configure_device(device_id, data):
    try:
        # Construct SNMP request
        target = ObjectIdentity(data['oid'])
        var_binds = (ObjectType(target, data['value']),)

        errorIndication, errorStatus, errorIndex, varBinds = setCmd(
            SnmpEngine(),
            CommunityData('private'),
            UdpTransportTarget(('demo.snmplabs.com', 161)),
            ContextData(),
            *var_binds
        )

        if errorIndication or errorStatus:
            return {'error': str(errorIndication or errorStatus)}

        # Update MongoDB with configured value
        mongo.db.devices.update_one({'_id': ObjectId(device_id)}, {'$set': {'configured_value': data['value']}})
        
        return {'message': f'Device {device_id} configured successfully'}
    
    except Exception as e:
        return {'error': f'Failed to configure device {device_id}: {e}'}

def fetch_device_data(device_id):
    device = mongo.db.devices.find_one({'_id': device_id})
    # Placeholder for actual SNMP data retrieval logic
    data = {'device_id': device_id, 'data': 'sample_data'}
    return data
