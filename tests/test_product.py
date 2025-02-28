import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from models import db, User, Product, Shop
from app import product_bp

@pytest.fixture
def app():
    """Create and configure a new app instance for testing"""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "test-secret-key"

    db.init_app(app)

    with app.app_context():
        db.create_all()
        # Create test data
        admin_user = User(username="admin", is_admin=True)
        admin_user.set_password("password123")  # Assuming User has set_password method
        db.session.add(admin_user)
        db.session.commit()

    app.register_blueprint(product_bp)

    yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client for making requests"""
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    """Generate authentication headers for an admin user"""
    with app.app_context():
        admin = User.query.filter_by(username="admin").first()
        access_token = create_access_token(identity=admin.id)
        return {"Authorization": f"Bearer {access_token}"}

def test_create_product(client, auth_headers):
    """Test product creation"""
    # First, create a shop
    shop = Shop(name="Test Shop", url="https://testshop.com")
    db.session.add(shop)
    db.session.commit()

    # Send a request to create a product
    response = client.post("/products", json={
        "product_name": "Laptop",
        "product_price": 1500.0,
        "product_rating": 4.5,
        "product_url": "https://shop.com/laptop",
        "delivery_cost": 50,
        "shop_name": "Test Shop",
        "payment_mode": "Credit Card"
    }, headers=auth_headers)

    assert response.status_code == 201
    assert response.json["message"] == "Product created successfully"

def test_get_all_products(client):
    """Test retrieving all products"""
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_product_by_id(client):
    """Test retrieving a product by ID"""
    product = Product(product_name="Phone", product_price=800, product_rating=4.2, product_url="https://shop.com/phone", delivery_cost=20, shop_name="Test Shop", payment_mode="Debit Card", shop_id=1)
    db.session.add(product)
    db.session.commit()

    response = client.get(f"/products/{product.id}")
    assert response.status_code == 200
    assert response.json["product_name"] == "Phone"

def test_update_product(client, auth_headers):
    """Test updating a product"""
    product = Product(product_name="Tablet", product_price=500, product_rating=4.0, product_url="https://shop.com/tablet", delivery_cost=15, shop_name="Test Shop", payment_mode="PayPal", shop_id=1)
    db.session.add(product)
    db.session.commit()

    response = client.put(f"/products/{product.id}", json={
        "product_price": 550
    }, headers=auth_headers)

    assert response.status_code == 200
    assert response.json["product"]["product_price"] == 550

def test_delete_product(client, auth_headers):
    """Test deleting a product"""
    product = Product(product_name="Headphones", product_price=200, product_rating=4.8, product_url="https://shop.com/headphones", delivery_cost=10, shop_name="Test Shop", payment_mode="Mobile Money", shop_id=1)
    db.session.add(product)
    db.session.commit()

    response = client.delete(f"/products/{product.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["message"] == "Product deleted successfully"
