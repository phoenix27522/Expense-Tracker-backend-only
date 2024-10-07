import unittest
import json
from app.config import TestingConfig
from app import create_app, db
from app.models import User

class TestUserRegistration(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()

        # Sets up the database for testing
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
        print(response.get_json())  # changing get_json() instead of json() to aviod conflict
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
        print(response.get_json())  # changing get_json() instead of json() to aviod conflict
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'User already exists')

    def test_invalid_email_format(self):
        response = self.client.post('/register', json={
            "user_name": "testuser",
            "email": "invalid-email-format",
            "password": "validPassword123"
        })
        print(response.get_json())  #  changing get_json() instead of json() to aviod conflict
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Invalid email format')

    def test_short_password(self):
        response = self.client.post('/register', json={
            "user_name": "testuser",
            "email": "testuser@example.com",
            "password": "short"
        })
        print(response.get_json())  # changing get_json() instead of json() to aviod conflict
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.get_json())
        self.assertEqual(response.get_json()['message'], 'Password too short, must be at least 6 characters')

if __name__ == '__main__':
    unittest.main()
