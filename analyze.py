from alerts import send_alert

CPU_THRESHOLD = 80.0  # threshold for CPU usage
DISK_THRESHOLD = 90.0  # threshold for disk usage (%)
MEMORY_THRESHOLD = 75.0  # threshold for memory usage (%)

def analyze_data(data):
    # Analyzing CPU usage
    if 'cpu_usage' in data and float(data['cpu_usage']) > CPU_THRESHOLD:
        send_alert(data['device_id'], f'CPU usage threshold exceeded: {data["cpu_usage"]}%')

    # Analyzing disk usage
    if 'disk_usage' in data and float(data['disk_usage']) > DISK_THRESHOLD:
        send_alert(data['device_id'], f'Disk usage threshold exceeded: {data["disk_usage"]}%')

    # Analyzing memory usage
    if 'memory_usage' in data and float(data['memory_usage']) > MEMORY_THRESHOLD:
        send_alert(data['device_id'], f'Memory usage threshold exceeded: {data["memory_usage"]}%')

    print('Data analyzed')
