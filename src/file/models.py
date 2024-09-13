from bson import ObjectId
from pydantic import BaseModel
from datetime import datetime

class FileModel(BaseModel):
    id: ObjectId
    file_name: str
    file_type: str
    uploaded_by: ObjectId
    upload_time: datetime
    file_url: str
    is_active: bool
