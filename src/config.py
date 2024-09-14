import os
from src.file import utils
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

ENCRYPTION_KEY = utils.generate_key(SECRET_KEY)
