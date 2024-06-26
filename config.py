import os

class Config:
    MONGO_URI = 'mongodb+srv://lauryn:2004@vnh.yitygnq.mongodb.net/VNH?retryWrites=true&w=majority'
    MAILJET_API_KEY = os.getenv("MAILJET_API_KEY", "f24b20762a3b2c6d868ff72bb8ab3927")
    MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET", "1d274eac3bba15316bfb267766c21162")
    ALERT_EMAIL = os.getenv("ALERT_EMAIL", "lauryn.waruingi@strathmore.edu")