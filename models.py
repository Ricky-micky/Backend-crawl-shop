from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)  
    password_hash = db.Column(db.String(128), nullable=False)
    profile_picture = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
 
    search_history = db.relationship('SearchHistory', backref='user', lazy=True)
    tokens = db.relationship('AuthToken', back_populates='user', lazy=True)


class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    id = db.Column(db.Integer, primary_key=True)
    search_query = db.Column(db.String(255), nullable=False)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    product_price = db.Column(db.Float)
    product_rating = db.Column(db.Float)
    product_url = db.Column(db.String(255))
    delivery_cost = db.Column(db.Float)
    shop_name = db.Column(db.String(100))
    payment_mode = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    comparisons = db.relationship('ComparisonResult', backref='product', lazy=True)


class ProductSearch(db.Model):
    __tablename__ = 'product_searches'
    id = db.Column(db.Integer, primary_key=True)
    search_query = db.Column(db.String(255), nullable=False)
    query_results = db.Column(db.JSON, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuthToken(db.Model):
    __tablename__ = 'auth_tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
   
    user = db.relationship('User', back_populates='tokens', lazy=True)


class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='price_history')


# Shop model
class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    
    products = db.relationship('Product', backref='shop', lazy=True)  # Related products for the shop
    comparisons = db.relationship('ComparisonResult', backref='shop', lazy=True)  # Related comparisons


# ComparisonResult Model
class ComparisonResult(db.Model):
    __tablename__ = 'comparison_results'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    shop_x_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    shop_y_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    
    product_name = db.Column(db.String, nullable=False)
    shop_x_cost = db.Column(db.Float, nullable=False)
    shop_x_rating = db.Column(db.Float)
    shop_x_delivery_cost = db.Column(db.Float, nullable=False)
    shop_x_payment_mode = db.Column(db.String)
    
    shop_y_cost = db.Column(db.Float, nullable=False)
    shop_y_rating = db.Column(db.Float)
    shop_y_delivery_cost = db.Column(db.Float, nullable=False)
    shop_y_payment_mode = db.Column(db.String)
    
    marginal_benefit = db.Column(db.Float)
    cost_benefit = db.Column(db.Float)
    
    shop_x = db.relationship('Shop', foreign_keys=[shop_x_id], backref='comparison_shop_x', lazy=True)
    shop_y = db.relationship('Shop', foreign_keys=[shop_y_id], backref='comparison_shop_y', lazy=True)
