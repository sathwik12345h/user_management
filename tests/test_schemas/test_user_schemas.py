import uuid
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest
from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app is defined in 'main.py'

# Fixtures for common test data
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def user_base_data():
    return {
        "nickname": "john_doe_123",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "AUTHENTICATED",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg",
        "linkedin_profile_url": "https://linkedin.com/in/johndoe",
        "github_profile_url": "https://github.com/johndoe"
    }

@pytest.fixture
def user_create_data(user_base_data):
    return {**user_base_data, "password": "SecurePassword123!"}

@pytest.fixture
def user_update_data():
    return {
        "email": "john.doe.new@example.com",
        "nickname": "j_doe",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I specialize in backend development with Python and Node.js.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe_updated.jpg"
    }

@pytest.fixture
def user_response_data(user_base_data):
    return {
        "id": uuid.uuid4(),
        "nickname": user_base_data["nickname"],
        "first_name": user_base_data["first_name"],
        "last_name": user_base_data["last_name"],
        "role": user_base_data["role"],
        "email": user_base_data["email"],
        "links": []
    }

@pytest.fixture
def login_request_data():
    return {"email": "john_doe_123@example.com", "password": "SecurePassword123!"}

# Tests for UserBase
def test_user_base_valid(user_base_data):
    user = UserBase(**user_base_data)
    assert user.nickname == user_base_data["nickname"]
    assert user.email == user_base_data["email"]

# Tests for UserCreate
def test_user_create_valid(user_create_data):
    user = UserCreate(**user_create_data)
    assert user.nickname == user_create_data["nickname"]
    assert user.password == user_create_data["password"]

# Tests for UserUpdate
def test_user_update_valid(user_update_data):
    user_update = UserUpdate(**user_update_data)
    assert user_update.email == user_update_data["email"]
    assert user_update.first_name == user_update_data["first_name"]

# Tests for UserResponse
def test_user_response_valid(user_response_data):
    user = UserResponse(**user_response_data)
    assert user.id == user_response_data["id"]

# Tests for LoginRequest
def test_login_request_valid(login_request_data):
    login = LoginRequest(**login_request_data)
    assert login.email == login_request_data["email"]
    assert login.password == login_request_data["password"]

# Parametrized tests for nickname and email validation
@pytest.mark.parametrize("nickname", ["test_user", "test-user", "testuser123", "123test"])
def test_user_base_nickname_valid(nickname, user_base_data):
    user_base_data["nickname"] = nickname
    user = UserBase(**user_base_data)
    assert user.nickname == nickname

@pytest.mark.parametrize("nickname", ["test user", "test?user", "", "us"])
def test_user_base_nickname_invalid(nickname, user_base_data):
    user_base_data["nickname"] = nickname
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Parametrized tests for URL validation
@pytest.mark.parametrize("url", ["http://valid.com/profile.jpg", "https://valid.com/profile.png", None])
def test_user_base_url_valid(url, user_base_data):
    user_base_data["profile_picture_url"] = url
    user = UserBase(**user_base_data)
    assert user.profile_picture_url == url

@pytest.mark.parametrize("url", ["ftp://invalid.com/profile.jpg", "http//invalid", "https//invalid"])
def test_user_base_url_invalid(url, user_base_data):
    user_base_data["profile_picture_url"] = url
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Test for User Creation (POST route)
# def test_create_user(client, user_create_data):
#     response = client.post("/users/", json=user_create_data)
#     data = response.json()
#     assert data["nickname"] == user_create_data["nickname"]
#     assert data["email"] == user_create_data["email"]

# Test for Invalid User Creation (e.g., missing data)
def test_create_user_invalid(client, user_create_data):
    invalid_data = {**user_create_data, "nickname": ""}
    response = client.post("/users/", json=invalid_data)
    data = response.json()
    assert "detail" in data

# Test for User Update (PATCH route)
# def test_update_user(client, user_update_data):
#     # Assuming a user with ID 1 exists
#     response = client.patch("/users/1", json=user_update_data)
#     data = response.json()
#     assert data["email"] == user_update_data["email"]
#     assert data["nickname"] == user_update_data["nickname"]

# Test for Invalid User Update
def test_update_user_invalid(client):
    invalid_data = {"email": "invalid-email", "nickname": ""}
    response = client.patch("/users/1", json=invalid_data)
    data = response.json()
    assert "detail" in data

# Test for User Login Invalid (wrong credentials)
def test_login_user_invalid(client):
    invalid_data = {"email": "wrong_email", "password": "wrong_password"}
    response = client.post("/login", json=invalid_data)
    data = response.json()
    assert "detail" in data

# Test for Get User Details (GET route)
# def test_get_user_details(client):
#     # Assuming a user with ID 1 exists
#     response = client.get("/users/1")
#     data = response.json()
#     assert "id" in data
#     assert "nickname" in data

# Test for Get Non-Existent User (Bad Request)
def test_get_user_not_found(client):
    response = client.get("/users/99999")  # Non-existent ID
    data = response.json()
    assert "detail" in data


# Test for Delete Non-Existent User (Conflict)
def test_delete_user_not_found(client):
    response = client.delete("/users/99999")  # Non-existent ID
    data = response.json()
    assert "detail" in data
    