import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from models import db, User, Product, Shop, ProductSearch, ComparisonResult
from app import filter_bp

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
        
        # Create test user
        user = User(username="testuser", is_admin=False)
        user.set_password("password123")  # Assuming User has a set_password method
        db.session.add(user)

        # Create test shops
        shop1 = Shop(name="Shop A", url="https://shopa.com")
        shop2 = Shop(name="Shop B", url="https://shopb.com")
        db.session.add_all([shop1, shop2])
        db.session.commit()

        # Create test products
        product1 = Product(product_name="Laptop", product_price=1000, product_rating=4.5, 
                           product_url="https://shopa.com/laptop", delivery_cost=50, 
                           shop_name="Shop A", payment_mode="Credit Card", shop_id=shop1.id)

        product2 = Product(product_name="Laptop", product_price=950, product_rating=4.0, 
                           product_url="https://shopb.com/laptop", delivery_cost=40, 
                           shop_name="Shop B", payment_mode="Debit Card", shop_id=shop2.id)

        db.session.add_all([product1, product2])
        db.session.commit()

        # Add search history for the user
        search_entry = ProductSearch(
            user_id=user.id, 
            product_name="Laptop",
            product_price=1000, 
            product_rating=4.5, 
            product_url="https://shopa.com/laptop",
            delivery_cost=50,
            shop_name="Shop A",
            payment_mode="Credit Card",
            shop_id=shop1.id
        )
        db.session.add(search_entry)
        db.session.commit()

    app.register_blueprint(filter_bp)

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

def test_filter_sorting_success(client, auth_headers):
    """Test filtering and sorting products successfully"""
    response = client.get("/filter_sort?q=Laptop", headers=auth_headers)
    assert response.status_code == 200
    assert "results" in response.json
    assert len(response.json["results"]) > 0

def test_filter_sorting_no_results(client):
    """Test filtering when no products match the query"""
    response = client.get("/filter_sort?q=Tablet")
    assert response.status_code == 404
    assert response.json["message"] == "No products found."

def test_filter_sorting_without_query(client):
    """Test filtering without providing a search query"""
    response = client.get("/filter_sort?q=")
    assert response.status_code == 400
    assert response.json["error"] == "Please provide a search query."

def test_filter_sorting_sort_by_marginal_benefit(client, auth_headers):
    """Test sorting results by Marginal Benefit (MB)"""
    response = client.get("/filter_sort?q=Laptop&sort_by=mb", headers=auth_headers)
    assert response.status_code == 200
    assert "results" in response.json
    results = response.json["results"]
    assert len(results) > 0
    assert results == sorted(results, key=lambda x: x["marginal_benefit"], reverse=True)

def test_filter_sorting_sort_by_cost_benefit(client, auth_headers):
    """Test sorting results by Cost-Benefit (CB)"""
    response = client.get("/filter_sort?q=Laptop&sort_by=cb", headers=auth_headers)
    assert response.status_code == 200
    assert "results" in response.json
    results = response.json["results"]
    assert len(results) > 0
    assert results == sorted(results, key=lambda x: x["cost_benefit"])
