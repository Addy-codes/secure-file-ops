from fastapi import APIRouter, File, UploadFile, Depends
from src.file.service import upload_file, generate_download_link, download_file
from src.auth.dependencies import require_role

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile = File(...), user=Depends(require_role("ops"))):
    return await upload_file(file, user)

@router.get("/download-link/{file_id}", dependencies=[Depends(require_role("client"))])
async def get_download_link(file_id: str):
    return await generate_download_link(file_id)

@router.get("/download/{encrypted_link}")
async def download(encrypted_link: str):
    return await download_file(encrypted_link)
