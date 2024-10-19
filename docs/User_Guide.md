---

# User Guide

Welcome to the Expense Tracker API! This guide will walk you through how to use the API to manage your expenses, view reports, and receive notifications.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Creating an Account](#creating-an-account)
  - [Logging In](#logging-in)
  - [Logging Out](#logging-out)
- [Managing Expenses](#managing-expenses)
  - [Adding a New Expense](#adding-a-new-expense)
  - [Viewing Your Expenses](#viewing-your-expenses)
  - [Modifying an Expense](#modifying-an-expense)
  - [Deleting an Expense](#deleting-an-expense)
- [Recurring Expenses](#recurring-expenses)
- [Notifications](#notifications)
- [Exporting Data](#exporting-data)
  - [Export as CSV](#export-as-csv)
  - [Export as PDF](#export-as-pdf)
- [FAQs](#faqs)

---

## Overview

The Expense Tracker API allows you to track your expenses, categorize them, and manage recurring expenses. You can also receive notifications about important events like large expenses and export your data as CSV or PDF.

---

## Getting Started

### Creating an Account

Before you can use the Expense Tracker API, you need to create an account.

1. **Endpoint**: `POST /register`
2. **Required Data**: 
   - Username
   - Email address
   - Password

Here’s an example of the data you need to provide when creating your account:

```json
{
  "user_name": "yourusername",
  "email": "youremail@example.com",
  "password": "yourpassword"
}
```

### Logging In

After registering, you can log in to receive an authentication token (JWT), which you’ll need to access protected features like adding and viewing expenses.

1. **Endpoint**: `POST /login`
2. **Required Data**:
   - Email
   - Password

Example:

```json
{
  "email": "youremail@example.com",
  "password": "yourpassword"
}
```

You will receive a token in the response. This token must be included in all further requests for authentication.

### Logging Out

To log out and invalidate your authentication token:

1. **Endpoint**: `POST /logout`
2. **Headers**: 
   - Authorization: `Bearer <your_token>`

---

## Managing Expenses

### Adding a New Expense

To add a new expense, you need to be logged in and provide details about the expense.

1. **Endpoint**: `POST /add_expense`
2. **Required Data**:
   - Amount
   - Description
   - Date of the expense
   - Category ID (you can view all categories with a separate request)

Example:

```json
{
  "user_name": "yourusername",
  "amount": 50.00,
  "description": "Grocery shopping",
  "date": "2024-10-15T14:00:00",
  "Category": 1
}
```

### Viewing Your Expenses

You can retrieve all your expenses with a simple request.

1. **Endpoint**: `GET /expenses`
2. **Query Parameters**: 
   - `user`: Your username

Example:

```bash
curl -X GET "http://127.0.0.1:5000/expenses?user=yourusername"
```

### Modifying an Expense

To modify an existing expense, provide the expense ID and the fields you wish to change.

1. **Endpoint**: `POST /mod_expense`
2. **Required Data**: 
   - Expense ID
   - Updated fields (e.g., amount, description, date)

Example:

```json
{
  "user": "yourusername",
  "id": 1,
  "Amount": 55.00,
  "Description": "Updated grocery shopping",
  "Date": "2024-10-16T14:00:00"
}
```

### Deleting an Expense

To delete an expense, specify the expense ID and mark it for deletion.

1. **Endpoint**: `POST /mod_expense`
2. **Required Data**:
   - Expense ID
   - Delete flag

Example:

```json
{
  "user": "yourusername",
  "id": 1,
  "Delete": true
}
```

---

## Recurring Expenses

You can set up recurring expenses that automatically get added on a regular schedule (e.g., daily, weekly, monthly).

1. **Endpoint**: `POST /add_expense`
2. **Required Data**:
   - Amount
   - Description
   - Recurrence (e.g., `daily`, `weekly`, `monthly`)
   - Start date and end date

Example:

```json
{
  "user_name": "yourusername",
  "amount": 100.00,
  "description": "Monthly subscription",
  "recurrence": "monthly",
  "start_date": "2024-10-01T00:00:00",
  "end_date": "2025-10-01T00:00:00",
  "Category": 2
}
```

---

## Notifications

The API will send you notifications for certain events, such as large expenses.

### Viewing Notifications

To view your notifications:

1. **Endpoint**: `GET /notifications`
2. **Headers**: 
   - Authorization: `Bearer <your_token>`

### Mark a Notification as Read

You can mark notifications as read:

1. **Endpoint**: `PATCH /notifications/:id/read`
2. **Headers**: 
   - Authorization: `Bearer <your_token>`

### Deleting a Notification

To delete a notification:

1. **Endpoint**: `DELETE /notifications/:id`
2. **Headers**: 
   - Authorization: `Bearer <your_token>`

---

## Exporting Data

You can export your expenses data as either CSV or PDF.

### Export as CSV

1. **Endpoint**: `GET /export/csv`
2. **Headers**: 
   - Authorization: `Bearer <your_token>`

The response will download a CSV file of your expenses.

### Export as PDF

1. **Endpoint**: `GET /export/pdf`
2. **Headers**: 
   - Authorization: `Bearer <your_token>`

The response will download a PDF report of your expenses.

---

## FAQs

### 1. How do I reset my password?

Currently, the API does not support password resets. You can manually update the password in the database or reach out to support.

### 2. How do I get my category ID?

You can view all available categories by sending a request to the categories endpoint (not implemented in this guide but available).

### 3. Can I modify multiple expenses at once?

Currently, the API supports modifying one expense at a time.

---