import time
import config
from mailjet_rest import Client
from db import mongo

def send_alert(device_id, alert_message):
    # Alerting logic
    alert = {'device_id': device_id, 'message': alert_message, 'timestamp': time.time()}
    mongo.db.alerts.insert_one(alert)
    # Logic to send email
    send_email_alert(device_id, alert_message)
    print(f'Alert for device {device_id}: {alert_message}')

def send_email_alert(device_id, alert_message):
    mailjet = Client(auth=(config.MAILJET_API_KEY, config.MAILJET_API_SECRET), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "lauryn.waruingi@strathmore.edu",
                    "Name": "Alert System"
                },
                "To": [
                    {
                        "Email": config.ALERT_EMAIL,
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
        print(f'Email sent to {config.ALERT_EMAIL} with status code {result.status_code}')
    else:
        print(f'Error sending email: {result.json()}')
