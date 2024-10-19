---

# API Usage Guide

This document provides examples of how to use the Expense Tracker API. You can interact with the API using tools such as **curl** or **Postman**. All endpoints expect and return **JSON** data.

## Table of Contents

- [Authentication](#authentication)
  - [Register](#register)
  - [Login](#login)
  - [Logout](#logout)
- [Expense Management](#expense-management)
  - [Add Expense](#add-expense)
  - [View Expenses](#view-expenses)
  - [Modify Expense](#modify-expense)
  - [Filter Expenses](#filter-expenses)
  - [Export Expenses](#export-expenses)
- [Notifications](#notifications)
  - [View Notifications](#view-notifications)
  - [Mark Notification as Read](#mark-notification-as-read)
  - [Delete Notification](#delete-notification)

---

## Authentication

### Register

Register a new user by sending a POST request to the `/register` endpoint with user details.

**Endpoint**: `POST /register`

**Request Body**:

```json
{
  "user_name": "newuser",
  "email": "newuser@example.com",
  "password": "newpassword"
}
```

**Curl Example**:

```bash
curl -X POST http://127.0.0.1:5000/register \
-H "Content-Type: application/json" \
-d '{"user_name": "newuser", "email": "newuser@example.com", "password": "newpassword"}'
```

---

### Login

Login with your credentials to receive a JWT token.

**Endpoint**: `POST /login`

**Request Body**:

```json
{
  "email": "newuser@example.com",
  "password": "newpassword"
}
```

**Curl Example**:

```bash
curl -X POST http://127.0.0.1:5000/login \
-H "Content-Type: application/json" \
-d '{"email": "newuser@example.com", "password": "newpassword"}'
```

**Response**:

```json
{
  "access_token": "<jwt_token>"
}
```

You will receive a JWT token that needs to be included in the Authorization header for accessing protected routes.

---

### Logout

Log out by invalidating the JWT token.

**Endpoint**: `POST /logout`

**Headers**:

```http
Authorization: Bearer <jwt_token>
```

**Curl Example**:

```bash
curl -X POST http://127.0.0.1:5000/logout \
-H "Authorization: Bearer <jwt_token>"
```

---

## Expense Management

### Add Expense

To add a new expense, you need to send a POST request with the expense details. Make sure you are authenticated.

**Endpoint**: `POST /add_expense`

**Request Body**:

```json
{
  "user_name": "newuser",
  "amount": 150.00,
  "description": "Groceries",
  "date": "2024-10-10T12:00:00",
  "Category": 1
}
```

**Headers**:

```http
Authorization: Bearer <jwt_token>
```

**Curl Example**:

```bash
curl -X POST http://127.0.0.1:5000/add_expense \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <jwt_token>" \
-d '{"user_name": "newuser", "amount": 150.00, "description": "Groceries", "date": "2024-10-10T12:00:00", "Category": 1}'
```

---

### View Expenses

Retrieve all expenses for a specific user.

**Endpoint**: `GET /expenses`

**Query Parameters**:

- `user`: The username of the user whose expenses you want to view.

**Curl Example**:

```bash
curl -X GET "http://127.0.0.1:5000/expenses?user=newuser"
```

**Response**:

```json
{
  "user": "newuser",
  "total": 150.0,
  "expenses": [
    {
      "id": 1,
      "amount": 150.0,
      "description": "Groceries"
    }
  ]
}
```

---

### Modify Expense

Update or delete an existing expense. Include the `id` of the expense to be modified.

**Endpoint**: `POST /mod_expense`

**Request Body**:

```json
{
  "user": "newuser",
  "id": 1,
  "Description": "New Groceries",
  "Amount": 180.00,
  "Date": "2024-10-11T12:00:00"
}
```

**Curl Example**:

```bash
curl -X POST http://127.0.0.1:5000/mod_expense \
-H "Content-Type: application/json" \
-d '{"user": "newuser", "id": 1, "Description": "New Groceries", "Amount": 180.00, "Date": "2024-10-11T12:00:00"}'
```

---

### Filter Expenses

Filter expenses based on amount, date, or sorting order.

**Endpoint**: `GET /filter_expenses`

**Query Parameters**:

- `min_amount`: Minimum expense amount
- `max_amount`: Maximum expense amount
- `start_date`: Start date for filtering expenses
- `end_date`: End date for filtering expenses
- `sort_by`: Field to sort by (default: `date`)
- `order`: Sorting order (`asc` or `desc`)

**Curl Example**:

```bash
curl -X GET "http://127.0.0.1:5000/filter_expenses?min_amount=50&max_amount=200&start_date=2024-01-01&end_date=2024-12-31" \
-H "Authorization: Bearer <jwt_token>"
```

---

### Export Expenses

Export all expenses to CSV or PDF.

#### Export to CSV

**Endpoint**: `GET /export/csv`

**Curl Example**:

```bash
curl -X GET http://127.0.0.1:5000/export/csv \
-H "Authorization: Bearer <jwt_token>"
```

#### Export to PDF

**Endpoint**: `GET /export/pdf`

**Curl Example**:

```bash
curl -X GET http://127.0.0.1:5000/export/pdf \
-H "Authorization: Bearer <jwt_token>"
```

---

## Notifications

### View Notifications

Retrieve all notifications for the current user.

**Endpoint**: `GET /notifications`

**Headers**:

```http
Authorization: Bearer <jwt_token>
```

**Curl Example**:

```bash
curl -X GET http://127.0.0.1:5000/notifications \
-H "Authorization: Bearer <jwt_token>"
```

---

### Mark Notification as Read

Mark a specific notification as read.

**Endpoint**: `PATCH /notifications/:id/read`

**Curl Example**:

```bash
curl -X PATCH http://127.0.0.1:5000/notifications/1/read \
-H "Authorization: Bearer <jwt_token>"
```

---

### Delete Notification

Delete a specific notification.

**Endpoint**: `DELETE /notifications/:id`

**Curl Example**:

```bash
curl -X DELETE http://127.0.0.1:5000/notifications/1 \
-H "Authorization: Bearer <jwt_token>"
```

---