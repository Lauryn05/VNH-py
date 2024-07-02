import psutil
import requests
import json
import socket
import datetime
from pysnmp.hlapi import *

def collect_metrics():
    # Collect system metrics
    metrics = {
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('C:\\').percent,  # Adjust disk path as needed
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    return metrics

def collect_device_details():
    # Function to get the IP address associated with the Ethernet interface
    def get_ethernet_ip():
        try:
            interfaces = psutil.net_if_addrs()
            for interface_name, snic_list in interfaces.items():
                for snic in snic_list:
                    if snic.family == socket.AF_INET and 'Ethernet' in interface_name:
                        return snic.address
        except Exception as e:
            print(f"Error retrieving Ethernet IP: {e}")
        return None

    # Collect device details using MIB
    device_details = {
        'device_id': get_snmp_data('1.3.6.1.2.1.1.5.0'),  # sysName OID
        'name': 'LAURYNSPC',  # sysName OID
        'ip_address': get_ethernet_ip(),  # Ethernet IP address
        'type': 'Windows',  # sysDescr OID
        'location': get_snmp_data('1.3.6.1.2.1.1.6.0'),  # sysLocation OID
        'status': 'Active',
        'last_updated': datetime.datetime.utcnow().isoformat()
    }
    return device_details

def get_snmp_data(oid):
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData('public'),
            UdpTransportTarget(('192.168.1.3', 161)),  # Adjust to the target device IP and port
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        
        if errorIndication:
            print(f"Error: {errorIndication}")
            return None
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            return None
        else:
            for varBind in varBinds:
                return varBind[1].prettyPrint()
    except Exception as e:
        print(f"Error retrieving SNMP data: {e}")
        return None

def send_metrics_to_manager(manager_url):
    metrics = collect_metrics()
    device_details = collect_device_details()
    
    data = {
        'details': device_details,
        'metrics': metrics
    }
    
    try:
        response = requests.post(f"{manager_url}/receive_metrics", json=data)
        if response.status_code == 200:
            print("Metrics sent successfully")
        else:
            print(f"Failed to send metrics: {response.status_code}")
    except Exception as e:
        print(f"Error sending metrics: {e}")

if __name__ == "__main__":
    MANAGER_URL = "http://192.168.1.3:5000"  # Replace with actual manager IP address
    send_metrics_to_manager(MANAGER_URL)
