---

# Database Schema

This document provides an overview of the database schema used in the Expense Tracker API. The schema is designed to handle user information, expense management, recurring expenses, and notifications.

## Tables

The database consists of the following tables:

- [User](#user)
- [Expenses](#expenses)
- [RecurringExpense](#recurringexpense)
- [Category](#category)
- [Notification](#notification)

---

## User

The `User` table stores user-related information.

| Column      | Type       | Constraints                | Description                               |
|-------------|------------|----------------------------|-------------------------------------------|
| `id`        | Integer    | Primary Key                | Unique identifier for the user            |
| `email`     | String(120)| Unique, Not Null           | User's email address                      |
| `user_name` | String(50) | Unique, Not Null           | User's username                           |
| `password_hash` | String(128) | Not Null              | Hashed password for authentication        |
| `created_at` | DateTime  | Default: `datetime.utcnow` | Timestamp when the user was created       |

### Relationships:
- **One-to-Many** with `Expenses`: A user can have many expense records.
- **One-to-Many** with `RecurringExpense`: A user can have many recurring expenses.
- **One-to-Many** with `Notification`: A user can receive multiple notifications.

---

## Expenses

The `Expenses` table stores information about individual expense entries.

| Column       | Type       | Constraints                | Description                               |
|--------------|------------|----------------------------|-------------------------------------------|
| `id`         | Integer    | Primary Key                | Unique identifier for the expense         |
| `amount`     | Float      | Not Null                   | The monetary amount of the expense        |
| `description`| String(255)| Not Null                   | Description of the expense                |
| `date`       | DateTime   | Not Null                   | Date when the expense occurred            |
| `user_id`    | Integer    | Foreign Key (`user.id`), Not Null | Reference to the user who created the expense |
| `category_id`| Integer    | Foreign Key (`category.id`), Not Null | Reference to the category of the expense  |

### Relationships:
- **Many-to-One** with `User`: Each expense belongs to a specific user.
- **Many-to-One** with `Category`: Each expense is categorized.

---

## RecurringExpense

The `RecurringExpense` table stores information about expenses that occur on a recurring basis.

| Column              | Type       | Constraints                | Description                               |
|---------------------|------------|----------------------------|-------------------------------------------|
| `id`                | Integer    | Primary Key                | Unique identifier for the recurring expense|
| `amount`            | Float      | Not Null                   | The amount for each recurrence            |
| `type_expense`      | String(255)| Not Null                   | Type of the recurring expense (e.g., bill, subscription) |
| `description_expense`| String(255)| Not Null                  | Description of the recurring expense      |
| `recurrence`        | String(255)| Not Null                   | Recurrence pattern (e.g., daily, weekly, monthly) |
| `start_date`        | DateTime   | Not Null                   | Start date of the recurring expense       |
| `end_date`          | DateTime   | Not Null                   | End date of the recurring expense         |
| `user_id`           | Integer    | Foreign Key (`user.id`), Not Null | Reference to the user who created the recurring expense |
| `category_id`       | Integer    | Foreign Key (`category.id`), Not Null | Reference to the category of the recurring expense |

### Relationships:
- **Many-to-One** with `User`: Each recurring expense belongs to a specific user.
- **Many-to-One** with `Category`: Each recurring expense has a category.

---

## Category

The `Category` table is used to categorize expenses and recurring expenses.

| Column      | Type       | Constraints                | Description                               |
|-------------|------------|----------------------------|-------------------------------------------|
| `id`        | Integer    | Primary Key                | Unique identifier for the category        |
| `name`      | String(50) | Unique, Not Null           | Name of the category                      |

### Relationships:
- **One-to-Many** with `Expenses`: A category can be assigned to multiple expenses.
- **One-to-Many** with `RecurringExpense`: A category can be assigned to multiple recurring expenses.

---

## Notification

The `Notification` table stores notifications for users. Notifications are created based on certain events such as large expenses.

| Column      | Type       | Constraints                | Description                               |
|-------------|------------|----------------------------|-------------------------------------------|
| `id`        | Integer    | Primary Key                | Unique identifier for the notification    |
| `user_id`   | Integer    | Foreign Key (`user.id`), Not Null | Reference to the user who receives the notification |
| `message`   | String(255)| Not Null                   | Message of the notification               |
| `type`      | String(50) | Not Null                   | Type of the notification (e.g., large_expense, reminder) |
| `created_at`| DateTime   | Default: `datetime.utcnow` | Timestamp when the notification was created |
| `is_read`   | Boolean    | Default: `False`           | Whether the notification has been read    |

### Relationships:
- **Many-to-One** with `User`: Each notification belongs to a specific user.

---

## Relationships Overview

- **User** ↔ **Expenses**: One-to-Many. Each user can have multiple expenses.
- **User** ↔ **RecurringExpense**: One-to-Many. Each user can have multiple recurring expenses.
- **User** ↔ **Notification**: One-to-Many. Each user can have multiple notifications.
- **Expenses** ↔ **Category**: Many-to-One. Each expense belongs to one category.
- **RecurringExpense** ↔ **Category**: Many-to-One. Each recurring expense belongs to one category.

---

## Database Diagram

You can visualize the relationships as follows:

```
User (1) ────> (∞) Expenses
User (1) ────> (∞) RecurringExpense
User (1) ────> (∞) Notification
Expenses (∞) ────> (1) Category
RecurringExpense (∞) ────> (1) Category
```

---