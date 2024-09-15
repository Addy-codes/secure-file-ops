from src.database import files_collection, users_collection
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime
from bson import ObjectId
from src.file import utils
from src.config import ENCRYPTION_KEY, BASE_URL
import requests
import io

async def upload_file(file: UploadFile, user):
    """
    Upload a file to an external service and store its metadata in the database.

    Args:
        file (UploadFile): The file to be uploaded.
        user: The authenticated user uploading the file.

    Returns:
        JSONResponse: A response containing the file ID and file name.

    Raises:
        HTTPException: If there is an error during the file upload process.
    """
    try:
        file_data = await file.read()

        response = requests.post(
            'https://file.io', 
            files={'file': file_data}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to upload file to file.io")

        response_data = response.json()

        file_id = ObjectId()
        encrypted_url = utils.encrypt_data(ENCRYPTION_KEY, str(file_id))

        file_metadata = {
            "_id": file_id,
            "file_name": file.filename,
            "file_type": file.content_type,
            "uploaded_by": user["_id"],
            "upload_time": datetime.utcnow(),
            "file_url": encrypted_url.decode(),
            "external_url": response_data['link'],
            "is_active": True,
        }

        await files_collection.insert_one(file_metadata)

        return JSONResponse(status_code=201, content={"file_id": str(file_id), "file_name": file.filename})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")

async def generate_download_link(file_id: str):
    """
    Generate a download link for a file.

    Args:
        file_id (str): The ID of the file.

    Returns:
        JSONResponse: A response containing the download link.

    Raises:
        HTTPException: If there is an error during the link generation process.
    """
    try:
        encrypted_link = utils.encrypt_data(ENCRYPTION_KEY, file_id)
        return JSONResponse(status_code=200, content={"download_link": f"{BASE_URL}/files/download/{encrypted_link.decode()}", "message": "success"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating download link: {e}")

async def download_file(encrypted_link: str):
    """
    Download a file using an encrypted link.

    Args:
        encrypted_link (str): The encrypted link for the file.

    Returns:
        StreamingResponse: A streaming response containing the file data.

    Raises:
        HTTPException: If there is an error during the file download process.
    """
    try:
        file_id = utils.decrypt_data(ENCRYPTION_KEY, encrypted_link)

        file_data = await files_collection.find_one({"_id": ObjectId(file_id)})

        if not file_data or not file_data['is_active']:
            raise HTTPException(status_code=404, detail="File not found or inactive")

        external_url = file_data['external_url']
        response = requests.get(external_url, stream=True)

        if response.status_code == 200:
            file_stream = io.BytesIO(response.content)

            return StreamingResponse(
                file_stream,
                media_type=file_data["file_type"],
                headers={
                    "Content-Disposition": f"attachment; filename={file_data['file_name']}"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to download file from external service")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching file: {e}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid link or decryption failed: {e}")

async def list_files_with_creators():
    """
    List all active files with their creators.

    Returns:
        JSONResponse: A response containing a list of files and their creators.

    Raises:
        HTTPException: If there is an error during the file retrieval process.
    """
    try:
        files = await files_collection.find({"is_active": True}).to_list(length=None)
        
        if not files:
            return JSONResponse(status_code=404, content="No files found")

        file_list = []
        for file in files:
            user = await users_collection.find_one({"_id": ObjectId(file['uploaded_by'])}, {"_id": 1, "email": 1})
            
            if user:
                file_list.append({
                    "file_id": str(file["_id"]),
                    "file_name": file["file_name"],
                    "file_type": file["file_type"],
                    "upload_time": str(file["upload_time"]),
                    "uploaded_by": {
                        "user_id": str(user["_id"]),
                        "email": user["email"]
                    },
                })
        
        return JSONResponse(status_code=200, content={"files": file_list})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving files: {e}")