from fastapi import HTTPException, status
from src.database import users_collection
from src.auth.schemas import SignupRequest
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(signup_request: SignupRequest):
    existing_user = await users_collection.find_one({"email": signup_request.email})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists. Kindly login."
        )

    hashed_password = pwd_context.hash(signup_request.password)
    
    user_data = {
        "username": signup_request.email.split("@")[0],
        "email": signup_request.email,
        "password": hashed_password,
        "role": signup_request.role,
        "is_verified": False,
        "created_at": datetime.utcnow()
    }

    result = await users_collection.insert_one(user_data)
    
    return {"id": str(result.inserted_id)}

async def verify_user(email: str):
    await users_collection.update_one({"email": email}, {"$set": {"is_verified": True}})
    return {"message": "User verified successfully"}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
