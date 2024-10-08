import csv
from fpdf import FPDF
from io import StringIO
import bcrypt
from flask import Flask, make_response, render_template, request, url_for, redirect, jsonify, Blueprint
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.models import Category, Notification, User, Expenses  # Correct model names
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

# protected
@main.route('/protected', methods=['GET'])
@jwt_required()  # Ensures that only users with a valid JWT can access this route
def protected():
    current_user = get_jwt_identity()  # Retrieves the identity of the logged-in user from the JWT
    return jsonify({'message': f'Welcome, user {current_user}'}), 200

# Add user
@main.route('/add_user', methods=['POST'])
def adding_new_users():
    data = request.get_json()

    if not data or not data.get('Name') or not data.get('Email_address'):
        return jsonify({'message': 'Missing required fields'}), 400

    # Basic email validation
    email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if not re.match(email_regex, data.get('Email_address')):
        return jsonify({'message': 'Invalid email format'}), 400

    try:
        # Create a new user with the provided data
        new_user = User(
            user_name=data.get("Name"), 
            email=data.get("Email_address")
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User added successfully'}), 201

    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction to avoid inconsistent state
        
        # Print the original error message for debugging
        print("IntegrityError:", str(e))

        # Check for unique constraint violations
        if "UNIQUE constraint failed: user.email" in str(e.orig):
            return jsonify({'message': 'This email is already in use, please use a different email'}), 400
        elif "UNIQUE constraint failed: user.user_name" in str(e.orig):
            return jsonify({'message': 'This name is already in use, please use a different name'}), 400

    except Exception as e:
        # General exception handling if something else goes wrong
        return jsonify({'message': 'An unexpected error occurred'}), 500
