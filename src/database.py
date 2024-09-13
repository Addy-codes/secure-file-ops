from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI")
DATABASE = os.getenv("DATABASE")

client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database(DATABASE)

users_collection = db.get_collection("users")
files_collection = db.get_collection("files")
