import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from models import db, User, Product, Shop, ProductSearch
from app import search_bp

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
        
        # Create test users
        user = User(username="testuser", is_admin=False)
        user.set_password("password123")  # Assuming User has a set_password method
        db.session.add(user)

        admin = User(username="admin", is_admin=True)
        admin.set_password("adminpass")
        db.session.add(admin)

        # Create test shops
        shop = Shop(name="Test Shop", url="https://testshop.com")
        db.session.add(shop)
        db.session.commit()

        # Create test products
        product1 = Product(product_name="Laptop", product_price=1000, product_rating=4.5, 
                           product_url="https://shop.com/laptop", delivery_cost=50, 
                           shop_name="Test Shop", payment_mode="Credit Card", shop_id=shop.id)

        product2 = Product(product_name="Phone", product_price=800, product_rating=4.2, 
                           product_url="https://shop.com/phone", delivery_cost=20, 
                           shop_name="Test Shop", payment_mode="Debit Card", shop_id=shop.id)

        db.session.add_all([product1, product2])
        db.session.commit()

    app.register_blueprint(search_bp)

    yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client for making requests"""
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    """Generate authentication headers for a test user"""
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        access_token = create_access_token(identity=user.id)
        return {"Authorization": f"Bearer {access_token}"}

def test_search_products_success(client):
    """Test searching for a valid product"""
    response = client.get("/search?q=Laptop")
    assert response.status_code == 200
    assert "results" in response.json
    assert len(response.json["results"]) > 0
    assert response.json["results"][0]["product_name"] == "Laptop"

def test_search_no_results(client):
    """Test searching for a non-existent product"""
    response = client.get("/search?q=Tablet")
    assert response.status_code == 404
    assert response.json["message"] == "No products found."

def test_search_without_query(client):
    """Test searching without providing a query"""
    response = client.get("/search?q=")
    assert response.status_code == 400
    assert response.json["error"] == "Please provide a search query."

def test_search_records_history_for_authenticated_users(client, auth_headers):
    """Test that search results are stored for authenticated users"""
    response = client.get("/search?q=Phone", headers=auth_headers)
    assert response.status_code == 200

    with client.application.app_context():
        search_history = ProductSearch.query.all()
        assert len(search_history) == 1  # Only one search entry should be recorded
        assert search_history[0].product_name == "Phone"
