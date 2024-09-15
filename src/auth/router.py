from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from src.auth.schemas import SignupRequest, LoginRequest, TokenResponse
from src.auth.service import create_user, create_access_token, change_to_verified, verification_email
from src.auth.dependencies import require_role
from src.database import users_collection
from passlib.context import CryptContext


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/signup", response_model=TokenResponse)
async def signup(signup_request: SignupRequest):
    """
    Create a new user account.

    Args:
        signup_request (SignupRequest): The user's signup information.

    Returns:
        TokenResponse: An access token for the newly created user.

    Raises:
        HTTPException: If the role is invalid.
    """

    if signup_request.role not in ["client", "ops"]:
        raise HTTPException(status_code=400, detail="Invalid role. Role must be either 'client' or 'ops'.")

    user = await create_user(signup_request)

    access_token = create_access_token({"sub": signup_request.email, "role": signup_request.role})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest):
    """
    Authenticate a user and provide an access token.

    Args:
        login_request (LoginRequest): The user's login credentials.

    Returns:
        TokenResponse: An access token for the authenticated user.

    Raises:
        HTTPException: If the credentials are invalid.
    """
    user = await users_collection.find_one({"email": login_request.email})
    if not user or not pwd_context.verify(login_request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": user["email"], "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/resend-verification-email")
async def resend_verification_email(user=Depends(require_role("client"))):
    """
    Resend the verification email to the user.

    Args:
        user: The authenticated user (injected by the require_role dependency).

    Returns:
        JSONResponse: A success message if the email is sent.

    Raises:
        HTTPException: If there's an error sending the verification email.
    """
    try:
        await verification_email(user)
        return JSONResponse(status_code=200, content={"message": "Verification Email Sent"})
    except Exception as e:
        raise HTTPException(status_code=501, detail=f"Unable to send verification mail: {e}")

@router.get("/verify-email")
async def verify_email(token: str):
    """
    Verify a user's email address using the provided token.

    Args:
        token (str): The verification token sent to the user's email.

    Returns:
        The result of the email verification process.
    """

    return await change_to_verified(token)
