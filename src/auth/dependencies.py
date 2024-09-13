from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from src.config import SECRET_KEY, ALGORITHM
from src.database import users_collection

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # Extract the actual token string from the credentials
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=403, detail="Invalid token")
        
        user = await users_collection.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=403, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

def require_role(role: str):
    async def role_dependency(user: dict = Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_dependency
