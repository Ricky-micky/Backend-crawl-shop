from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Shop, User, db

# Define the Blueprint
filter_bp = Blueprint('filter', __name__)
