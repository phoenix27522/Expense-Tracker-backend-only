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
import logging

# Configure logging to log to a file
logging.basicConfig(filename='app.log', 
                    level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

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

# adding expense 
@main.route('/add_expense', methods=['POST'])
def adding_new_expenses():
    data = request.get_json()  # Expect JSON payload in the request body

    if not data or 'user_name' not in data:
        return jsonify({'message': 'User not specified'}), 400

    # Extracting required fields from the JSON payload
    user_name = data.get('user_name')
    amount = data.get('amount')
    description = data.get('description')
    date = data.get('date')
    category_id = data.get('Category')  # Assuming this is passed in the JSON

    # Validate the incoming data (basic validation)
    if amount is None or description is None or date is None or category_id is None:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        # Convert the date to the appropriate format if needed
        date_purchase = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

        # Create the expense
        new_expense = Expenses(
            amount=amount,
            description=description,
            date=date_purchase,
            user_id=User.query.filter_by(user_name=user_name).first().id,
            category_id=category_id
        )
        db.session.add(new_expense)
        db.session.commit()

        return jsonify({'message': 'Expense added successfully'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# show expenses
@main.route('/expenses', methods=['GET'])
def show_expenses():
    user_name = request.args.get("user")  # Using query parameters to get the username
    if user_name is None:
        return jsonify({'message': 'User not specified'}), 400

    # Query the user's expenses
    expenses_user = db.session.query(Expenses).join(User).filter(User.user_name == user_name).all()
    
    if not expenses_user:
        return jsonify({'message': f'No expenses found for user {user_name}'}), 404

    # Calculate the total amount of expenses
    total_amount = sum(expense.amount for expense in expenses_user)

    # Prepare the response
    expenses_data = [{'id': expense.id, 'amount': expense.amount, 'description': expense.description} for expense in expenses_user]

    return jsonify({
        'user': user_name,
        'total': round(total_amount, 2),
        'expenses': expenses_data
    }), 200

#modifiying expense
@main.route('/mod_expense', methods=['POST'])
def modifying_expenses():
    data = request.get_json()  # Expect JSON payload in the request body

    name_user = data.get("user")
    expense_id = data.get("id")

    if name_user is None or expense_id is None:
        return jsonify({'message': 'User or expense ID not specified'}), 400

    # Fetch the expense by ID
    query = db.session.query(Expenses).filter(Expenses.id == expense_id).first()
    if not query:
        return jsonify({'message': 'Expense not found'}), 404

    if 'Delete' in data:
        # Handle deletion of the expense
        db.session.delete(query)
        db.session.commit()
        return jsonify({'message': 'Expense deleted successfully'}), 200

    # Updating expense details based on the existing fields
    try:
        query.description = data.get('Description', query.description)  # Update description
        query.date = datetime.strptime(data.get('Date'), "%Y-%m-%dT%H:%M:%S") if data.get('Date') else query.date
        query.amount = data.get('Amount', query.amount)  # Update amount
        query.category_id = data.get('Category', query.category_id)  # Update category if provided

        db.session.commit()
        return jsonify({'message': 'Expense updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Filtering expenses
@main.route('/filter_expenses', methods=['GET'])
@jwt_required()
def filter_expenses():
    user_id = get_jwt_identity()  # Assuming JWT contains the user ID

    # Retrieve query parameters
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    sort_by = request.args.get('sort_by', 'date')  # Default sort field
    order = request.args.get('order', 'asc')

    # Convert date strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

    # Build the query
    query = Expenses.query.filter_by(user_id=user_id)

    if min_amount is not None:
        query = query.filter(Expenses.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Expenses.amount <= max_amount)

    if start_date:
        query = query.filter(Expenses.date >= start_date)

    if end_date:
        query = query.filter(Expenses.date <= end_date)

    if order == 'asc':
        query = query.order_by(getattr(Expenses, sort_by).asc())
    else:
        query = query.order_by(getattr(Expenses, sort_by).desc())

    expenses = query.all()

    # Serialize the data
    result = []
    for expense in expenses:
        expense_data = {
            'id': expense.id,  # Using the primary key
            'amount': expense.amount,
            'description': expense.description,  # Match the model
            'date': expense.date.strftime('%Y-%m-%d'),  # Correctly formatting date
            'user_id': expense.user_id,  # Use user_id from the model
            'category_id': expense.category_id  # Use category_id from the model
        }
        result.append(expense_data)

    return jsonify(result), 200

# Viewing profile
@main.route('/profile', methods=['GET'])
@jwt_required()
def view_profile():
    try:
        # Get the current user's ID from the JWT token
        user_id = get_jwt_identity()

        # Retrieve the user from the database
        user = User.query.get(user_id)

        # Check if the user exists
        if not user:
            logging.error(f"User with ID {user_id} not found")
            return jsonify({'error': 'User not found'}), 404

        # Return the user profile details
        return jsonify({
            'user_name': user.user_name,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        }), 200

    except Exception as e:
        # Log the error for debugging with the exception details
        logging.error(f"Error in view_profile: {e}", exc_info=True)
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Editing profile 
@main.route('/profile', methods=['PUT'])
@jwt_required()
def edit_profile():
    try:
        # Get the current user's ID from the JWT token
        user_id = get_jwt_identity()

        # Retrieve the user from the database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get the data from the request
        data = request.get_json()
        user_name = data.get('user_name')
        email = data.get('email')

        # Validate the input data
        if not user_name or not email:
            return jsonify({'error': 'Username and email are required'}), 400

        # Validate the email format
        email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if the new username or email already exists
        existing_user = User.query.filter(
            (User.user_name == user_name) | (User.email == email)).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Username or email already in use'}), 400

        # Update the user profile
        user.user_name = user_name
        user.email = email

        # Commit the changes to the database
        db.session.commit()

        return jsonify({'message': 'Profile updated successfully'}), 200

    except Exception as e:
        # Rollback only if it's a database-related error
        db.session.rollback()
        
        # Log the error for production debugging
        logging.error(f"Error in edit_profile: {e}")

        return jsonify({'error': 'An unexpected error occurred'}), 500

# getting notification 
@main.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        # Get the current user's ID from the JWT token
        user_id = get_jwt_identity()
        if not user_id:
            logging.warning('JWT token did not provide a valid user ID.')
            return jsonify({'error': 'Invalid token'}), 401

        # Query for the user's notifications
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

        # Log if no notifications found
        if not notifications:
            logging.info(f'No notifications found for user ID {user_id}')

        # Prepare the response
        return jsonify([
            {
                'id': notification.id,
                'message': notification.message,
                'type': notification.type,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': notification.is_read
            } for notification in notifications
        ]), 200

    except Exception as e:
        # Log the exception for debugging
        logging.error(f"Error fetching notifications for user ID {user_id}: {e}", exc_info=True)
        return jsonify({'error': 'An unexpected error occurred'}), 500

# mark read for notification 
@main.route('/notifications/<int:id>/read', methods=['PATCH'])
@jwt_required()
def mark_notification_as_read(id):
    try:
        # Get the current user's ID from the JWT
        user_id = get_jwt_identity()

        # Query the notification by ID and user_id to ensure the user owns the notification
        notification = Notification.query.filter_by(id=id, user_id=user_id).first()

        if not notification:
            return jsonify({'error': 'Notification not found'}), 404

        # Check if the notification is already marked as read
        if notification.is_read:
            return jsonify({'message': 'Notification is already marked as read'}), 200

        # Mark the notification as read
        notification.is_read = True
        db.session.commit()  # Ensure the session is active when committing changes

        return jsonify({'message': 'Notification marked as read'}), 200

    except Exception as e:
        # Rollback in case of an exception during the database commit
        db.session.rollback()

        # Log the error for further investigation
        logging.error(f"Error marking notification as read: {e}", exc_info=True)

        return jsonify({'error': 'An unexpected error occurred'}), 500


@main.route('/notifications/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_notification(id):
    user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=id, user_id=user_id).first()

    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    # Explicitly merge the object into the current session if it's detached
    notification = db.session.merge(notification)

    db.session.delete(notification)
    db.session.commit()

    return jsonify({'message': 'Notification deleted successfully'}), 200

@main.route('/export/csv', methods=['GET'])
@jwt_required()
def export_expenses_csv():
    try:
        user_id = get_jwt_identity()
        expenses = Expenses.query.filter_by(user_name=user_id).all()

        si = StringIO()
        csv_writer = csv.writer(si)
        csv_writer.writerow(['Type', 'Description', 'Date', 'Amount', 'Recurrence', 'RecurrenceEndDate'])

        for expense in expenses:
            csv_writer.writerow([
                expense.type_expense,
                expense.description_expense,
                expense.date_purchase.strftime('%Y-%m-%d'),
                expense.amount,
                expense.recurrence,
                expense.recurrence_end_date.strftime('%Y-%m-%d') if expense.recurrence_end_date else None
            ])

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=expenses.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    except Exception as e:
        print(f"Error in export_expenses_csv: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@main.route('/export/pdf', methods=['GET'])
@jwt_required()
def export_expenses_pdf():
    try:
        user_id = get_jwt_identity()
        expenses = Expenses.query.filter_by(user_name=user_id).all()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Expense Report", ln=True, align='C')

        pdf.cell(50, 10, txt="Type", border=1)
        pdf.cell(70, 10, txt="Description", border=1)
        pdf.cell(30, 10, txt="Date", border=1)
        pdf.cell(30, 10, txt="Amount", border=1)
        pdf.cell(30, 10, txt="Recurrence", border=1)
        pdf.cell(30, 10, txt="End Date", border=1)
        pdf.ln()

        for expense in expenses:
            pdf.cell(50, 10, txt=expense.type_expense, border=1)
            pdf.cell(70, 10, txt=expense.description_expense, border=1)
            pdf.cell(30, 10, txt=expense.date_purchase.strftime('%Y-%m-%d'), border=1)
            pdf.cell(30, 10, txt=f"{expense.amount:.2f}", border=1)
            pdf.cell(30, 10, txt=expense.recurrence if expense.recurrence else "", border=1)
            pdf.cell(30, 10, txt=expense.recurrence_end_date.strftime('%Y-%m-%d') if expense.recurrence_end_date else "", border=1)
            pdf.ln()

        output = make_response(pdf.output(dest='S').encode('latin1'))
        output.headers["Content-Disposition"] = "attachment; filename=expenses.pdf"
        output.headers["Content-type"] = "application/pdf"
        return output

    except Exception as e:
        print(f"Error in export_expenses_pdf: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
