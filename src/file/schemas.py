from pydantic import BaseModel

class FileUploadResponse(BaseModel):
    file_id: str
    file_name: str

class FileDownloadResponse(BaseModel):
    download_link: str
