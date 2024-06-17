from flask import Flask, jsonify, request, render_template
from db import mongo
from snmp_manager import discover_devices, configure_device, fetch_device_data
from alerts import send_alert
from analyze import analyze_data
from config import Config
import logging

app = Flask(__name__)
app.config['MONGO_URI'] = Config.MONGO_URI
mongo.init_app(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/devices')
def devices():
    try:
        devices = list(mongo.db.devices.find())
        return render_template('devices.html', devices=devices)
    except Exception as e:
        logging.error(f"Error fetching devices: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/device/<device_id>')
def device_details(device_id):
    try:
        device = mongo.db.devices.find_one({'_id': device_id})
        return render_template('device_details.html', device=device)
    except Exception as e:
        logging.error(f"Error fetching device details for {device_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/alerts')
def alerts():
    try:
        alerts = list(mongo.db.alerts.find())
        return render_template('alerts.html', alerts=alerts)
    except Exception as e:
        logging.error(f"Error fetching alerts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/discover_devices', methods=['GET'])
def discover():
    result = discover_devices()
    return jsonify(result), 200

@app.route('/configure_device/<device_id>', methods=['POST'])
def configure(device_id):
    data = request.json
    result = configure_device(device_id, data)
    return jsonify(result), 200

@app.route('/device_data/<device_id>', methods=['GET'])
def device_data(device_id):
    data = fetch_device_data(device_id)
    analyze_data(data)
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(debug=True)
