from src.database import files_collection
from fastapi import UploadFile
from cryptography.fernet import Fernet
from datetime import datetime
from bson import ObjectId
import os

ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

async def upload_file(file: UploadFile, user):
    upload_dir = "uploaded_files"

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    file_id = ObjectId()
    encrypted_url = cipher.encrypt(str(file_id).encode()).decode()

    file_data = {
        "_id": file_id,
        "file_name": file.filename,
        "file_type": file.content_type,
        "uploaded_by": user["_id"],
        "upload_time": datetime.utcnow(),
        "file_url": encrypted_url,
        "is_active": True,
        "file_path": file_path
    }

    await files_collection.insert_one(file_data)
    return {"file_id": str(file_id), "file_name": file.filename}

async def generate_download_link(file_id: str):
    encrypted_link = cipher.encrypt(file_id.encode()).decode()
    return {"download_link": f"/files/download/{encrypted_link}"}

async def download_file(encrypted_link: str, user):
    try:
        file_id = cipher.decrypt(encrypted_link.encode()).decode()
        file_data = await files_collection.find_one({"_id": ObjectId(file_id), "is_active": True})
        if file_data:
            return {"file_name": file_data["file_name"]}
    except:
        return {"error": "Invalid link"}
