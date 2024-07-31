from alerts import send_alert  # Importing send_alert function from alerts.py
from db import mongo
from bson import ObjectId

CPU_THRESHOLD = 80.0  # threshold for CPU usage
DISK_THRESHOLD = 90.0  # threshold for disk usage (%)
MEMORY_THRESHOLD = 75.0  # threshold for memory usage (%)

def analyze_data():
    try:
        # Retrieve metrics from the database
        metrics_collection = mongo.db.performance_metrics.find()
        
        for metrics_entry in metrics_collection:
            device_id = metrics_entry['device_id']
            cpu_usage = metrics_entry.get('cpu_usage')
            disk_usage = metrics_entry.get('disk_usage')
            memory_usage = metrics_entry.get('memory_usage')
            
            # Analyzing CPU usage
            if cpu_usage is not None and float(cpu_usage) > CPU_THRESHOLD:
                send_alert(device_id, f'CPU usage threshold exceeded: {cpu_usage}%')

            # Analyzing disk usage
            if disk_usage is not None and float(disk_usage) > DISK_THRESHOLD:
                send_alert(device_id, f'Disk usage threshold exceeded: {disk_usage}%')

            # Analyzing memory usage
            if memory_usage is not None and float(memory_usage) > MEMORY_THRESHOLD:
                send_alert(device_id, f'Memory usage threshold exceeded: {memory_usage}%')

        print('Data analyzed')
    
    except Exception as e:
        print(f"Error analyzing data: {e}")

if __name__ == "__main__":
    analyze_data()
