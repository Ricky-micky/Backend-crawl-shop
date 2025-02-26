import pytest
import time
from flask import Flask
from werkzeug.security import generate_password_hash
from models import User, db
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_jwt_extended import JWTManager
from views.auth import auth_bp, serializer  # Import the same serializer instance

# Fixture to initialize the Flask app
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
    app.config['MAIL_SUPPRESS_SEND'] = True
    db.init_app(app)
    JWTManager(app)
    mail = Mail(app)
    app.register_blueprint(auth_bp)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

# Fixture to create a test client
@pytest.fixture
def client(app):
    return app.test_client()

# Fixture to create a test user
@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            phone_number='1234567890',
            password_hash=generate_password_hash('testpassword')
        )
        db.session.add(user)
        db.session.commit()
        return user

# Test case for expired token
def test_reset_password_expired_token(client, test_user):
    # Generate the token without max_age
    token = serializer.dumps('test@example.com', salt="password-reset-salt")
    
    # Wait for 2 seconds to simulate the token expiring
    time.sleep(2)
    
    # Now post the token to the reset-password endpoint
    response = client.post(f'/reset-password/{token}', json={'new_password': 'newpassword'})
    
    # Assert that the response code is 400 and the message is 'Token expired'
    assert response.status_code == 400
    assert response.json['message'] == 'Token expired'

# Test case for invalid token
def test_reset_password_invalid_token(client):
    response = client.post('/reset-password/invalidtoken', json={'new_password': 'newpassword'})
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid token'

# Test case for successful password reset
def test_reset_password_success(client, test_user):
    # Generate the token
    token = serializer.dumps('test@example.com', salt="password-reset-salt")
    
    # Post the token to the reset-password endpoint
    response = client.post(f'/reset-password/{token}', json={'new_password': 'newpassword'})
    
    # Assert that the response code is 200 and the message is 'Password reset successfully'
    assert response.status_code == 200
    assert response.json['message'] == 'Password reset successfully'