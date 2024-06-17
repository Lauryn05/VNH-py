from pysnmp.hlapi import *
from pymongo import MongoClient
from pysnmp.smi import builder, view, compiler, rfc1902
import os

def discover_devices():
    # Initialize MIB builder and load MIB files
    mibBuilder = builder.MibBuilder()
    
    # Add local directory with MIB files
    mib_dir = os.path.join(os.path.dirname(__file__), 'mibs')
    mibBuilder.addMibSources(builder.DirMibSource(mib_dir))
    
    # Print the MIB sources for debugging
    print("MIB Sources: ", mibBuilder.getMibSources())
    
    mibViewController = view.MibViewController(mibBuilder)

    # Load custom MIB file
    try:
        # Ensure the module name matches the one defined in the MIB file
        mibBuilder.loadModules('DEMO-MIB')
    except Exception as e:
        print(f"Error loading MIB module: {e}")
        return []

    # Initialize SNMP engine
    snmpEngine = SnmpEngine()

    # SNMP GET command to discover devices
    devices = []
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(snmpEngine,
               CommunityData('public', mpModel=0),
               UdpTransportTarget(('demo.snmplabs.com', 161)),
               ContextData(),
               ObjectType(ObjectIdentity('DEMO-MIB', 'demoString', 0)))
    )

    if errorIndication:
        print(f"Error: {errorIndication}")
    elif errorStatus:
        print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1] or '?'}")
    else:
        for varBind in varBinds:
            device = {'oid': varBind[0].prettyPrint(), 'description': varBind[1].prettyPrint()}
            devices.append(device)

    return {'devices': devices}

# Testing the discovery function
if __name__ == "__main__":
    print(discover_devices())
