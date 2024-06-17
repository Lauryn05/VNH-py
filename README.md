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
 - snmp_agent.py: SNMP agent implementation.
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