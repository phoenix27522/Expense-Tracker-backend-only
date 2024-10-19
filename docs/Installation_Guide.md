---

# Installation Guide

This document provides step-by-step instructions for installing and setting up the Expense Tracker API on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8+**: The application is written in Python, so you'll need Python 3.8 or higher.
- **SQLite**: The project uses SQLite as the default database for development.
- **Git**: For cloning the repository.

---

## Steps to Install

### 1. Clone the Repository

Start by cloning the project repository from GitHub:

```bash
git clone https://github.com/phoenix27522/Expense-Tracker-backend-only.git
```

Navigate into the project directory:

```bash
cd Expense-Tracker-backend-only
```

### 2. Set Up a Virtual Environment

It is recommended to use a virtual environment to manage the project dependencies. Create and activate a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

After activating your virtual environment, install the required Python dependencies by running:

```bash
pip install -r requirements.txt
```

This command installs all the necessary packages such as Flask, SQLAlchemy, JWT, and others as defined in the `requirements.txt` file.

### 4. Configure Environment Variables

You need to set up environment variables for the project. Create a `.env` file in the root directory of the project with the following content:

```env
FLASK_ENV=development
SECRET_KEY=<your_secret_key>
JWT_SECRET_KEY=<your_jwt_secret_key>
DATABASE_URL=sqlite:///expenses.db
```

Replace `<your_secret_key>` and `<your_jwt_secret_key>` with your own secure keys.

### 5. Set Up the Database

To set up the SQLite database and apply migrations, run the following command:

```bash
flask db upgrade
```

This command will create the necessary tables and structure in the `expenses.db` database.

### 6. Run the Application

You can now start the Flask development server:

```bash
flask run
```

The server will be running at `http://127.0.0.1:5000`.

---

## Additional Tools

### Using Postman or Curl

Once the server is running, you can test the API using tools like **Postman** or **curl**. For detailed API usage examples, refer to the `API_Usage.md` file.

### Swagger UI

If you included the optional `swagger.yaml` file, you can load it into Swagger UI or Postman to visualize and interact with the API documentation.

---

## Common Issues

- **Virtual Environment Not Activated**: Ensure you have activated the virtual environment before running any Python commands.
- **Missing Migrations**: If you encounter migration issues, you might need to run `flask db migrate` before applying the migrations with `flask db upgrade`.

---

This guide should get you up and running with the Expense Tracker API in no time. If you encounter any issues, consult the `Troubleshooting` section in the `docs/` folder.

---