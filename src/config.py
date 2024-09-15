import os
from cryptography.fernet import Fernet
from sib_api_v3_sdk import Configuration
from dotenv import load_dotenv

load_dotenv()

description = """
This project implements a **highly secure file-sharing system** utilizing **FastAPI** and **MongoDB** for two distinct user roles: Operations (Ops) Users and Client Users.

Existing users:

User1: Verified Client

{
  "email": "adeeb9839@gmail.com",
  "password": "ez-wroks9839",
  "role": "client"
}

User2: Ops

{
  "email": "adeeb.rimor@gmail.com",
  "password": "ez-wroks9839",
  "role": "ops"
}

Security highlights:
- **JWT Authentication**: Ensures secure API access with role-based restrictions.
- **Encrypted URLs**: Protects file downloads by generating secure, time-limited links.
- **File Upload Restrictions**: Ensures only trusted file formats are uploaded, enhancing data security.
"""

BASE_URL = os.getenv("BASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

ENCRYPTION_KEY = Fernet.generate_key() + SECRET_KEY.encode()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE = os.getenv("DATABASE")

CONFIGURATION = Configuration()
CONFIGURATION.api_key['api-key'] = os.getenv("BREVO_API_KEY")

PROJECT_TITLE = "Secure File OPS"
PROJECT_DESCRIPTION = description
PROJECT_VERSION = "0.0.1"

ALLOWED_FILE_TYPES = ['application/vnd.openxmlformats-officedocument.presentationml.presentation',  # pptx
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # docx
                      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']  # xlsx
MAX_FILE_SIZE = 3 * 1024 * 1024  # 3MB