import unittest
from app.config import TestingConfig
from app import create_app, db
from app.models import User
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

if __name__ == '__main__':
    unittest.main()
