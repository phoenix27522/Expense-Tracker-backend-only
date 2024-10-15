### Architecture Documentation

```markdown
# Project Architecture

This document provides an overview of the architecture of the Expense Tracker API. It explains the structure of the codebase, how different components interact with each other, and the design principles followed in this project.

---

## 1. Overview

The Expense Tracker API is built using **Flask** (a Python web framework) and **SQLAlchemy** (an ORM for database interaction). The system is designed to allow users to track their expenses, manage recurring expenses, and receive notifications. The core architectural components include:

- **Flask** as the web framework.
- **SQLAlchemy** as the ORM for database management.
- **JWT Authentication** for secure access control.
- **Modular Codebase**: Separation of concerns into different components (e.g., models, routes, utilities).
- **Database**: SQLite (or other SQL-based databases in production) to store users, expenses, recurring expenses, categories, and notifications.

---

## 2. Directory Structure

The project follows a typical Flask application structure. Below is the general layout:

```
expense-tracker/
│
├── app/                          # Main application package
│   ├── __init__.py               # Application factory and app configuration
│   ├── models.py                 # Database models (User, Expenses, RecurringExpense, etc.)
│   ├── routes.py                 # API routes (user management, expense management, etc.)
│   ├── utils.py                  # Utility functions (e.g., user authentication helpers)
│   ├── config.py                 # Configuration for different environments (development, testing, production)
│   ├── tests/                    # Test cases for the application
│
├── migrations/                   # Database migration scripts (if using Flask-Migrate)
│
├── .env                          # Environment variable file (for development)
├── requirements.txt              # Project dependencies
├── run.py                        # Entry point for the application
├── README.md                     # General project overview and setup instructions
└── docs/                         # Documentation folder
    ├── API_Documentation.md      # API documentation
    ├── Installation_Guide.md     # Setup and installation guide
    ├── Architecture.md           # Architecture documentation (this file)
    └── ...
```

---

## 3. Core Components

### 3.1 **Flask Application Factory**

The application uses the **Flask Application Factory** pattern, which allows for flexible configuration and easy setup for different environments (development, testing, production). This pattern ensures that the app instance can be created dynamically as needed.

- **File:** `app/__init__.py`
- **Purpose:** Sets up the Flask app, initializes extensions (e.g., SQLAlchemy, JWTManager), and registers blueprints for routes.

```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app
```

### 3.2 **Models (Database Layer)**

The database models are defined using **SQLAlchemy**, which allows the application to interact with an SQL database using Python objects. The main models include:

- **User**: Represents the registered users of the system.
- **Expenses**: Represents individual expense records.
- **RecurringExpense**: Represents expenses that recur over time (e.g., monthly subscriptions).
- **Category**: Represents expense categories (e.g., Food, Rent).
- **Notification**: Represents notifications sent to users (e.g., reminders, alerts).

- **File:** `app/models.py`
- **Purpose:** Defines the structure and relationships of the database entities.

#### Model Relationships:
- **User** has a one-to-many relationship with **Expenses**, **RecurringExpense**, and **Notifications**.
- **Expenses** and **RecurringExpense** are related to **Category** via a foreign key.
  
**Example:**
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    expenses = db.relationship('Expenses', back_populates='user')

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='expenses')
```

### 3.3 **Routes (API Layer)**

The routes handle HTTP requests and map them to corresponding business logic (e.g., user registration, adding expenses, fetching notifications). Each route is associated with a specific HTTP method (e.g., `GET`, `POST`) and interacts with the database models to handle incoming requests.

- **File:** `app/routes.py`
- **Purpose:** Defines all the API endpoints for user management, expense management, notifications, and other features.

**Example Endpoints:**
- `/register`: Register a new user.
- `/login`: Log in and receive a JWT token.
- `/add_expense`: Add a new expense for a user.
- `/notifications`: Get notifications for a user.

### 3.4 **Authentication (JWT-Based)**

The application uses **JSON Web Tokens (JWT)** for authentication. JWT is used to secure endpoints that require user authentication, such as adding expenses or viewing notifications. After logging in, users receive a JWT token that must be included in the `Authorization` header for protected requests.

- **File:** `app/routes.py` (JWT integration)
- **Library:** `flask_jwt_extended` (for JWT management)
  
**Example JWT Flow:**
1. A user logs in and receives a JWT token.
2. The token is included in the `Authorization` header when making requests to protected routes.
3. The server verifies the token before processing the request.

```python
@main.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()  # Retrieves user identity from the JWT
    return jsonify({'message': f'Welcome, user {current_user}'})
```

---

## 4. Database Structure

### Tables and Relationships

The following tables are present in the database:

- **User Table**: Stores user data (ID, email, password, etc.).
- **Expenses Table**: Stores individual expenses, linked to a user and a category.
- **RecurringExpense Table**: Stores recurring expenses, also linked to a user and a category.
- **Category Table**: Stores categories that group expenses (e.g., Food, Rent).
- **Notification Table**: Stores notifications related to users.

### Entity Relationship Diagram (ERD)

Below is a high-level overview of the relationships between the core entities:

```
User
  |
  +---> Expenses
  |
  +---> RecurringExpense
  |
  +---> Notifications
         |
         +---> Category
```

---

## 5. Key Design Principles

### 5.1 **Separation of Concerns**

- **Models**: Handle the definition and interaction with the database.
- **Routes**: Handle API requests and responses, providing the bridge between the frontend and backend.
- **Utilities**: Contain reusable functions such as user authentication helpers, data validation, etc.

### 5.2 **Modularity and Reusability**

- The project follows a modular approach where components such as routes, models, and utilities are separated to ensure reusability and maintainability.

### 5.3 **Security**

- **JWT Authentication**: Ensures that only authenticated users can access protected routes.
- **Input Validation**: All input data is validated to prevent SQL injection, cross-site scripting (XSS), and other security vulnerabilities.

### 5.4 **Scalability**

- The app uses Flask's blueprints, which allows for future scalability by easily adding more modules, routes, and features.

---

## 6. Future Improvements

- **Caching**: Implement caching mechanisms to optimize performance, especially for frequently accessed routes (e.g., fetching expenses or notifications).
- **Rate Limiting**: Add rate-limiting features to protect the API from abuse.
- **Pagination**: Implement pagination for endpoints that return large datasets, such as the `/expenses` endpoint.

---

## Conclusion

The Expense Tracker API is built with a focus on modularity, security, and scalability. It leverages Flask and SQLAlchemy to provide a robust backend for managing user expenses, recurring expenses, and notifications. The architecture ensures that the codebase is easy to maintain and extend as the application grows.
```

---

### Explanation of Key Sections:

1. **Overview**: Gives a high-level understanding of the project's purpose and the technology stack used.
2. **Directory Structure**: Shows how the codebase is organized.
3. **Core Components**: Explains the key components of the architecture, such as models, routes, authentication, etc.
4. **Database Structure**: Describes the tables and their relationships, which is essential for understanding how data is stored.
5. **Key Design Principles**: Highlights the best practices followed in the project, such as separation of concerns and modularity.
6. **Future Improvements**: Suggests areas where the architecture can be improved over time.

---

