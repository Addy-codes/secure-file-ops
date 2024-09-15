import os
from src.file import utils
from sib_api_v3_sdk import Configuration
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

ENCRYPTION_KEY = utils.generate_key(SECRET_KEY)

CONFIGURATION = Configuration()
CONFIGURATION.api_key['api-key'] = os.getenv("BREVO_API_KEY")
