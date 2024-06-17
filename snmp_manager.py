from pysnmp.hlapi import *
from db import mongo
from datetime import datetime
from pysnmp.smi import builder, view, compiler, rfc1902

def discover_devices():
    # Initialize MIB builder and load MIB files
    mibBuilder = builder.MibBuilder()
    compiler.addMibCompiler(mibBuilder, sources=['http://mibs.snmplabs.com/asn1/@mib@'])
    mibViewController = view.MibViewController(mibBuilder)

    # Load custom MIB file if necessary
    mibBuilder.loadModules('SNMPv2-MIB')

    # Initialize SNMP engine
    snmpEngine = SnmpEngine()

    # SNMP GET command to discover devices
    devices = []
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(snmpEngine,
               CommunityData('public', mpModel=0),
               UdpTransportTarget(('demo.snmplabs.com', 161)),
               ContextData(),
               ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
    )

    if errorIndication:
        print(f"Error: {errorIndication}")
    elif errorStatus:
        print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1] or '?'}")
    else:
        for varBind in varBinds:
            device = {'oid': varBind[0].prettyPrint(), 'description': varBind[1].prettyPrint()}
            devices.append(device)
            mongo.db.devices.insert_one({
                'device_id': device['oid'],
                'name': device['description'],
                'ip_address': 'demo.snmplabs.com',
                'status': 'Active',
                'last_updated': datetime.utcnow()
            })

    return {'devices': devices}

def configure_device(device_id, data):
    # SNMP configuration logic
    target = ObjectIdentity(data['oid'])
    var_binds = (ObjectType(target, data['value']),)
    errorIndication, errorStatus, errorIndex, varBinds = setCmd(SnmpEngine(), CommunityData('private'),
                                                                UdpTransportTarget(('demo.snmplabs.com', 161)),
                                                                ContextData(), *var_binds)
    if errorIndication or errorStatus:
        return {'error': str(errorIndication or errorStatus)}
    mongo.db.devices.update_one({'_id': device_id}, {'$set': {'configured_value': data['value']}})
    return {'message': f'Device {device_id} configured successfully'}

def fetch_device_data(device_id):
    # Fetch device data logic
    device = mongo.db.devices.find_one({'_id': device_id})
    # SNMP get request to fetch data
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData('public', mpModel=0),
               UdpTransportTarget((device['ip_address'], 161)),
               ContextData(),
               ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0)))
    )
    if errorIndication or errorStatus:
        return {'error': str(errorIndication or errorStatus)}
    
    data = {'device_id': device_id, 'timestamp': datetime.utcnow()}
    for varBind in varBinds:
        data[varBind[0].prettyPrint()] = varBind[1].prettyPrint()
    
    # Save fetched data to MongoDB
    mongo.db.performance_metrics.insert_one(data)
    return data
