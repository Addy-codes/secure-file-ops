from motor.motor_asyncio import AsyncIOMotorClient
from src.config import MONGO_URI, DATABASE

client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database(DATABASE)

users_collection = db.get_collection("users")
files_collection = db.get_collection("files")
