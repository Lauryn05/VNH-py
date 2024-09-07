import os

class Config:
    MONGO_URI = 'mongodb+srv'
    MAILJET_API_KEY = os.getenv("MAILJET_API_KEY", "key")
    MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET", "secret")
    ALERT_EMAIL = os.getenv("ALERT_EMAIL", "email")