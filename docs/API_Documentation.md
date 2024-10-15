### Comprehensive Documentation of API Endpoints

This document provides a detailed description of all the API endpoints in the provided `routes.py` file. It includes information about request methods, authentication requirements, input parameters, and response formats.

---

### **1. `/register` - Register a New User**
- **Method:** `POST`
- **Authentication:** None
- **Description:** Registers a new user in the system by providing a username, email, and password.
- **Request Body (JSON):**
  ```json
  {
    "user_name": "string",  // Required
    "email": "string",      // Required, must be a valid email format
    "password": "string"    // Required, must be at least 6 characters
  }
  ```
- **Responses:**
  - **201 Created:**
    ```json
    {
      "message": "User registered successfully"
    }
    ```
  - **400 Bad Request:** Missing fields or validation errors.
    ```json
    {
      "message": "Validation error message"
    }
    ```

---

### **2. `/login` - User Login**
- **Method:** `POST`
- **Authentication:** None
- **Description:** Authenticates a user by verifying email and password, and returns a JWT access token.
- **Request Body (JSON):**
  ```json
  {
    "email": "string",      // Required, valid email format
    "password": "string"    // Required, must be the correct password for the given email
  }
  ```
- **Responses:**
  - **200 OK:**
    ```json
    {
      "access_token": "string"  // JWT access token
    }
    ```
  - **401 Unauthorized:** Invalid credentials.
    ```json
    {
      "message": "Invalid credentials"
    }
    ```
  - **400 Bad Request:** Missing fields or validation errors.
    ```json
    {
      "message": "Missing required fields"
    }
    ```

---

### **3. `/logout` - User Logout**
- **Method:** `POST`
- **Authentication:** JWT required
- **Description:** Logs out a user by invalidating the JWT token.
- **Responses:**
  - **200 OK:**
    ```json
    {
      "message": "Successfully logged out"
    }
    ```

---

### **4. `/protected` - Access Protected Route**
- **Method:** `GET`
- **Authentication:** JWT required
- **Description:** Demonstrates access to a protected route. Returns a welcome message for authenticated users.
- **Responses:**
  - **200 OK:**
    ```json
    {
      "message": "Welcome, user {user_id}"
    }
    ```

---

### **5. `/add_user` - Add a New User**
- **Method:** `POST`
- **Authentication:** None
- **Description:** Adds a new user with basic information such as name and email.
- **Request Body (JSON):**
  ```json
  {
    "Name": "string",             // Required
    "Email_address": "string"     // Required, valid email format
  }
  ```
- **Responses:**
  - **201 Created:**
    ```json
    {
      "message": "User added successfully"
    }
    ```
  - **400 Bad Request:** User already exists or validation error.
    ```json
    {
      "message": "Validation error message"
    }
    ```

---

### **6. `/add_expense` - Add a New Expense**
- **Method:** `POST`
- **Authentication:** None
- **Description:** Adds a new expense for the specified user.
- **Request Body (JSON):**
  ```json
  {
    "user_name": "string",   // Required, username of the user
    "amount": "float",       // Required, amount of the expense
    "description": "string", // Required, description of the expense
    "date": "string",        // Required, purchase date in ISO format (YYYY-MM-DDTHH:MM:SS)
    "Category": "int"        // Required, category ID of the expense
  }
  ```
- **Responses:**
  - **201 Created:**
    ```json
    {
      "message": "Expense added successfully"
    }
    ```
  - **400 Bad Request:** Missing or invalid data.
    ```json
    {
      "message": "Validation error message"
    }
    ```

---

### **7. `/expenses` - Show Expenses**
- **Method:** `GET`
- **Authentication:** None
- **Description:** Retrieves all expenses for the specified user.
- **Query Parameters:**
  - `user` (string): The username of the user whose expenses you want to retrieve.
- **Responses:**
  - **200 OK:**
    ```json
    {
      "user": "string",    // Username
      "total": float,      // Total amount of expenses
      "expenses": [
        {
          "id": int,           // Expense ID
          "amount": float,     // Expense amount
          "description": "string" // Expense description
        },
        // Additional expense objects...
      ]
    }
    ```
  - **404 Not Found:** No expenses found for the user.
    ```json
    {
      "message": "No expenses found for user {user}"
    }
    ```

---

### **8. `/mod_expense` - Modify/Delete an Expense**
- **Method:** `POST`
- **Authentication:** None
- **Description:** Modifies or deletes an expense based on the provided data.
- **Request Body (JSON):**
  ```json
  {
    "user": "string",       // Required, username of the user
    "id": int,              // Required, ID of the expense
    "Description": "string",// Optional, new description
    "Date": "string",       // Optional, new purchase date (ISO format)
    "Amount": float,        // Optional, new amount
    "Category": int,        // Optional, new category ID
    "Delete": bool          // Optional, set to true to delete the expense
  }
  ```
- **Responses:**
  - **200 OK:**
    ```json
    {
      "message": "Expense updated successfully" // or "Expense deleted successfully"
    }
    ```
  - **404 Not Found:** Expense not found.
    ```json
    {
      "message": "Expense not found"
    }
    ```

---

### **9. `/filter_expenses` - Filter Expenses**
- **Method:** `GET`
- **Authentication:** JWT required
- **Description:** Filters expenses based on parameters like amount and date range.
- **Query Parameters:**
  - `min_amount` (float): Minimum amount of the expenses to filter.
  - `max_amount` (float): Maximum amount of the expenses to filter.
  - `start_date` (string): Start date in ISO format (YYYY-MM-DD).
  - `end_date` (string): End date in ISO format (YYYY-MM-DD).
  - `sort_by` (string): Field to sort by (default: `date`).
  - `order` (string): Sorting order (`asc` or `desc`).
- **Responses:**
  - **200 OK:**
    ```json
    [
      {
        "id": int,              // Expense ID
        "amount": float,        // Expense amount
        "description": "string",// Description
        "date": "string",       // Date in YYYY-MM-DD format
        "user_id": int,         // User ID
        "category_id": int      // Category ID
      },
      // Additional expense objects...
    ]
    ```

---

### **10. `/profile` - View Profile**
- **Method:** `GET`
- **Authentication:** JWT required
- **Description:** Retrieves the profile information of the authenticated user.
- **Responses:**
  - **200 OK:**
    ```json
    {
      "user_name": "string",   // Username
      "email": "string",       // Email address
      "created_at": "string"   // Account creation date (ISO format)
    }
    ```
  - **404 Not Found:** User not found.
    ```json
    {
      "error": "User not found"
    }
    ```

---

### **11. `/profile` - Edit Profile**
- **Method:** `PUT`
- **Authentication:** JWT required
- **Description:** Updates the profile information of the authenticated user.
- **Request Body (JSON):**
  ```json
  {
    "user_name": "string",  // Required, new username
    "email": "string"       // Required, new email address
  }
  ```
- **Responses:**
  - **200 OK:**
    ```json
    {
      "message": "Profile updated successfully"
    }
    ```
  - **400 Bad Request:** Validation errors or username/email already exists.
    ```json
    {
      "error": "Validation error message"
    }
    ```

---

### **12. `/notifications` - Get Notifications**
- **Method:** `GET`
- **Authentication:** JWT required
- **Description:** Retrieves all notifications for the authenticated user.
- **Responses:**
  - **200 OK:**
    ```json
    [
      {
        "id": int,             // Notification ID
        "message": "string",   // Notification message
        "type": "string",      // Notification type
        "created_at": "string",// Date created (YYYY-MM-DD HH:MM:SS)
        "is

_read": bool        // Whether the notification is read
      },
      // Additional notification objects...
    ]
    ```

---

### **13. `/notifications/<int:id>/read` - Mark Notification as Read**
- **Method:** `PATCH`
- **Authentication:** JWT required
- **Description:** Marks a specific notification as read for the authenticated user.
- **Path Parameter:**
  - `id` (int): The ID of the notification.
- **Responses:**
  - **200 OK:**
    ```json
    {
      "message": "Notification marked as read"
    }
    ```
  - **404 Not Found:** Notification not found.
    ```json
    {
      "error": "Notification not found"
    }
    ```

---

### **14. `/notifications/<int:id>` - Delete Notification**
- **Method:** `DELETE`
- **Authentication:** JWT required
- **Description:** Deletes a specific notification for the authenticated user.
- **Path Parameter:**
  - `id` (int): The ID of the notification.
- **Responses:**
  - **200 OK:**
    ```json
    {
      "message": "Notification deleted successfully"
    }
    ```
  - **404 Not Found:** Notification not found.
    ```json
    {
      "error": "Notification not found"
    }
    ```

---

### **15. `/export/csv` - Export Expenses as CSV**
- **Method:** `GET`
- **Authentication:** JWT required
- **Description:** Exports all expenses for the authenticated user as a CSV file.
- **Responses:**
  - **200 OK:** Returns a CSV file with the expenses.
    - Headers:
      ```
      Content-Disposition: attachment; filename=expenses.csv
      Content-Type: text/csv
      ```

---

### **16. `/export/pdf` - Export Expenses as PDF**
- **Method:** `GET`
- **Authentication:** JWT required
- **Description:** Exports all expenses for the authenticated user as a PDF file.
- **Responses:**
  - **200 OK:** Returns a PDF file with the expenses.
    - Headers:
      ```
      Content-Disposition: attachment; filename=expenses.pdf
      Content-Type: application/pdf
      ```

---
