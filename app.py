from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the Flask app and configure it
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Database URI, for SQLite
app.config['SECRET_KEY'] = 'your_secret_key'  # For session management
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the models as per your initial code (User, SearchHistory, Product, etc.)

# User registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")
        password_hash = generate_password_hash(password)  # Hash the password
        
        user = User(username=username, email=email, phone_number=phone_number, password_hash=password_hash)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating account. Please try again.', 'danger')
            return redirect(url_for('register'))
    return render_template("register.html")

# User login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template("login.html")

# Dashboard route (after login)
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# Route to handle user search history
@app.route("/search", methods=["POST"])
def search():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        user_id = 1  # For now, use user ID 1. You can dynamically fetch the logged-in user's ID
        
        search_history = SearchHistory(search_query=search_query, user_id=user_id)
        
        try:
            db.session.add(search_history)
            db.session.commit()
            flash('Search recorded successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error saving search. Please try again.', 'danger')
        return redirect(url_for('dashboard'))

# Setup for handling the database and starting the app
if __name__ == "__main__":
    db.create_all()  # Create all tables from models
    app.run(debug=True)
