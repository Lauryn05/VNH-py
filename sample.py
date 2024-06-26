from pymongo import MongoClient
import datetime

# MongoDB Atlas connection string
connection_string = "mongodb+srv://lauryn:2004@vnh.yitygnq.mongodb.net/?retryWrites=true&w=majority&appName=VNH"

# Connect to MongoDB Atlas
try:
    client = MongoClient(connection_string)
    db = client.VNH  # Replace 'VNH' with your database name
    print("Connected to MongoDB Atlas successfully!")

    # Sample data for each collection
    devices = [
        {"device_id": "1", "name": "Router", "ip_address": "192.168.1.1", "type": "Router", "location": "Data Center", "status": "Active", "last_updated": datetime.datetime.utcnow()},
        {"device_id": "2", "name": "Switch", "ip_address": "192.168.1.2", "type": "Switch", "location": "Office", "status": "Active", "last_updated": datetime.datetime.utcnow()}
    ]

    configurations = [
        {"device_id": "1", "configuration": "Default Configuration", "timestamp": datetime.datetime.utcnow()},
        {"device_id": "2", "configuration": "Custom Configuration", "timestamp": datetime.datetime.utcnow()}
    ]

    traffic_logs = [
        {"device_id": "1", "timestamp": datetime.datetime.utcnow(), "traffic_in": 100.0, "traffic_out": 150.0, "protocol": "TCP", "src_ip": "10.0.0.1", "dst_ip": "10.0.0.2", "src_port": 12345, "dst_port": 80},
        {"device_id": "2", "timestamp": datetime.datetime.utcnow(), "traffic_in": 200.0, "traffic_out": 250.0, "protocol": "UDP", "src_ip": "10.0.0.3", "dst_ip": "10.0.0.4", "src_port": 54321, "dst_port": 443}
    ]

    performance_metrics = [
        {"device_id": "1", "timestamp": datetime.datetime.utcnow(), "cpu_usage": 30.5, "memory_usage": 40.5, "disk_usage": 50.5},
        {"device_id": "2", "timestamp": datetime.datetime.utcnow(), "cpu_usage": 35.5, "memory_usage": 45.5, "disk_usage": 55.5}
    ]

    alerts = [
        {"device_id": "1", "alert_type": "CPU High", "message": "CPU usage exceeded threshold", "timestamp": datetime.datetime.utcnow(), "status": "Active", "resolved_at": None},
        {"device_id": "2", "alert_type": "Memory Low", "message": "Memory usage below threshold", "timestamp": datetime.datetime.utcnow(), "status": "Resolved", "resolved_at": datetime.datetime.utcnow()}
    ]

    users = [
        {"username": "admin", "password_hash": "hashed_password", "email": "admin@example.com", "role": "Admin", "last_login": datetime.datetime.utcnow()},
        {"username": "user", "password_hash": "hashed_password", "email": "user@example.com", "role": "User", "last_login": datetime.datetime.utcnow()}
    ]

    # Insert data into collections
    db.devices.insert_many(devices)
    db.configurations.insert_many(configurations)
    db.traffic_logs.insert_many(traffic_logs)
    db.performance_metrics.insert_many(performance_metrics)
    db.alerts.insert_many(alerts)
    db.users.insert_many(users)

    print("Sample data inserted successfully!")

except Exception as e:
    print(f"Error inserting data: {e}")
