from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from models import db  # Import db from models.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate  # For database migrations
from flask_jwt_extended import JWTManager  # For JWT authentication
from flask_cors import CORS  # For handling CORS


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enabling CORS for cross-origin requests

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shopcrawl.db'  # Path to your database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
db.init_app(app)  # Initialize db with the app
migrate = Migrate(app, db)  # Initialize migrations with the app and db


# JWT configuration
app.config["JWT_SECRET_KEY"] = "fghsgdgfdsgf"  # Secret key for JWT
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)  # Set the expiration time for access tokens
jwt = JWTManager(app)  # Initialize JWTManager

# Import and register blueprints (Ensure these views exist)
from views import *


# Register blueprints with the app
app.register_blueprint(auth_bp)
app.register_blueprint(filter_bp)
app.register_blueprint(product_bp)
app.register_blueprint(search_bp)
app.register_blueprint(user_bp)
app.register_blueprint(shop_bp)

if __name__ == "__main__":
    app.run(debug=True)  # Start the Flask app in debug mode
