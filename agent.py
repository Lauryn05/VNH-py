from flask import Flask, jsonify
from pysnmp.hlapi import *

app = Flask(__name__)

@app.route('/api/trap', methods=['POST'])
def receive_trap():
    data = request.json
    print('Received Trap:', data)
    return jsonify({'message': 'Trap received'})

def send_get_request(ip, community, oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )
    if errorIndication:
        print('Error:', errorIndication)
    else:
        for varBind in varBinds:
            print(varBind)

if __name__ == '__main__':
    app.run(debug=True)
