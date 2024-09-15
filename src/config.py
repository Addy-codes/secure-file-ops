import os
from src.file import utils
from sib_api_v3_sdk import Configuration
from dotenv import load_dotenv

load_dotenv()

description = """
This project implements a **highly secure file-sharing system** utilizing **FastAPI** and **MongoDB** for two distinct user roles: Operations (Ops) Users and Client Users.

Key functionalities:
- **Ops User**:
  - Upload files restricted to `.pptx`, `.docx`, and `.xlsx` formats.
  - Only authorized Ops Users are allowed to perform uploads.
- **Client User**:
  - Register with secure email verification flow.
  - Access and download files via encrypted URLs.
  - View a list of available files, ensuring controlled and secure access.

Security highlights:
- **JWT Authentication**: Ensures secure API access with role-based restrictions.
- **Encrypted URLs**: Protects file downloads by generating secure, time-limited links.
- **File Upload Restrictions**: Ensures only trusted file formats are uploaded, enhancing data security.
"""

BASE_URL = os.getenv("BASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

ENCRYPTION_KEY = utils.generate_key(SECRET_KEY)

CONFIGURATION = Configuration()
CONFIGURATION.api_key['api-key'] = os.getenv("BREVO_API_KEY")

PROJECT_TITLE = "Secure File OPS"
PROJECT_DESCRIPTION = description
PROJECT_VERSION = "0.0.1"