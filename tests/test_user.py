import pytest
from werkzeug.security import generate_password_hash
from flask import Flask
from models import db, User
from flask_jwt_extended import JWTManager, create_access_token

# Fixtures to set up the application and database
@pytest.fixture
def app():
    # Create a Flask application for testing
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
    
    db.init_app(app)
    JWTManager(app)

    # Register the Blueprint
    from views.user import user_bp  # Assuming the Blueprint is named 'user_bp'
    app.register_blueprint(user_bp)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    # Return the test client for sending requests
    return app.test_client()

@pytest.fixture
def test_user(app):
    # Add a test user to the database
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            phone_number='1234567890',
            password_hash=generate_password_hash('testpassword'),
            profile_picture='test.jpg',
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        return user

# Test: Register a new user
def test_register(client):
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "phone_number": "9876543210",
        "password": "newpassword",
        "profile_picture": "new.jpg",
        "is_admin": False
    }
    response = client.post('/register', json=data)
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

# Test: Login with correct credentials
def test_login(client, test_user):
    data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert response.json['user']['email'] == 'test@example.com'

# Test: Fetch the current logged-in user
def test_get_current_user(client, test_user):
    # Log in to get the access token
    data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    login_response = client.post('/login', json=data)
    access_token = login_response.json['access_token']

    # Use the access token to access the 'me' endpoint
    response = client.get('/me', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json['email'] == 'test@example.com'

# Test: Fetch a specific user by ID
def test_get_user(client, test_user):
    # Log in to get the access token
    data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    login_response = client.post('/login', json=data)
    access_token = login_response.json['access_token']

    # Fetch the user by ID
    response = client.get(f'/{test_user.id}', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json['email'] == 'test@example.com'

# Test: Update the logged-in user details
def test_update_user(client, test_user):
    # Log in to get the access token
    data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    login_response = client.post('/login', json=data)
    access_token = login_response.json['access_token']

    # Update the user details
    update_data = {
        "username": "updateduser",
        "email": "updated@example.com",
        "phone_number": "1112223333",
        "password": "updatedpassword",
        "profile_picture": "updated.jpg",
        "is_admin": True
    }
    response = client.put('/update', json=update_data, headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'User updated successfully'

# Test: Delete a user
def test_delete_user(client, test_user):
    # Log in to get the access token
    data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    login_response = client.post('/login', json=data)
    access_token = login_response.json['access_token']

    # Delete the user
    response = client.delete(f'/{test_user.id}', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'User deleted successfully'

