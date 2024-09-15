from bson import ObjectId
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserModel(BaseModel):
    id: Optional[ObjectId]
    email: EmailStr
    password: str
    role: str
    is_verified: bool
    created_at: datetime
