from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: Literal["client", "ops"] = Field(..., description="Role must be either 'client' or 'ops'")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
