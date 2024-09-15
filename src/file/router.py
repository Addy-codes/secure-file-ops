from fastapi import APIRouter, File, UploadFile, Depends
from src.file.service import upload_file, generate_download_link, download_file, list_files_with_creators
from src.auth.dependencies import require_role, is_verified_client

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile = File(...), user=Depends(require_role("ops"))):
    """
    Upload a file to the server.

    Args:
        file (UploadFile): The file to be uploaded.
        user: The authenticated user (injected by the require_role dependency).

    Returns:
        The result of the file upload process.
    """
    return await upload_file(file, user)

@router.get("/download-link/{file_id}", dependencies=[Depends(require_role("client")), Depends(is_verified_client)])
async def get_download_link(file_id: str):
    """
    Generate a download link for a file.

    Args:
        file_id (str): The ID of the file.

    Returns:
        The generated download link for the file.
    """
    return await generate_download_link(file_id)

@router.get("/download/{encrypted_link}")
async def download(encrypted_link: str):
    """
    Download a file using an encrypted link.

    Args:
        encrypted_link (str): The encrypted link for the file.

    Returns:
        The result of the file download process.
    """
    return await download_file(encrypted_link)

@router.get("/", dependencies=[Depends(require_role("client")), Depends(is_verified_client)])
async def list_files():
    """
    List all files with their creators.

    Returns:
        A list of files with their creators.
    """
    return await list_files_with_creators()