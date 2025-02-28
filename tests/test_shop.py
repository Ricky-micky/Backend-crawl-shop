import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from models import db, User, Shop
from app import shop_bp

@pytest.fixture
def client():
    """Set up a test client and an in-memory database."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test_secret"
    
    db.init_app(app)
    app.register_blueprint(shop_bp)

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    admin = User(username="admin", email="admin@example.com", phone_number="1234567890", is_admin=True)
    admin.password_hash = "hashed_password"
    db.session.add(admin)
    db.session.commit()
    return admin

@pytest.fixture
def normal_user():
    """Create a non-admin user for testing."""
    user = User(username="user", email="user@example.com", phone_number="0987654321", is_admin=False)
    user.password_hash = "hashed_password"
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def admin_token(client, admin_user):
    """Generate a JWT token for the admin user."""
    return create_access_token(identity=admin_user.id)

@pytest.fixture
def user_token(client, normal_user):
    """Generate a JWT token for a normal user."""
    return create_access_token(identity=normal_user.id)

@pytest.fixture
def test_shop():
    """Create a test shop."""
    shop = Shop(name="Test Shop", url="https://example.com")
    db.session.add(shop)
    db.session.commit()
    return shop

def test_create_shop_admin(client, admin_token):
    """Test that an admin can create a shop."""
    response = client.post(
        "/shops",
        json={"name": "New Shop", "url": "https://newshop.com"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    assert response.json["message"] == "Shop created successfully"

def test_create_shop_non_admin(client, user_token):
    """Test that a normal user cannot create a shop."""
    response = client.post(
        "/shops",
        json={"name": "Unauthorized Shop", "url": "https://unauthorized.com"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    assert response.json["message"] == "Only admins can create shops"

def test_get_all_shops(client, test_shop):
    """Test retrieving all shops."""
    response = client.get("/shops")
    assert response.status_code == 200
    assert len(response.json) > 0

def test_get_single_shop(client, test_shop):
    """Test retrieving a single shop by ID."""
    response = client.get(f"/shops/{test_shop.id}")
    assert response.status_code == 200
    assert response.json["name"] == "Test Shop"

def test_get_nonexistent_shop(client):
    """Test fetching a non-existent shop."""
    response = client.get("/shops/9999")  # ID that doesn't exist
    assert response.status_code == 404
    assert response.json["message"] == "Shop not found"

def test_update_shop_admin(client, admin_token, test_shop):
    """Test that an admin can update a shop."""
    response = client.put(
        f"/shops/{test_shop.id}",
        json={"name": "Updated Shop"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Shop updated successfully"

def test_update_shop_non_admin(client, user_token, test_shop):
    """Test that a normal user cannot update a shop."""
    response = client.put(
        f"/shops/{test_shop.id}",
        json={"name": "Unauthorized Update"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    assert response.json["message"] == "Only admins can update shops"

def test_delete_shop_admin(client, admin_token, test_shop):
    """Test that an admin can delete a shop."""
    response = client.delete(
        f"/shops/{test_shop.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json["message"] == "Shop deleted successfully"

def test_delete_shop_non_admin(client, user_token, test_shop):
    """Test that a normal user cannot delete a shop."""
    response = client.delete(
        f"/shops/{test_shop.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    assert response.json["message"] == "Only admins can delete shops"

def test_delete_nonexistent_shop(client, admin_token):
    """Test deleting a shop that does not exist."""
    response = client.delete(
        "/shops/9999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    assert response.json["message"] == "Shop not found"
