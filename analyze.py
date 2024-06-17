from alerts import send_alert

THRESHOLD = 80.0  # threshold for CPU usage

def analyze_data(data):
    # Analyzing logic
    if 'cpu_usage' in data and float(data['cpu_usage']) > THRESHOLD:
        send_alert(data['device_id'], f'CPU usage threshold exceeded: {data["cpu_usage"]}%')
    print('Data analyzed')
