from pysnmp.hlapi import *
from pymongo import MongoClient
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

    return {'devices': devices}

# Testing the discovery function
if __name__ == "__main__":
    print(discover_devices())
