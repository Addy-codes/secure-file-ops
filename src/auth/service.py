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
    """
    Create a new user in the database.

    Args:
        signup_request (SignupRequest): The user's signup information.

    Returns:
        dict: The ID of the newly created user.

    Raises:
        HTTPException: If the user already exists or the password is not strong enough.
    """
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
    """
    Verify a user's email address.

    Args:
        email (str): The user's email address.

    Returns:
        dict: A success message if the user is verified.

    Raises:
        HTTPException: If the user verification fails.
    """
    result = await users_collection.update_one(
        {"email": email},
        {"$set": {"is_verified": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to verify user")
    
    return {"message": "User verified successfully"}


def create_access_token(data: dict):
    """
    Create a JWT access token.

    Args:
        data (dict): The data to encode in the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verification_email(user):
    """
    Send a verification email to the user if not already verified.

    Args:
        user (dict): The user document.

    Returns:
        dict: A message indicating the email verification status.
    """
    if user["is_verified"]:
        return {"message": "Email already verified"}
    await send_verification_email(user['email'])


async def send_verification_email(user_email: str):
    """
    Send a verification email to the user.

    Args:
        user_email (str): The user's email address.

    Raises:
        HTTPException: If the email sending fails.
    """
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
    """
    Change the user's status to verified using the provided token.

    Args:
        token (str): The verification token.

    Returns:
        dict: A message indicating the email verification status.

    Raises:
        HTTPException: If the token is invalid, expired, or the user is not found.
    """
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
    """
    Validate the strength of the provided password.

    Args:
        password (str): The password to validate.

    Raises:
        HTTPException: If the password does not meet complexity requirements.
    """
    stats = PasswordStats(password)

    if stats.strength() < 0.5:
        raise HTTPException(
            status_code=400, 
            detail="Password does not meet complexity requirements."
        )