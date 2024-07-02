import time
from mailjet_rest import Client
from db import mongo
from bson import ObjectId
from config import Config  # Ensure Config is imported correctly

def send_alert(device_id, alert_message):
    # Check if an alert with the same device_id and message already exists
    existing_alert = mongo.db.alerts.find_one({
        'device_id': device_id,
        'message': alert_message
    })

    if existing_alert:
        # If the alert exists and email has been sent, do not send again
        if existing_alert.get('email_sent', False):
            print(f"Alert for device {device_id}: {alert_message} already sent.")
            return
    
        # Otherwise, update the existing alert with the current timestamp
        mongo.db.alerts.update_one(
            {'_id': existing_alert['_id']},
            {'$set': {'timestamp': time.time(), 'email_sent': False}}
        )
        print(f"Updated existing alert for device {device_id}: {alert_message}")

    else:
        # Insert new alert
        alert = {
            'device_id': device_id,
            'message': alert_message,
            'timestamp': time.time(),
            'email_sent': False
        }
        mongo.db.alerts.insert_one(alert)
        print(f'New alert for device {device_id}: {alert_message}')

def send_email_alert(device_id, alert_message):
    try:
        mailjet = Client(auth=(Config.MAILJET_API_KEY, Config.MAILJET_API_SECRET), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "lauryn.waruingi@strathmore.edu",
                        "Name": "Alert System"
                    },
                    "To": [
                        {
                            "Email": Config.ALERT_EMAIL,
                            "Name": "Admin"
                        }
                    ],
                    "Subject": f'Alert for Device {device_id}',
                    "TextPart": f'Alert for Device {device_id}: {alert_message}',
                    "HTMLPart": f'<h3>Alert for Device {device_id}</h3><p>{alert_message}</p>'
                }
            ]
        }
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print(f'Email sent to {Config.ALERT_EMAIL} with status code {result.status_code}')
            # Update email_sent flag in the database
            mongo.db.alerts.update_one(
                {'device_id': device_id, 'message': alert_message},
                {'$set': {'email_sent': True}}
            )
        else:
            print(f'Error sending email: {result.json()}')
    except Exception as e:
        print(f'Exception occurred while sending email: {e}')

def check_and_send_alerts():
    unsent_alerts = mongo.db.alerts.find({'email_sent': False})

    for alert in unsent_alerts:
        send_email_alert(alert['device_id'], alert['message'])
        mongo.db.alerts.update_one(
            {'_id': alert['_id']},
            {'$set': {'email_sent': True}}
        )
        print(f'Email sent for alert: {alert["_id"]}')

def send_email_for_alert(alert_id):
    alert = mongo.db.alerts.find_one({'_id': ObjectId(alert_id)})
    if alert and not alert.get('email_sent'):
        send_email_alert(alert['device_id'], alert['message'])
        mongo.db.alerts.update_one(
            {'_id': alert['_id']},
            {'$set': {'email_sent': True}}
        )
        print(f'Email sent for alert: {alert["_id"]}')
        return True
    return False
