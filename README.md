# VELOCITYNETHUB: AN SNMP BASED OPEN SOURCE NETWORK MANAGEMENT TOOL FOR SMEs
This project is a Python-based Network Management Tool that provides SNMP device discovery, monitoring, and management functionalities. It uses PySNMP for SNMP operations, PyMongo for MongoDB interactions, and Flask for the web interface.

## Table of Contents
   - Features
   - Project Sructure
   - Installation
   - Usage
   - Configuration
   - Customizable MIB files
   - Troubleshooting

## Features
 - SNMP device discovery and monitoring
 - MIB integration
 - MongoDB for storage
 - Web interface for managing devices and viewing alerts
 - Device status analysis and alert system (sends emails using mailjet API)

## Project Structyre
    VNH/
    ├── app.py
    ├── alerts.py
    ├── analyze.py
    ├── config.py
    ├── db.py
    ├── snmp_manager.py
    ├── manage.py
    ├── templates/
    │   ├── dashboard.html
    │   ├── devices.html
    │   ├── device_details.html
    │   └── alerts.html
    ├── mibs/
    │   ├── DEMO-MIB.mib
    │   └── DEMO-MIB.py
    ├── requirements.txt
    └── README.md
 - app.py: Entry point for the Flask application.
 - alerts.py: Script for managing and sending alerts.
 - analyze.py: Script for analyzing device data and generating insights.
 - config.py: Configuration file for the application.
 - db.py: MongoDB interactions and operations
 - snmp_manager.py: SNMP management and device discovery functions.
 - snmp_agent_x.py: SNMP agent implementation (Linux or Windows).
 - manage.py: Script for managing the application (eg., database migrations)
 - templates/: Directory containing HTML templates for the web interface.
    dashboard.html: Dashboard view.
    devices.html: Device list view.
    device_details.html: Device details view.
    alerts.html: Alerts view.
 - mibs/: Directory containing MIB files.
    DEMO-MIB.mib: Custom MIB definition.
    DEMO-MIB.py: Python translation of the custom MIB.
 - requirements.txt: List of Python dependencies.
 - README.md: Project documentation.

## Installation
 - Clone this repository into your local device
     -git clone http://github.com/Lauryn05/VNH-py
 - This tool requires MongoDB Atlas for data storage so ensure you have an acount with Mongo DB and have a database for network management.
 - Change the information in config.py.
 - Create an account in MailjetAPI and change the data in config.py and alerts.py.

## Usage
 - Once the repository containing all the files in VelocityNetHub is cloned, the network administrator copies the SNMP agent file (linux or windows) to the monitored devices.
 - The SNMP manager is then run on the administrator’s device which uses packet sniffing concept and flask to listen on a specific IP address.
 - Change the IP address on the SNMP agent to the IP address the manager is listening on the run it on the managed devices.
 - The SNMP agent sends the device’s performance metrics and system information to the manager which then stores it in the Database.
 - This process can be automated by setting up cron jobs at the managed devices to make sure the agent is run periodically to ensure up to date device information.
 - When the flask app is run, it retrieves data from the database and displays the latest performance metrics of the managed devices on the dashboard.
 - Running the flask app also triggers the analysis module which checks if set thresholds have been surpassed then sends alerts to the network administrator though email using Mailjet API.
 - The devices are then displayed in the devices page of the dashboard and when one selects a specific device, they can be able to view more device details and configure its hostname and IP address.
 - The network administrator can also be able to view the alerts sent on the alerts page of the dashboard.
