import os

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://atlas-sql-6660eeffd618ae1ad10794bb-bmdn7.a.query.mongodb.net/VNH?ssl=true&authSource=admin")
