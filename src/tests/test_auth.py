import pytest
from fastapi.testclient import TestClient
from src.main import app
from pymongo import MongoClient
from datetime import datetime, timedelta
from jose import jwt
from src.config import SECRET_KEY, BASE_URL
from src.auth.service import create_access_token

@pytest.fixture(scope="session")
def client():
    """Create a TestClient for the FastAPI app."""
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    """Set up and tear down the test database."""
    client = MongoClient("mongodb://localhost:27017/test_db")
    # Drop all collections before test
    client.drop_database("test_db")
    yield
    # Drop all collections after test
    client.drop_database("test_db")


def test_signup_success(client):
    """Test successful user signup."""
    response = client.post("/auth/signup", json={
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "role": "client"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_signup_existing_user(client):
    """Test signup with an existing email."""
    client.post("/auth/signup", json={
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "role": "client"
    })
    response = client.post("/auth/signup", json={
        "email": "testuser@example.com",
        "password": "AnotherPassword456!",
        "role": "client"
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "User with this email already exists. Kindly login."

def test_login_success(client):
    """Test successful user login."""
    client.post("/auth/signup", json={
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "role": "client"
    })
    # Assume email verification is automatic for testing purposes
    response = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "TestPassword123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_credentials(client):
    """Test login with incorrect credentials."""
    client.post("/auth/signup", json={
        "email": "testuser@example.com",
        "password": "CorrectPassword123!",
        "role": "client"
    })
    response = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"

def test_resend_verification_email(client):
    """Test resending the verification email."""
    client.post("/auth/signup", json={
        "email": "resend@example.com",
        "password": "TestPassword123!",
        "role": "client"
    })
    # Login to get the token
    login_response = client.post("/auth/login", json={
        "email": "resend@example.com",
        "password": "TestPassword123!"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/resend-verification-email", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Verification Email Sent"}

def test_verify_email_success(client):
    """Test successful email verification."""
    client.post("/auth/signup", json={
        "email": "verify@example.com",
        "password": "TestPassword123!",
        "role": "client"
    })
    verification_token = create_access_token({"email": "verify@example.com"})
    response = client.get(f"{BASE_URL}/auth/verify-email?token={verification_token}")
    assert response.status_code == 200
    assert response.json() == {"message": "Email verified successfully"}

def test_verify_email_invalid_token(client):
    """Test email verification with an invalid token."""
    response = client.get("/auth/verify-email?token=invalidtoken")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid token"

def test_verify_email_expired_token(client):
    """Test email verification with an expired token."""
    expired_token = jwt.encode(
        {"sub": "expired@example.com", "exp": datetime.utcnow() - timedelta(hours=1)},
        SECRET_KEY,
        algorithm="HS256"
    )
    response = client.get(f"/auth/verify-email?token={expired_token}")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Verification token has expired"

def test_signup_invalid_role(client):
    """Test signup with an invalid role."""
    response = client.post("/auth/signup", json={
        "email": "invalidrole@example.com",
        "password": "TestPassword123!",
        "role": "invalid_role"
    })
    assert response.status_code == 422

def test_signup_weak_password(client):
    """Test signup with a weak password."""
    response = client.post("/auth/signup", json={
        "email": "weakpassword@example.com",
        "password": "123",
        "role": "client"
    })
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Password does not meet complexity requirements."

def test_login_nonexistent_user(client):
    """Test login with a nonexistent user."""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "AnyPassword123!"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"
