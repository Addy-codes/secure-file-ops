from cryptography.fernet import Fernet
from src.config import MAX_FILE_SIZE, ALLOWED_FILE_TYPES
from fastapi import HTTPException
from starlette.datastructures import UploadFile

def encrypt_data(key, data):
    """
    Encrypt data using the provided encryption key.

    Args:
        key (bytes): The encryption key.
        data (str): The data to be encrypted.

    Returns:
        bytes: The encrypted data.
    """
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

def decrypt_data(key, encrypted_data):
    """
    Decrypt data using the provided encryption key.

    Args:
        key (bytes): The encryption key.
        encrypted_data (bytes): The data to be decrypted.

    Returns:
        str: The decrypted data.
    """
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

async def verify_file(file: UploadFile):
    """
    Verify if the uploaded file meets the required conditions:
    - File must be .pptx, .docx, or .xlsx.
    - File must not be larger than 3MB.
    
    Args:
        file (UploadFile): The file to be verified.
    
    Raises:
        HTTPException: If the file is invalid or does not meet the criteria.
    """

    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only .pptx, .docx, and .xlsx files are allowed."
        )

    file_size = 0
    contents = await file.read()  # Read the contents of the file
    file_size = len(contents)  # Get the size of the file
    await file.seek(0)  # Reset the file pointer after reading the file

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds 3MB. Uploaded file size: {file_size / (1024 * 1024):.2f} MB"
        )