# snmp_agent.py
from pysnmp.hlapi import *
from pysnmp.smi import builder, view, compiler, rfc1902
from mongoengine import connect
import os
from manage import Device, PerformanceMetric
import datetime

def connect_to_mongo():
    connection_string = "mongodb://lauryn:2004@atlas-sql-6660eeffd618ae1ad10794bb-bmdn7.a.query.mongodb.net/?ssl=true&authSource=admin"
    connect(host=connection_string)

def discover_devices():
    mibBuilder = builder.MibBuilder()
    mib_dir = os.path.join(os.path.dirname(__file__), 'mibs')
    mibBuilder.addMibSources(builder.DirMibSource(mib_dir))
    mibViewController = view.MibViewController(mibBuilder)

    try:
        compiler.addMibCompiler(mibBuilder, sources=['file://' + mib_dir])
        mibBuilder.loadModules('DEMO-MIB')
        print("MIB DEMO-MIB loaded successfully.")
    except Exception as e:
        print(f"Error loading MIB module: {e}")
        return []

    snmpEngine = SnmpEngine()
    devices = []

    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(snmpEngine,
                   CommunityData('public', mpModel=0),
                   UdpTransportTarget(('demo.snmplabs.com', 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity('DEMO-MIB::demoString')))
        )
    except Exception as e:
        print(f"Error executing SNMP command: {e}")
        return []

    if errorIndication:
        print(f"Error: {errorIndication}")
    elif errorStatus:
        print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
    else:
        for varBind in varBinds:
            device = {'oid': varBind[0].prettyPrint(), 'description': varBind[1].prettyPrint()}
            devices.append(device)

    return {'devices': devices}

def store_metrics_in_mongo(devices):
    for device in devices['devices']:
        device_entry = Device(
            device_id=device['oid'],
            name=device['description'],
            ip_address='demo.snmplabs.com',
            type='SNMP Device',
            status='Active'
        )
        device_entry.save()

        # Placeholder for actual SNMP metrics retrieval logic
        performance_metric = PerformanceMetric(
            device_id=device_entry.device_id,
            cpu_usage=20.0,  
            memory_usage=50.0, 
            disk_usage=70.0
        )
        performance_metric.save()

if __name__ == "__main__":
    connect_to_mongo()
    devices = discover_devices()
    if devices:
        store_metrics_in_mongo(devices)