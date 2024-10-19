---

# Testing Guide

This guide outlines the testing strategy for the Expense Tracker API, including how to set up, run, and write tests. The project uses the **`unittest`** framework for testing, and all tests are located in the `tests/` directory.

## Table of Contents

- [Setting Up Tests](#setting-up-tests)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
  - [Test Structure](#test-structure)
  - [Sample Test Case](#sample-test-case)
- [Test Coverage](#test-coverage)
- [Common Issues](#common-issues)

---

## Setting Up Tests

Before running tests, ensure the following:

1. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

2. **Install test dependencies**: All testing dependencies should already be installed via `requirements.txt`. If not, install them manually:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the test database**: The `TestingConfig` in your `config.py` file should be configured to use an in-memory SQLite database for testing. Make sure your environment is correctly set up by checking that `TESTING=True` is enabled in your `.env` file or configuration settings.

---

## Running Tests

You can run all tests by navigating to the project root directory and using the following command:

```bash
python -m unittest discover -s tests
```

This will automatically discover and run all test files in the `tests/` directory.

### Running a Specific Test

To run a specific test case or module:

```bash
python -m unittest tests.test_user.UserModelTestCase
```

Where `test_user.py` is the test file and `UserModelTestCase` is the test case class.

### Verbose Mode

For more detailed output, you can run the tests in verbose mode:

```bash
python -m unittest discover -v
```

---

## Writing Tests

### Test Structure

Tests are organized into separate files based on the functionality being tested. Each test file should have the following structure:

- **Setup**: Prepare the necessary resources (e.g., initialize the test database, create mock data).
- **Test cases**: Individual tests should focus on one piece of functionality, checking both valid and invalid cases.
- **Tear down**: Clean up resources after the test runs.

### Writing a New Test

1. Create a new file in the `tests/` directory named according to the feature being tested. For example, if you're writing tests for the `Expenses` model, create `test_expenses.py`.

2. Create a test class that inherits from `unittest.TestCase`. Within this class, write test methods to check each feature.

3. Use assertions to verify the expected outcome.

### Sample Test Case

Here is a simple example of how to write a test case for user registration:

```python
import unittest
from app import create_app, db
from app.models import User

class UserModelTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up the test database and create the test app"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        """Test user registration with valid data"""
        user = User(user_name='testuser', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        
        # Check if user was successfully added
        self.assertEqual(User.query.count(), 1)
        self.assertTrue(user.check_password('testpassword'))

if __name__ == '__main__':
    unittest.main()
```

### Key Functions:
- `setUp()`: Initializes the app context and test database before each test.
- `tearDown()`: Cleans up the database and app context after each test.
- `self.assertEqual()`, `self.assertTrue()`: Assertion methods to verify test outcomes.

---

## Test Coverage

To check the test coverage of your project, you can use the `coverage` library. First, install `coverage` if you haven't already:

```bash
pip install coverage
```

Then, run your tests with coverage:

```bash
coverage run -m unittest discover
```

After running the tests, generate a coverage report:

```bash
coverage report
```

You can also generate an HTML report:

```bash
coverage html
```

This will create an `htmlcov/` directory with detailed reports on the coverage of each file.

---

## Common Issues

1. **Database Not Found**: Ensure that the `TESTING=True` configuration is set and that the database is being created in memory.
   
2. **Circular Imports**: If you experience circular import issues, try importing models and utility functions inside your test functions rather than at the top of the file.

3. **Tests Failing Locally**: Make sure the environment is correctly set up (e.g., virtual environment activated, test database created). If issues persist, rerun migrations or recreate the test database.

---

By following this guide, you'll be able to write effective and meaningful tests for the Expense Tracker API. Make sure to always run tests before submitting a pull request to ensure everything is functioning as expected.

---