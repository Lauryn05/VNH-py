from flask import Flask, jsonify, request, render_template  # Necessary Flask modules
from db import mongo, init_db  # MongoDB connection and initialization function
from snmp_manager import discover_devices, configure_device, receive_metrics  # Impoet SNMP manager functions
from alerts import send_alert, check_and_send_alerts, send_email_for_alert  # Import alerting functions
from analyze import analyze_data  # data analysis function
from config import Config  # configuration detaild
import logging  # logging for error handling
from bson import ObjectId  # BSON ObjectId for MongoDB queries
import time  # time handling
import threading  # threading for background tasks

app = Flask(__name__)  # Create Flask application instance
app.config.from_object(Config)  # Configure Flask app using Config settings

# Initialize MongoDB connection
init_db(app)
logging.info("MongoDB connection initialized")  # Log MongoDB connection initialization

logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG

@app.route('/')
def home():
    try:
        # Fetch performance metrics for all devices, sorted by timestamp descending
        performance_metrics = list(mongo.db.performance_metrics.find().sort("timestamp", -1))
        
        # Create a dictionary to store latest metrics for each device
        latest_metrics = {}

        # Iterate through all metrics and update latest_metrics for each device
        for metric in performance_metrics:
            device_id = str(metric['device_id'])  # Convert ObjectId to string
            if device_id not in latest_metrics:
                latest_metrics[device_id] = {
                    'device_id': device_id,
                    'cpu_usage': metric.get('cpu_usage', 'N/A'),
                    'memory_usage': metric.get('memory_usage', 'N/A'),
                    'disk_usage': metric.get('disk_usage', 'N/A'),
                    'timestamp': metric['timestamp']
                }
        
        # Convert dictionary values to list for template rendering
        latest_metrics_list = list(latest_metrics.values())

        return render_template('dashboard.html', metrics=latest_metrics_list)  # Render dashboard.html template with latest metrics
    
    except Exception as e:
        logging.error(f"Error fetching or processing performance metrics: {e}")  # Log error if fetching or processing metrics fails
        return jsonify({"error": str(e)}), 500  # Return JSON response with error message and status code 500 for internal server error

@app.route('/devices')
def devices():
    try:
        devices = list(mongo.db.devices.find())  # Fetch all devices from MongoDB
        return render_template('devices.html', devices=devices)  # Render devices.html template with list of devices
    
    except Exception as e:
        logging.error(f"Error fetching devices: {e}")  # Log error if fetching devices fails
        return jsonify({"error": str(e)}), 500  # Return JSON response with error message and status code 500

@app.route('/device/<device_id>')
def device_details(device_id):
    try:
        device = mongo.db.devices.find_one({'_id': ObjectId(device_id)})  # Find device by ObjectId
        if device is None:
            logging.error(f"Device with ID {device_id} not found")  # Log error if device not found
            return jsonify({"error": "Device not found"}), 404  # Return JSON response with error message and status code 404
        
        return render_template('device_details.html', device=device)  # Render device_details.html template with device details
    
    except Exception as e:
        logging.error(f"Error fetching device details for {device_id}: {e}")  # Log error if fetching device details fails
        return jsonify({"error": str(e)}), 500  # Return JSON response with error message and status code 500

@app.route('/alerts')
def alerts():
    try:
        alerts = list(mongo.db.alerts.find())  # Fetch all alerts from MongoDB
        return render_template('alerts.html', alerts=alerts)  # Render alerts.html template with list of alerts
    
    except Exception as e:
        logging.error(f"Error fetching alerts: {e}")  # Log error if fetching alerts fails
        return jsonify({"error": str(e)}), 500  # Return JSON response with error message and status code 500

@app.route('/send_email/<alert_id>', methods=['POST'])
def send_email(alert_id):
    try:
        success = send_email_for_alert(alert_id)  # Call send_email_for_alert function with alert_id
        if success:
            return jsonify({"message": "Email sent successfully"}), 200  # Return JSON response for successful email send
        
        else:
            return jsonify({"message": "Email already sent or alert not found"}), 404  # Return JSON response for email already sent or alert not found
    
    except Exception as e:
        logging.error(f"Error sending email for alert {alert_id}: {e}")  # Log error if sending email fails
        return jsonify({"message": str(e)}), 500  # Return JSON response with error message and status code 500

@app.route('/discover_devices', methods=['GET'])
def discover():
    result = discover_devices()  # Call discover_devices function
    return jsonify(result), 200  # Return JSON response with discovery result and status code 200

@app.route('/configure_device/<device_id>', methods=['POST'])
def configure(device_id):
    try:
        data = request.get_json()  # Get JSON data from request body
        if not data or 'hostname' not in data or 'ip_address' not in data or 'oid' not in data:
            logging.error("Invalid data received")  # Log error if invalid data received
            return jsonify({"error": "Invalid data"}), 400  # Return JSON response with error message and status code 400
        
        result = configure_device(device_id, data)  # Call configure_device function with device_id and data
        return jsonify(result), 200  # Return JSON response with configuration result and status code 200
    
    except Exception as e:
        logging.error(f"Error configuring device {device_id}: {e}")  # Log error if configuring device fails
        return jsonify({"error": str(e)}), 500  # Return JSON response with error message and status code 500

@app.route('/device_data/<device_id>', methods=['GET'])
def device_data(device_id):
    try:
        performance_metrics = list(mongo.db.performance_metrics.find({'device_id': ObjectId(device_id)}).sort("timestamp", -1))  # Fetch performance metrics for device
        if not performance_metrics:
            logging.error(f"No data found for device ID {device_id}")  # Log error if no data found for device
            return jsonify({"error": "No data found for the device"}), 404  # Return JSON response with error message and status code 404
        
        analyzed_data = analyze_data(performance_metrics)  # Analyze fetched performance metrics
        return jsonify(analyzed_data), 200  # Return JSON response with analyzed data and status code 200
    
    except Exception as e:
        logging.error(f"Error fetching data for device {device_id}: {e}")  # Log error if fetching data fails
        return jsonify({"error": str(e)}), 500  # Return JSON response with error message and status code 500

def periodic_alert_check():
    while True:
        check_and_send_alerts()  # Call function to check and send alerts
        time.sleep(60)  # Sleep for 60 seconds before checking again

if __name__ == '__main__':
    threading.Thread(target=periodic_alert_check).start()  # Start a new thread for periodic_alert_check function
    analyze_data()  # Trigger analyze_data function when app.py is launched
    app.run(debug=True)  # Run the Flask application in debug mode
