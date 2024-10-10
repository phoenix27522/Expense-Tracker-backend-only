from datetime import datetime
import unittest
from app.config import TestingConfig
from app import create_app, db
from app.models import Category, User, Expenses
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

if __name__ == '__main__':
    unittest.main()

