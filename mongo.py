from mongoengine import Document, StringField, DateTimeField, FloatField, IntField, ObjectIdField
import datetime

class Device(Document):
    device_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    ip_address = StringField(required=True)
    type = StringField(required=True)
    location = StringField()
    status = StringField(required=True, choices=('Active', 'Inactive'))
    last_updated = DateTimeField(default=datetime.datetime.utcnow)

class Configuration(Document):
    device_id = StringField(required=True)
    configuration = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)

class TrafficLog(Document):
    device_id = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    traffic_in = FloatField(required=True)
    traffic_out = FloatField(required=True)
    protocol = StringField(required=True)
    src_ip = StringField(required=True)
    dst_ip = StringField(required=True)
    src_port = IntField(required=True)
    dst_port = IntField(required=True)

class PerformanceMetric(Document):
    device_id = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    cpu_usage = FloatField(required=True)
    memory_usage = FloatField(required=True)
    disk_usage = FloatField(required=True)

class Alert(Document):
    device_id = StringField(required=True)
    alert_type = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    status = StringField(required=True, choices=('Active', 'Resolved'))
    resolved_at = DateTimeField()

class User(Document):
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    email = StringField(required=True)
    role = StringField(required=True, choices=('Admin', 'User'))
    last_login = DateTimeField()
