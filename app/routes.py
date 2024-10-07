import csv
from fpdf import FPDF
from io import StringIO
import bcrypt
from flask import Flask, make_response, render_template, request, url_for, redirect, jsonify, Blueprint
from sqlalchemy import func
from app.models import Category, Notification, User, Expenses  # Correct model names
#from app.forms import AddUser, AddExpense, ModExpense
from datetime import date, datetime
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from app.utils import verify_user_credentials
from app import blacklist, db, jwt
import re

main = Blueprint('main', __name__)

@main.route('/')
def home(): 
    count_users = User.query.count()
    if count_users==0: 
        return render_template("home.html")
    else: 
        users = User.query.all() 
        return render_template("home.html", users=users)
    
@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('user_name') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400

    user_name = data['user_name']
    email = data['email']
    password = data['password']

    email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if not re.match(email_regex, email):
        return jsonify({'message': 'Invalid email format'}), 400

    if len(password) < 6:
        return jsonify({'message': 'Password too short, must be at least 6 characters'}), 400

    existing_user = User.query.filter((User.user_name == user_name) | (User.email == email)).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    # Correct bcrypt usage
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = User(
        user_name=user_name,
        email=email,
        password_hash=password_hash
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# login route
@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate input data
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400

    email = data['email']
    password = data['password']

    # Verify user credentials
    user = verify_user_credentials(email, password)
    if user is None:
        return jsonify({'message': 'Invalid credentials'}), 401

    # Create access token
    access_token = create_access_token(identity=user.id)

    # Return the access token
    return jsonify({'access_token': access_token}), 200

# logout route 
@main.route('/logout', methods=['POST'])
@jwt_required()  # Ensure the user is authenticated via JWT
def logout():
    # Extract the JWT token's unique identifier (JTI)
    jti = get_jwt()['jti']
    
    # Add the JTI to the blacklist to invalidate the token
    blacklist.add(jti)
    
    # Return a success message indicating logout
    return jsonify({'message': 'Successfully logged out'}), 200
