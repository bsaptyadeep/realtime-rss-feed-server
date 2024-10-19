from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
import os

# Database connection details (store these in environment variables for security)
DATABASE_URI = os.getenv("MONGO_DB_URI")
DATABASE_NAME = "realtime_rss_feed"
RSS_FEED_COLLECTION_NAME = "RSS_FEED"

# Connect to MongoDB
client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
rss_feed_collection=db[RSS_FEED_COLLECTION_NAME]

# Function to get the database collection (optional, for reusability)
def get_rss_feed_collection():
    return rss_feed_collection