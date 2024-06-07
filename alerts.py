from db import mongo

def send_alert(device_id, alert_message):
    # Alerting logic
    alert = {'device_id': device_id, 'message': alert_message, 'timestamp': time.time()}
    mongo.db.alerts.insert_one(alert)
    # Logic to send email
    print(f'Alert for device {device_id}: {alert_message}')
