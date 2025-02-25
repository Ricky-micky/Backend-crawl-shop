from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Shop, User, db

# Define the Blueprint
search_bp = Blueprint('search', __name__)