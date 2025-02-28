import pytest
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token


@pytest.fixture
def test_client():
    """Set up a test client with an in-memory database"""
    app = create_app("testing")  # Ensure the app supports test config
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()


@pytest.fixture
def create_test_user():
    """Create a test user in the database"""
    user = User(
        username="testuser",
        email="test@example.com",
        phone_number="1234567890",
        password_hash=generate_password_hash("password"),
        profile_picture=None,
        is_admin=False
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_headers(create_test_user):
    """Generate JWT token for authentication"""
    access_token = create_access_token(identity=create_test_user.id)
    return {"Authorization": f"Bearer {access_token}"}


# ✅ Test User Registration
def test_register_user(test_client):
    response = test_client.post('/register', json={
        "username": "newuser",
        "email": "newuser@example.com",
        "phone_number": "9876543210",
        "password": "securepassword",
        "profile_picture": None,
        "is_admin": False
    })
    assert response.status_code == 201
    assert response.json["message"] == "User registered successfully"


# ✅ Test User Login
def test_login_user(test_client, create_test_user):
    response = test_client.post('/login', json={
        "email": "test@example.com",
        "password": "password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json


# ❌ Test Login with Wrong Credentials
def test_login_invalid_credentials(test_client, create_test_user):
    response = test_client.post('/login', json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json["message"] == "Invalid credentials"


# ✅ Test Fetching the Current User (Authenticated)
def test_get_current_user(test_client, auth_headers):
    response = test_client.get('/me', headers=auth_headers)
    assert response.status_code == 200
    assert response.json["username"] == "testuser"
    assert response.json["email"] == "test@example.com"


# ❌ Test Fetching User Without Authentication
def test_get_current_user_unauthenticated(test_client):
    response = test_client.get('/me')
    assert response.status_code == 401  # Unauthorized


# ✅ Test Fetching a Specific User by ID
def test_get_user_by_id(test_client, create_test_user, auth_headers):
    response = test_client.get(f'/{create_test_user.id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json["username"] == "testuser"


# ❌ Test Fetching a Non-Existent User
def test_get_nonexistent_user(test_client, auth_headers):
    response = test_client.get('/999', headers=auth_headers)  # ID 999 unlikely to exist
    assert response.status_code == 404
    assert response.json["message"] == "User not found"


# ✅ Test Updating User Information
def test_update_user(test_client, auth_headers):
    response = test_client.put('/update', headers=auth_headers, json={
        "username": "updateduser",
        "email": "updated@example.com"
    })
    assert response.status_code == 200
    assert response.json["message"] == "User updated successfully"


# ❌ Test Updating User Without Authentication
def test_update_user_unauthenticated(test_client):
    response = test_client.put('/update', json={
        "username": "unauthorizeduser"
    })
    assert response.status_code == 401


# ✅ Test Deleting a User (Self-Deletion)
def test_delete_user(test_client, create_test_user, auth_headers):
    response = test_client.delete(f'/{create_test_user.id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json["message"] == "User deleted successfully"


# ❌ Test Deleting a Non-Existent User
def test_delete_nonexistent_user(test_client, auth_headers):
    response = test_client.delete('/999', headers=auth_headers)
    assert response.status_code == 404
    assert response.json["error"] == "User not found"


# ❌ Test Deleting a User Without Authentication
def test_delete_user_unauthenticated(test_client):
    response = test_client.delete('/1')  # Trying to delete without token
    assert response.status_code == 401  # Unauthorized
