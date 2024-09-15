from fastapi import HTTPException, status
from src.database import users_collection
from src.auth.schemas import SignupRequest
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, CONFIGURATION, BASE_URL
from sib_api_v3_sdk import ApiClient
from sib_api_v3_sdk.api.transactional_emails_api import TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail
from password_strength import PasswordStats

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(signup_request: SignupRequest):

    validate_password_strength(signup_request.password)

    existing_user = await users_collection.find_one({"email": signup_request.email})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists. Kindly login."
        )

    hashed_password = pwd_context.hash(signup_request.password)
    
    user_data = {
        "email": signup_request.email,
        "password": hashed_password,
        "role": signup_request.role,
        "is_verified": False,
        "created_at": datetime.utcnow()
    }

    result = await users_collection.insert_one(user_data)
    
    if signup_request.role == 'client':
        await send_verification_email(signup_request.email)
    
    return {"id": str(result.inserted_id)}


async def verify_user(email: str):
    result = await users_collection.update_one(
        {"email": email},
        {"$set": {"is_verified": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to verify user")
    
    return {"message": "User verified successfully"}


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verification_email(user):
    if user["is_verified"]:
        return {"message": "Email already verified"}
    await send_verification_email(user['email'])


async def send_verification_email(user_email: str):
    token = create_access_token({"email": user_email})

    verification_url = f"{BASE_URL}/auth/verify-email?token={token}"

    api_instance = TransactionalEmailsApi(ApiClient(CONFIGURATION))
    
    send_smtp_email = SendSmtpEmail(
        to=[{"email": user_email}],
        sender={"email": "adeeb.rimor@gmail.com", "name": "Secure File Ops"},
        subject="Verify your email address",
        html_content=f"<p>Please verify your email by clicking <a href='{verification_url}'>here</a>.</p>"
    )
    
    try:
        api_instance.send_transac_email(send_smtp_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")


async def change_to_verified(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("email")
        
        if not user_email:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = await users_collection.find_one({"email": user_email})
        
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        if user["is_verified"]:
            return {"message": "Email already verified"}
        
        await verify_user(user_email)
        
        return {"message": "Email verified successfully"}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Verification token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

def validate_password_strength(password: str):
    stats = PasswordStats(password)

    if stats.strength() < 0.5:
        raise HTTPException(
            status_code=400, 
            detail="Password does not meet complexity requirements."
        )