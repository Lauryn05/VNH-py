from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    try:
        mongo.init_app(app)
        print("MongoDB connection initialized")
    except Exception as e:
        print(f"Error initializing MongoDB connection: {e}")
        raise
