import os

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from src.main import app
from src.auth.service import create_access_token

# ============================ FIXTURES ============================

@pytest.fixture(scope="session")
def client():
    """Create a TestClient for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    """Set up and tear down the test database before and after each test."""
    mongo_client = MongoClient("mongodb://localhost:27017/test_db")
    mongo_client.drop_database("test_db")
    yield
    mongo_client.drop_database("test_db")

# ============================ HELPER FUNCTIONS ============================

def create_user(client, email, password, role="client"):
    """Helper function to create a user."""
    response = client.post("/auth/signup", json={
        "email": email,
        "password": password,
        "role": role
    })
    assert response.status_code == 200
    return response.json()


def login_user(client, email, password):
    """Helper function to log in a user and return the token."""
    response = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    return response.json()["access_token"]


def verify_user(client, email):
    """Helper function to verify a user's email."""
    verification_token = create_access_token({"email": email})
    response = client.get(f"/auth/verify-email?token={verification_token}")
    assert response.status_code == 200

# ============================ TEST CASES ============================

def test_file_upload_ops_user(client):
    """Test Ops user file upload functionality."""
    create_user(client, "opsuser1@example.com", "OpsPassword123!", role="ops")
    token = login_user(client, "opsuser1@example.com", "OpsPassword123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a dummy file for testing
    with open("testfile.xlsx", "wb") as f:
        f.write(b"Dummy content")

    with open("testfile.xlsx", "rb") as file:
        response = client.post("/files/upload", files={"file": file}, headers=headers)

    os.remove("testfile.xlsx")  # Clean up the test file
    assert response.status_code == 201


def test_file_upload_client_user_restricted(client):
    """Test that client users are restricted from uploading files."""
    create_user(client, "clientuser2@example.com", "ClientPassword123!")
    verify_user(client, "clientuser2@example.com")
    token = login_user(client, "clientuser2@example.com", "ClientPassword123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a dummy file for testing
    with open("testfile.docx", "wb") as f:
        f.write(b"Dummy content")

    with open("testfile.docx", "rb") as file:
        response = client.post("/files/upload", files={"file": file}, headers=headers)

    os.remove("testfile.docx")  # Clean up the test file
    assert response.status_code == 403  # Client users are forbidden from uploading files


def test_file_download_link(client):
    """Test uploading a file by an Ops user and retrieving the download link for that file by a Client user."""
    # Step 1: Create and login Ops user
    create_user(client, "opsuser2@example.com", "OpsPassword123!", role="ops")
    ops_token = login_user(client, "opsuser2@example.com", "OpsPassword123!")
    ops_headers = {"Authorization": f"Bearer {ops_token}"}

    # Step 2: Create and login Client user
    create_user(client, "clientuser@example.com", "ClientPassword123!")
    verify_user(client, "clientuser@example.com")
    client_token = login_user(client, "clientuser@example.com", "ClientPassword123!")
    client_headers = {"Authorization": f"Bearer {client_token}"}

    # Step 3: Ops User uploads a file
    with open("testfile.txt", "wb") as f:
        f.write(b"Dummy file content")

    with open("testfile.txt", "rb") as file:
        upload_response = client.post("/files/upload", files={"file": file}, headers=ops_headers)

    os.remove("testfile.txt")  # Clean up the test file
    assert upload_response.status_code == 201

    file_id = upload_response.json()["file_id"]

    # Step 4: Client User requests the download link
    response = client.get(f"/files/download-link/{file_id}", headers=client_headers)
    assert response.status_code == 200
    assert "download_link" in response.json()
    assert response.json()["message"] == "success"

    download_link = response.json()["download_link"]
    assert download_link.startswith("http://") or download_link.startswith("https://")

    # Step 5: Client User uses the download link to download the file
    response = client.get(download_link, headers=client_headers)
    assert response.status_code == 200
    assert response.content == b"Dummy file content"


def test_file_download(client):
    """Test uploading a file, generating an encrypted link, and downloading the file."""
    create_user(client, "clientuser4@example.com", "ClientPassword123!")
    verify_user(client, "clientuser4@example.com")
    token = login_user(client, "clientuser4@example.com", "ClientPassword123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Ops user creates and uploads the file
    create_user(client, "opsuser3@example.com", "OpsPassword123!", role="ops")
    ops_token = login_user(client, "opsuser3@example.com", "OpsPassword123!")
    ops_headers = {"Authorization": f"Bearer {ops_token}"}

    with open("testfile.txt", "wb") as f:
        f.write(b"Dummy file content")

    with open("testfile.txt", "rb") as file:
        response = client.post("/files/upload", files={"file": file}, headers=ops_headers)

    os.remove("testfile.txt")  # Clean up the test file
    assert response.status_code == 201

    file_id = response.json()["file_id"]

    # Generate encrypted download link
    response = client.get(f"/files/download-link/{file_id}", headers=headers)
    assert response.status_code == 200
    encrypted_link = response.json()["download_link"]

    # Use encrypted link to download the file
    response = client.get(encrypted_link, headers=headers)
    assert response.status_code == 200
    assert response.content == b"Dummy file content"


def test_list_files(client):
    """Test listing available files for a client user."""
    create_user(client, "clientuser1@example.com", "ClientPassword123!")
    verify_user(client, "clientuser1@example.com")
    token = login_user(client, "clientuser1@example.com", "ClientPassword123!")
    headers = {"Authorization": f"Bearer {token}"}

    # Request the list of files
    response = client.get("/files/", headers=headers)
    assert response.status_code == 200
