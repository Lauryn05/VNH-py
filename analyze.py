from alerts import send_alert

def analyze_data(data):
    # Analyzing logic
    if 'anomaly' in data:
        send_alert(data['device_id'], 'Anomaly detected')
    print('Data analyzed')
