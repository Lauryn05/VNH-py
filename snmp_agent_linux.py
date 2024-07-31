import psutil  # system and process utilities
import requests  # Import requests for making HTTP requests
import json  # Import json for JSON handling
import socket  # Import socket for network-related functions
import datetime  # Import datetime for date and time handling
from pysnmp.hlapi import *  # Import PySNMP for SNMP operations

def collect_metrics():
    # Collect system metrics using psutil
    metrics = {
        'cpu_usage': psutil.cpu_percent(interval=1),  # Get CPU usage percentage
        'memory_usage': psutil.virtual_memory().percent,  # Get memory usage percentage
        'disk_usage': psutil.disk_usage('/').percent,  # Get disk usage percentage of root partition
        'timestamp': datetime.datetime.utcnow().isoformat()  # Get current UTC timestamp in ISO format
    }
    return metrics

def collect_device_details():
    # Function to get the IP address associated with the Ethernet interface
    def get_ethernet_ip():
        try: # Iterate over all network interfaces and their associated addresses
            for interface, snic_tuple in psutil.net_if_addrs().items():
                for snic in snic_tuple: # Check if the address family is IPv4 and the interface name contains 'eth'
                    if snic.family == socket.AF_INET and 'eth' in interface:
                        return snic.address # Return the IPv4 address associated with the Ethernet interface
        except Exception as e:
            print(f"Error retrieving Ethernet IP: {e}") # Print an error message if any exception occurs
        return None # Return None if no Ethernet IP address is found or an error occurs

    # Collect device details using SNMP
    device_details = {
        'device_id': get_snmp_data('1.3.6.1.2.1.1.5.0'),  # Get sysName OID for device ID
        'name': get_snmp_data('1.3.6.1.2.1.1.5.0'),  # Get sysName OID for device name
        'ip_address': get_ethernet_ip(),  # Get Ethernet IP address
        'type': get_snmp_data('1.3.6.1.2.1.1.1.0'),  # Get sysDescr OID for device type
        'location': get_snmp_data('1.3.6.1.2.1.1.6.0'),  # Get sysLocation OID for device location
        'status': 'Active',  # Set device status
        'last_updated': datetime.datetime.utcnow().isoformat()  # Get current UTC timestamp for last update
    }
    return device_details

def get_snmp_data(oid):
    try:
        # Perform SNMP GET operation for given OID
        iterator = getCmd(
            SnmpEngine(),  # Create SNMP engine instance
            CommunityData('public'),  # Set SNMP community string
            UdpTransportTarget(('10.0.2.15', 161)),  # Set managed device IP and port
            ContextData(),  # Create SNMP context data
            ObjectType(ObjectIdentity(oid))  # Define SNMP object type using OID
        )
        
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)  # Retrieve SNMP data
        
        if errorIndication:
            print(f"Error: {errorIndication}")  # Print error indication if SNMP operation fails
            return None
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            return None
        else:
            for varBind in varBinds:
                return varBind[1].prettyPrint()  # Return SNMP data
    except Exception as e:
        print(f"Error retrieving SNMP data: {e}")  # Print error if SNMP operation encounters exception
        return None

def send_metrics_to_manager(manager_url):
    metrics = collect_metrics()  # Collect system metrics
    device_details = collect_device_details()  # Collect device details
    
    data = {
        'details': device_details,  # Include device details in data
        'metrics': metrics  # Include metrics in data
    }
    
    try:
        response = requests.post(f"{manager_url}/receive_metrics", json=data)  # Send POST request with data to manager URL
        if response.status_code == 200:
            print("Metrics sent successfully")  # Print success message if metrics are sent successfully
        else:
            print(f"Failed to send metrics: {response.status_code}")  # Print error message if sending metrics fails
    except Exception as e:
        print(f"Error sending metrics: {e}")  # Print error if HTTP request encounters exception

if __name__ == "__main__":
    MANAGER_URL = "http://192.168.1.3:5000"  # Manager IP address
    send_metrics_to_manager(MANAGER_URL)  # Call function to send metrics to manager URL
