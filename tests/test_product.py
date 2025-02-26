import pytest
from flask_jwt_extended import create_access_token
from models import db, Product, User, Shop
from app import create_app  # Assuming you have a factory function `create_app`

@pytest.fixture(scope="module")
def app():
    # Create the app instance with testing config
    app = create_app(testing=True)
    yield app

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

@pytest.fixture(scope="module")
def init_db(app):
    # Create the tables in the test database
    with app.app_context():
        db.create_all()

    # Create test user and admin
    user = User(username="testuser", password="password", is_admin=False)
    admin = User(username="admin", password="password", is_admin=True)
    db.session.add(user)
    db.session.add(admin)
    db.session.commit()

    # Create a test shop
    shop = Shop(name="Test Shop")
    db.session.add(shop)
    db.session.commit()

    # Generate tokens for both user and admin
    user_token = create_access_token(identity=user.id)
    admin_token = create_access_token(identity=admin.id)

    yield {
        "user_token": user_token,
        "admin_token": admin_token,
        "user": user,
        "admin": admin,
        "shop": shop
    }

    # Cleanup after tests
    with app.app_context():
        db.session.remove()
        db.drop_all()

# Test Cases

def test_create_product_success(client, init_db):
    data = {
        "product_name": "Test Product",
        "product_price": 99.99,
        "shop_id": init_db["shop"].id,
        "shop_name": "Test Shop",
    }

    response = client.post('/products', json=data, headers={"Authorization": f"Bearer {init_db['user_token']}"})
    assert response.status_code == 201
    assert 'id' in response.get_json()

def test_create_product_missing_fields(client, init_db):
    data = {
        "product_name": "Test Product",
        "product_price": 99.99,
    }

    response = client.post('/products', json=data, headers={"Authorization": f"Bearer {init_db['user_token']}"})
    assert response.status_code == 400
    assert response.get_json()['message'] == 'Product name, price, and shop_id are required'

def test_create_product_shop_not_found(client, init_db):
    data = {
        "product_name": "Test Product",
        "product_price": 99.99,
        "shop_id": 9999,  # Non-existent shop
        "shop_name": "Test Shop",
    }

    response = client.post('/products', json=data, headers={"Authorization": f"Bearer {init_db['user_token']}"})
    assert response.status_code == 404
    assert response.get_json()['message'] == 'Shop not found'

def test_get_all_products(client, init_db):
    product = Product(
        product_name="Product 1",
        product_price=19.99,
        shop_id=init_db["shop"].id,
        shop_name="Test Shop"
    )
    db.session.add(product)
    db.session.commit()

    response = client.get('/products')
    assert response.status_code == 200
    assert len(response.get_json()) > 0

def test_get_product(client, init_db):
    product = Product(
        product_name="Product 2",
        product_price=29.99,
        shop_id=init_db["shop"].id,
        shop_name="Test Shop"
    )
    db.session.add(product)
    db.session.commit()

    response = client.get(f'/products/{product.id}')
    assert response.status_code == 200
    assert response.get_json()['id'] == product.id

def test_get_product_not_found(client, init_db):
    response = client.get('/products/9999')
    assert response.status_code == 404
    assert response.get_json()['message'] == 'Product not found'

def test_update_product_admin(client, init_db):
    product = Product(
        product_name="Product 3",
        product_price=49.99,
        shop_id=init_db["shop"].id,
        shop_name="Test Shop"
    )
    db.session.add(product)
    db.session.commit()

    data = {
        "product_name": "Updated Product",
        "product_price": 59.99,
    }

    response = client.put(f'/products/{product.id}', json=data, headers={"Authorization": f"Bearer {init_db['admin_token']}"})
    assert response.status_code == 200
    assert response.get_json()['product']['product_name'] == "Updated Product"

def test_update_product_not_admin(client, init_db):
    product = Product(
        product_name="Product 4",
        product_price=59.99,
        shop_id=init_db["shop"].id,
        shop_name="Test Shop"
    )
    db.session.add(product)
    db.session.commit()

    data = {
        "product_name": "Updated Product",
        "product_price": 69.99,
    }

    response = client.put(f'/products/{product.id}', json=data, headers={"Authorization": f"Bearer {init_db['user_token']}"})
    assert response.status_code == 403
    assert response.get_json()['message'] == 'Only admins can update products'

def test_delete_product_admin(client, init_db):
    product = Product(
        product_name="Product 5",
        product_price=69.99,
        shop_id=init_db["shop"].id,
        shop_name="Test Shop"
    )
    db.session.add(product)
    db.session.commit()

    response = client.delete(f'/products/{product.id}', headers={"Authorization": f"Bearer {init_db['admin_token']}"})
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Product deleted successfully'

def test_delete_product_not_admin(client, init_db):
    product = Product(
        product_name="Product 6",
        product_price=79.99,
        shop_id=init_db["shop"].id,
        shop_name="Test Shop"
    )
    db.session.add(product)
    db.session.commit()

    response = client.delete(f'/products/{product.id}', headers={"Authorization": f"Bearer {init_db['user_token']}"})
    assert response.status_code == 403
    assert response.get_json()['message'] == 'Only admins can delete products'
