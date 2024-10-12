from datetime import datetime
import unittest

from flask_jwt_extended import create_access_token
from app.config import TestingConfig
from app import create_app, db
from app.models import Category, Notification, User, Expenses
import bcrypt  # Import bcrypt for password hashing

# test case for user registration
class TestUserRegistration(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Set up the database for testing
        with self.app.app_context():
            db.create_all()  # Create the database tables
            User.query.delete()  # Clear any existing users

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()  # Remove the current session
            db.drop_all()  # Drop all tables

    def test_valid_registration(self):
        response = self.client.post('/register', json={
            "user_name": "testuser",
            "email": "testuser@example.com",
            "password": "validPassword123"
        })
        print("Test valid registration:", response.get_json())
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'User registered successfully')

    def test_duplicate_registration(self):
        # Registering the user for the first time
        self.client.post('/register', json={
            "user_name": "testuser",
            "email": "testuser@example.com",
            "password": "validPassword123"
        })

        # Trying to register the same user again
        response = self.client.post('/register', json={
            "user_name": "testuser",
            "email": "testuser@example.com",
            "password": "validPassword123"
        })
        print("Test duplicate registration:", response.get_json())
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'User already exists')

    def test_invalid_email_format(self):
        response = self.client.post('/register', json={
            "user_name": "testuser",
            "email": "invalid-email-format",
            "password": "validPassword123"
        })
        print("Test invalid email format:", response.get_json())
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Invalid email format')

    def test_short_password(self):
        response = self.client.post('/register', json={
            "user_name": "testuser",
            "email": "testuser@example.com",
            "password": "short"
        })
        print("Test short password:", response.get_json())
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Password too short, must be at least 6 characters')

# test case for login
class TestUserLogin(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Set up the database
        with self.app.app_context():
            db.create_all()  # Create the database tables

            # Create a test user with the correct password hash
            password_hash = bcrypt.hashpw('validPassword123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            test_user = User(
                user_name='testuser',
                email='testuser@example.com',
                password_hash=password_hash  # Use the generated hash
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()  # Remove the current session
            db.drop_all()  # Drop all tables

    def test_valid_login(self):
        response = self.client.post('/login', json={
            'email': 'testuser@example.com',
            'password': 'validPassword123'
        })
        print("Test valid login:", response.get_json())
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.get_json())

    def test_invalid_email(self):
        response = self.client.post('/login', json={
            'email': 'invaliduser@example.com',
            'password': 'validPassword123'
        })
        print("Test invalid email:", response.get_json())
        self.assertEqual(response.status_code, 401)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Invalid credentials')

    def test_invalid_password(self):
        response = self.client.post('/login', json={
            'email': 'testuser@example.com',
            'password': 'wrongPassword'
        })
        print("Test invalid password:", response.get_json())
        self.assertEqual(response.status_code, 401)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Invalid credentials')

    def test_missing_email(self):
        response = self.client.post('/login', json={
            'password': 'validPassword123'
        })
        print("Test missing email:", response.get_json())
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Missing required fields')

    def test_missing_password(self):
        response = self.client.post('/login', json={
            'email': 'testuser@example.com'
        })
        print("Test missing password:", response.get_json())
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Missing required fields')
# test case for logout
class TestUserLogout(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Set up the database and create a user
        with self.app.app_context():
            db.create_all()
            password_hash = bcrypt.hashpw('validPassword123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            test_user = User(
                user_name='testuser',
                email='testuser@example.com',
                password_hash=password_hash
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_logout(self):
        # Login first to get the access token
        login_response = self.client.post('/login', json={
            'email': 'testuser@example.com',
            'password': 'validPassword123'
        })
        access_token = login_response.get_json()['access_token']
        
        # Logout using the access token
        response = self.client.post('/logout', headers={
            'Authorization': f'Bearer {access_token}'
        })
        print("Test logout:", response.get_json())
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Successfully logged out')

# testing the protected route
class TestProtectedRoute(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Set up the database and create a user
        with self.app.app_context():
            db.create_all()
            password_hash = bcrypt.hashpw('validPassword123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            test_user = User(
                user_name='testuser',
                email='testuser@example.com',
                password_hash=password_hash
            )
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_access_protected_route_with_valid_token(self):
        # Login to get a valid token
        login_response = self.client.post('/login', json={
            'email': 'testuser@example.com',
            'password': 'validPassword123'
        })
        access_token = login_response.get_json()['access_token']

        # Access the protected route using the valid token
        response = self.client.get('/protected', headers={
            'Authorization': f'Bearer {access_token}'
        })
        print("Test protected route with valid token:", response.get_json())
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.get_json())
        self.assertIn('Welcome, user', response.get_json()['message'])

    def test_access_protected_route_without_token(self):
        # Try to access the protected route without providing a token
        response = self.client.get('/protected')
        print("Test protected route without token:", response.get_json())
        self.assertEqual(response.status_code, 401)
        self.assertIn('msg', response.get_json())  # Flask-JWT-Extended returns 'msg' for missing/invalid token
        self.assertEqual(response.get_json()['msg'], 'Missing Authorization Header')

# testing add user route 
class TestAddUser(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Set up the database
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_valid_post_add_user(self):
        """Test valid POST request for adding a new user"""
        response = self.client.post('/add_user', json={
            'Name': 'testuser',
            'Email_address': 'testuser@example.com'
        })
        print("Test valid add user:", response.get_json())  # Print the response message
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'User added successfully')

    def test_duplicate_user_post(self):
        """Test adding a user with an existing email"""
        # First, add a user with a unique username and email
        self.client.post('/add_user', json={
            'Name': 'uniqueuser',  # Use a different name
            'Email_address': 'testuser@example.com'
        })

        # Try adding another user with the same email but a different username
        response = self.client.post('/add_user', json={
            'Name': 'anotheruser',  # Use a different name
            'Email_address': 'testuser@example.com'  # Same email
        })
    
        print("Test duplicate user response:", response.get_json())  # Print the response message
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'This email is already in use, please use a different email')



    def test_invalid_email_format(self):
        """Test adding a user with an invalid email format"""
        response = self.client.post('/add_user', json={
            'Name': 'testuser',
            'Email_address': 'invalid-email'
        })
        print("Test invalid email format:", response.get_json())  # Print the response message
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Invalid email format')

    def test_missing_name(self):
        """Test adding a user without a name"""
        response = self.client.post('/add_user', json={
            'Name': '',
            'Email_address': 'testuser@example.com'
        })
        print("Test missing name:", response.get_json())  # Print the response message
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Missing required fields')

# testing expense api
class TestExpensesAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Set up the database
        with self.app.app_context():
            db.create_all()

            # Create a test user and category for use in tests
            self.test_user = User(user_name='testuser', email='testuser@example.com')
            self.test_category = Category(name='Food')

            db.session.add(self.test_user)
            db.session.add(self.test_category)
            db.session.commit()  # Commit the changes to the database

            # Store the category ID for use in tests
            self.category_id = self.test_category.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_expense(self):
        """Test valid POST request for adding a new expense"""
        response = self.client.post('/add_expense', json={
            'user_name': 'testuser',  # Ensure this user exists
            'amount': 100,
            'description': 'Groceries',
            'date': '2024-10-08T00:00:00',  # Use an appropriate date format
            'Category': self.category_id  # Use the stored category ID
        })

        print("Test add expense response:", response.get_json())  # Print the response for debugging
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Expense added successfully')

    def test_show_expenses(self):
        """Test retrieving expenses for a specific user"""
        # Add an expense for the user
        self.client.post('/add_expense', json={
            'user_name': 'testuser',
            'amount': 100,
            'description': 'Test Expense',
            'date': '2024-10-08T00:00:00',
            'Category': self.category_id  # Use the stored category ID
        })

        # Retrieve expenses for the user
        response = self.client.get('/expenses?user=testuser')

        print("Test show expenses response:", response.get_json())  # Print the response for debugging
        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.get_json())
        self.assertIn('total', response.get_json())
        self.assertIn('expenses', response.get_json())
        self.assertEqual(response.get_json()['user'], 'testuser')
        self.assertEqual(response.get_json()['total'], 100.0)  # Expect total to be the sum of expenses
        self.assertEqual(len(response.get_json()['expenses']), 1)  # Check the number of expenses

    def test_show_expenses_no_user(self):
        """Test retrieving expenses without specifying a user"""
        response = self.client.get('/expenses')
        print("Test show expenses no user response:", response.get_json())  # Print the response for debugging
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'User not specified')

    def test_show_expenses_no_expenses(self):
        """Test retrieving expenses for a user with no expenses"""
        self.client.post('/add_user', json={
            'Name': 'testuser2',
            'Email_address': 'testuser2@example.com'
        })

        response = self.client.get('/expenses?user=testuser2')
        print("Test show expenses no expenses response:", response.get_json())  # Print the response for debugging
        self.assertEqual(response.status_code, 404)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'No expenses found for user testuser2')

class TestModifyExpense(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Set up the database
        with self.app.app_context():
            db.create_all()

            # Create test user and category
            self.test_user = User(user_name='testuser', email='testuser@example.com')
            self.test_category = Category(name='Food')

            db.session.add(self.test_user)
            db.session.add(self.test_category)
            db.session.commit()

            # Add a test expense
            self.test_expense = Expenses(
                amount=50.0,
                description='Initial Expense',
                date=datetime.now(),
                user_id=self.test_user.id,
                category_id=self.test_category.id
            )
            db.session.add(self.test_expense)
            db.session.commit()

            # Ensure the test_expense and test_category are attached to the session
            self.test_expense = db.session.query(Expenses).filter_by(id=self.test_expense.id).first()
            self.test_category = db.session.query(Category).filter_by(id=self.test_category.id).first()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_modify_expense(self):
        """Test modifying an existing expense"""
        with self.app.app_context():
            # Re-query the test_expense to ensure it's attached to the session
            expense = db.session.query(Expenses).filter_by(id=self.test_expense.id).first()

            response = self.client.post('/mod_expense', json={
                'user': 'testuser',
                'id': expense.id,
                'Description': 'Updated Description',
                'Date': '2024-10-08T00:00:00',
                'Amount': 100.0,
                'Category': self.test_category.id  # Use the re-attached category id
            })

            print("Test modify expense response:", response.get_json())  # For debugging
            self.assertEqual(response.status_code, 200)
            self.assertIn('message', response.get_json())
            self.assertEqual(response.get_json()['message'], 'Expense updated successfully')

    def test_delete_expense(self):
        """Test deleting an existing expense"""
        with self.app.app_context():
            # Re-query the test_expense to ensure it's attached to the session
            expense = db.session.query(Expenses).filter_by(id=self.test_expense.id).first()

            response = self.client.post('/mod_expense', json={
                'user': 'testuser',
                'id': expense.id,
                'Delete': True
            })

            print("Test delete expense response:", response.get_json())  # For debugging
            self.assertEqual(response.status_code, 200)
            self.assertIn('message', response.get_json())
            self.assertEqual(response.get_json()['message'], 'Expense deleted successfully')

class TestFilterExpenses(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Set up the database
        with self.app.app_context():
            db.create_all()

            # Create a test category to avoid ForeignKey errors
            self.test_category = Category(name='Food')
            db.session.add(self.test_category)
            db.session.commit()

            # Create a test user and add some expenses
            self.test_user = User(user_name='testuser', email='testuser@example.com')
            password_hash = bcrypt.hashpw('validPassword123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.test_user.password_hash = password_hash  # Set the hashed password
            db.session.add(self.test_user)
            db.session.commit()

            # Add some test expenses
            self.expense1 = Expenses(
                amount=100,
                description='Test Expense 1',
                date=datetime(2024, 10, 1),
                user_id=self.test_user.id,
                category_id=self.test_category.id
            )
            self.expense2 = Expenses(
                amount=150,
                description='Test Expense 2',
                date=datetime(2024, 10, 5),
                user_id=self.test_user.id,
                category_id=self.test_category.id
            )
            db.session.add(self.expense1)
            db.session.add(self.expense2)
            db.session.commit()

            # Log in the user to get JWT
            login_response = self.client.post('/login', json={
                'email': 'testuser@example.com',
                'password': 'validPassword123'  # Ensure this password matches what's set in your user model
            })
            self.access_token = login_response.get_json()['access_token']

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_filter_expenses_by_amount(self):
        print("\nTesting filter by amount...")
        response = self.client.get('/filter_expenses', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, query_string={
            'min_amount': 100,
            'max_amount': 150
        })

        print("Response Status Code:", response.status_code)
        print("Response Data:", response.get_json())  # Debugging print
        self.assertEqual(response.status_code, 200)
        expenses = response.get_json()
        print("Filtered Expenses by Amount:", expenses)  # Debugging print
        self.assertEqual(len(expenses), 2)  # Expect both expenses to match

    def test_filter_expenses_by_date(self):
        print("\nTesting filter by date...")
        response = self.client.get('/filter_expenses', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, query_string={
            'start_date': '2024-10-01',
            'end_date': '2024-10-05'
        })

        print("Response Status Code:", response.status_code)
        print("Response Data:", response.get_json())  # Debugging print
        self.assertEqual(response.status_code, 200)
        expenses = response.get_json()
        print("Filtered Expenses by Date:", expenses)  # Debugging line
        self.assertEqual(len(expenses), 2)  # Expect both expenses in this date range

    def test_filter_expenses_empty(self):
        print("\nTesting filter with no matching expenses...")
        response = self.client.get('/filter_expenses', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, query_string={
            'min_amount': 200  # No expense should match
        })

        print("Response Status Code:", response.status_code)
        print("Response Data:", response.get_json())  # Debugging print
        self.assertEqual(response.status_code, 200)
        expenses = response.get_json()
        print("Filtered Expenses for No Match:", expenses)  # Debugging print
        self.assertEqual(len(expenses), 0)  # Expect no expenses

# testing for viewing profile
class TestUserProfile(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Set up the database
        with self.app.app_context():
            db.create_all()

            # Create a test user
            self.test_user = User(user_name='testuser', email='testuser@example.com')
            password_hash = bcrypt.hashpw('validPassword123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.test_user.password_hash = password_hash
            db.session.add(self.test_user)
            db.session.commit()

            # Log in the user to get JWT
            login_response = self.client.post('/login', json={
                'email': 'testuser@example.com',
                'password': 'validPassword123'
            })
            self.access_token = login_response.get_json()['access_token']

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_view_profile(self):
        # Access the profile route
        response = self.client.get('/profile', headers={
            'Authorization': f'Bearer {self.access_token}'
        })

        print("Profile Response:", response.get_json())  # Debugging print
        self.assertEqual(response.status_code, 200)
        profile_data = response.get_json()
        self.assertEqual(profile_data['user_name'], 'testuser')
        self.assertEqual(profile_data['email'], 'testuser@example.com')
        self.assertIn('created_at', profile_data)  # Ensure the created_at field is included

    def test_unauthorized_access(self):
        # Attempt to access the profile route without a JWT
        response = self.client.get('/profile')

        print("Unauthorized Access Response:", response.get_json())  # Debugging print
        self.assertEqual(response.status_code, 401)
        error_data = response.get_json()
        self.assertIn('msg', error_data)  # Flask-JWT returns 'msg' field for missing tokens
        self.assertEqual(error_data['msg'], 'Missing Authorization Header')

# Testing for editing profile
class TestEditProfile(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Set up the database
        with self.app.app_context():
            db.create_all()

            # Create a test user
            self.test_user = User(user_name='testuser', email='testuser@example.com')
            password_hash = bcrypt.hashpw('validPassword123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.test_user.password_hash = password_hash
            db.session.add(self.test_user)
            db.session.commit()

            # Log in the user to get JWT
            login_response = self.client.post('/login', json={
                'email': 'testuser@example.com',
                'password': 'validPassword123'
            })
            self.access_token = login_response.get_json()['access_token']

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_valid_profile_update(self):
        # Update the profile with valid data
        response = self.client.put('/profile', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, json={
            'user_name': 'updateduser',
            'email': 'updatedemail@example.com'
        })

        print("Valid Update Response:", response.get_json())  # Debugging print

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Profile updated successfully')

        # Ensure the changes were made in the database
        with self.app.app_context():
            updated_user = User.query.get(self.test_user.id)
            self.assertEqual(updated_user.user_name, 'updateduser')
            self.assertEqual(updated_user.email, 'updatedemail@example.com')

    def test_profile_update_with_invalid_email(self):
        # Try to update the profile with an invalid email
        response = self.client.put('/profile', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, json={
            'user_name': 'updateduser',
            'email': 'invalidemail'  # Invalid email format
        })

        print("Invalid Email Response:", response.get_json())  # Debugging print

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())
        self.assertEqual(response.get_json()['error'], 'Invalid email format')

    def test_profile_update_with_existing_username_or_email(self):
        # Create another user to test duplicate username/email
        with self.app.app_context():
            another_user = User(user_name='existinguser', email='existing@example.com')
            db.session.add(another_user)
            db.session.commit()

        # Try to update the profile with an existing username
        response = self.client.put('/profile', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, json={
            'user_name': 'existinguser',  # Existing username
            'email': 'updatedemail@example.com'
        })

        print("Existing Username Response:", response.get_json())  # Debugging print

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())
        self.assertEqual(response.get_json()['error'], 'Username or email already in use')

        # Try to update the profile with an existing email
        response = self.client.put('/profile', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, json={
            'user_name': 'updateduser',
            'email': 'existing@example.com'  # Existing email
        })

        print("Existing Email Response:", response.get_json())  # Debugging print

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())
        self.assertEqual(response.get_json()['error'], 'Username or email already in use')

    def test_profile_update_with_missing_fields(self):
        # Try to update the profile without a username
        response = self.client.put('/profile', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, json={
            'email': 'updatedemail@example.com'
        })

        print("Missing Username Response:", response.get_json())  # Debugging print

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())
        self.assertEqual(response.get_json()['error'], 'Username and email are required')

        # Try to update the profile without an email
        response = self.client.put('/profile', headers={
            'Authorization': f'Bearer {self.access_token}'
        }, json={
            'user_name': 'updateduser'
        })

        print("Missing Email Response:", response.get_json())  # Debugging print

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())
        self.assertEqual(response.get_json()['error'], 'Username and email are required')
        
# Testing for getting notification  
class TestNotifications(unittest.TestCase):
    def setUp(self):
        # Create the Flask app and configure the test client
        self.app = create_app()
        self.app.config.from_object('app.config.TestingConfig')
        self.client = self.app.test_client()

        # Set up the database and create a test user and notifications
        with self.app.app_context():
            db.create_all()

            # Create a test user with a valid password
            self.test_user = User(user_name='testuser', email='testuser@example.com')
            password_hash = bcrypt.hashpw('validPassword123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.test_user.password_hash = password_hash
            db.session.add(self.test_user)
            db.session.commit()

            # Create some test notifications for the user
            self.notification1 = Notification(
                user_id=self.test_user.id,
                message='Notification 1',
                type='Info',
                created_at=datetime(2024, 10, 10, 9, 30, 0),
                is_read=False
            )
            self.notification2 = Notification(
                user_id=self.test_user.id,
                message='Notification 2',
                type='Warning',
                created_at=datetime(2024, 10, 10, 10, 30, 0),
                is_read=True
            )
            db.session.add(self.notification1)
            db.session.add(self.notification2)
            db.session.commit()

            # Log in the user to get a JWT
            self.access_token = create_access_token(identity=self.test_user.id)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_notifications(self):
        """Test retrieving all notifications for the user."""
        response = self.client.get('/notifications', headers={
            'Authorization': f'Bearer {self.access_token}'
        })

        self.assertEqual(response.status_code, 200)
        notifications = response.get_json()

        self.assertEqual(len(notifications), 2)  # Expecting two notifications
        self.assertEqual(notifications[0]['message'], 'Notification 2')  # Ordered by created_at desc
        self.assertEqual(notifications[1]['message'], 'Notification 1')

    def test_empty_notifications(self):
        """Test when the user has no notifications."""
        # Create a new user with no notifications
        with self.app.app_context():
            new_user = User(user_name='newuser', email='newuser@example.com')
            password_hash = bcrypt.hashpw('newPassword123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user.password_hash = password_hash
            db.session.add(new_user)
            db.session.commit()

            # Log in with the new user to get a JWT
            new_access_token = create_access_token(identity=new_user.id)

        response = self.client.get('/notifications', headers={
            'Authorization': f'Bearer {new_access_token}'
        })

        self.assertEqual(response.status_code, 200)
        notifications = response.get_json()
        self.assertEqual(len(notifications), 0)  # No notifications for the new user

    def test_get_notifications_with_no_auth(self):
        """Test accessing the notifications route without a valid JWT."""
        response = self.client.get('/notifications')
        self.assertEqual(response.status_code, 401)
        self.assertIn('msg', response.get_json())  # Flask-JWT returns 'msg' for missing tokens
        self.assertEqual(response.get_json()['msg'], 'Missing Authorization Header')

    def test_unread_notifications(self):
        """Test checking if unread notifications are marked correctly."""
        response = self.client.get('/notifications', headers={
            'Authorization': f'Bearer {self.access_token}'
        })

        self.assertEqual(response.status_code, 200)
        notifications = response.get_json()

        unread_notification = notifications[1]  # Notification 1 should be unread
        self.assertFalse(unread_notification['is_read'])
        
        read_notification = notifications[0]  # Notification 2 should be read
        self.assertTrue(read_notification['is_read'])

    def test_notification_format(self):
        """Test the format of the notifications returned."""
        response = self.client.get('/notifications', headers={
            'Authorization': f'Bearer {self.access_token}'
        })

        self.assertEqual(response.status_code, 200)
        notifications = response.get_json()

        for notification in notifications:
            self.assertIn('id', notification)
            self.assertIn('message', notification)
            self.assertIn('type', notification)
            self.assertIn('created_at', notification)
            self.assertIn('is_read', notification) 
            
class TestMarkNotificationAsRead(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object('app.config.TestingConfig')
        self.client = self.app.test_client()

        # Set up the database
        with self.app.app_context():
            db.create_all()

            # Create a test user
            self.test_user = User(user_name='testuser', email='testuser@example.com')
            password_hash = bcrypt.hashpw('validPassword123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.test_user.password_hash = password_hash
            db.session.add(self.test_user)
            db.session.commit()

            # Create test notifications for this user
            self.notification1 = Notification(
                user_id=self.test_user.id,
                message='Test notification 1',
                type='info',
                is_read=False
            )
            self.notification2 = Notification(
                user_id=self.test_user.id,
                message='Test notification 2',
                type='warning',
                is_read=False
            )
            db.session.add(self.notification1)
            db.session.add(self.notification2)
            db.session.commit()

            # Log in the user to get JWT
            login_response = self.client.post('/login', json={
                'email': 'testuser@example.com',
                'password': 'validPassword123'
            })
            self.access_token = login_response.get_json()['access_token']

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_mark_notification_as_read(self):
        """Test marking a notification as read by the correct user."""
        with self.app.app_context():
            notification1 = Notification.query.get(self.notification1.id)  # Fetch notification

        response = self.client.patch(f'/notifications/{notification1.id}/read', headers={
            'Authorization': f'Bearer {self.access_token}'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Notification marked as read')

        # Verify that the notification is marked as read in the database
        with self.app.app_context():
            updated_notification = Notification.query.get(notification1.id)
            self.assertTrue(updated_notification.is_read)

    def test_mark_notification_as_read_without_auth(self):
        """Test trying to mark a notification as read without authentication."""
        with self.app.app_context():
            notification1 = Notification.query.get(self.notification1.id)  # Re-fetch notification
        
        response = self.client.patch(f'/notifications/{notification1.id}/read')
        self.assertEqual(response.status_code, 401)  # Should return unauthorized error

    def test_mark_other_users_notification_as_read(self):
        """Test marking another user's notification as read."""
        # Create another user and notification
        with self.app.app_context():
            another_user = User(user_name='otheruser', email='otheruser@example.com')
            password_hash = bcrypt.hashpw('validPassword123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            another_user.password_hash = password_hash
            db.session.add(another_user)
            db.session.commit()

            # Create a notification for the other user
            notification_for_other_user = Notification(
                user_id=another_user.id,
                message='Test notification for another user',
                type='info',
                is_read=False
            )
            db.session.add(notification_for_other_user)
            db.session.commit()

        with self.app.app_context():
            response = self.client.patch(f'/notifications/{notification_for_other_user.id}/read', headers={
                'Authorization': f'Bearer {self.access_token}'
            })

            self.assertEqual(response.status_code, 404)  # Should return not found error for unauthorized access


if __name__ == '__main__':
    unittest.main()
