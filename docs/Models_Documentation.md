### Comprehensive Documentation of db

This document provides a detailed description of all documentation for the `models.py` file, which defines the database models for the expense tracker project. Each model is described with its fields, relationships, and validation methods.

---

### **Database Models Documentation**

#### 1. **User Model**
The `User` model represents users in the application. It stores user credentials and maintains relationships with expenses, recurring expenses, and notifications.

- **Table Name:** `user`

- **Fields:**
  | **Field Name**  | **Type**       | **Description**                                      | **Constraints**        |
  |-----------------|----------------|------------------------------------------------------|------------------------|
  | `id`            | `Integer`      | Primary key, unique identifier for each user         | Primary Key            |
  | `email`         | `String(120)`  | User's email address                                 | Unique, Not Null       |
  | `user_name`     | `String(50)`   | Username                                             | Unique, Not Null       |
  | `password_hash` | `String(128)`  | Hashed password for authentication                   |                        |
  | `created_at`    | `DateTime`     | Timestamp when the user was created                  | Default: `datetime.utcnow` |

- **Relationships:**
  - `expenses`: One-to-Many relationship with `Expenses`.
  - `recurring_expenses`: One-to-Many relationship with `RecurringExpense`.
  - `notifications`: One-to-Many relationship with `Notification`.

- **Methods:**
  - `set_password(password)`: Hashes the password and stores it.
  - `set_email(email)`: Validates and sets the email address.
  - `set_username(username)`: Validates and sets the username.

---

#### 2. **Expenses Model**
The `Expenses` model represents individual expenses created by users. Each expense is associated with a user and a category.

- **Table Name:** `expenses`

- **Fields:**
  | **Field Name**  | **Type**       | **Description**                                      | **Constraints**        |
  |-----------------|----------------|------------------------------------------------------|------------------------|
  | `id`            | `Integer`      | Unique identifier for the expense                    | Primary Key            |
  | `amount`        | `Float`        | The amount spent                                     | Not Null               |
  | `description`   | `String(255)`  | A brief description of the expense                   | Not Null               |
  | `date`          | `DateTime`     | The date the expense occurred                        | Not Null               |
  | `user_id`       | `Integer`      | Reference to the user who made the expense           | Foreign Key (`user.id`)|
  | `category_id`   | `Integer`      | Reference to the category of the expense             | Foreign Key (`category.id`) |

- **Relationships:**
  - `user`: Many-to-One relationship with `User`.
  - `category`: Many-to-One relationship with `Category`.

- **Validation Methods:**
  - `validate_amount(self, key, amount)`: Ensures the amount is greater than zero.
  - `validate_date(self, key, date)`: Ensures the date is a valid `datetime` object.

---

#### 3. **Category Model**
The `Category` model represents different categories under which expenses and recurring expenses can be grouped.

- **Table Name:** `category`

- **Fields:**
  | **Field Name**  | **Type**       | **Description**                                      | **Constraints**        |
  |-----------------|----------------|------------------------------------------------------|------------------------|
  | `id`            | `Integer`      | Unique identifier for the category                   | Primary Key            |
  | `name`          | `String(50)`   | Name of the category                                 | Unique, Not Null       |

- **Relationships:**
  - `expenses_list`: One-to-Many relationship with `Expenses`.
  - `recurring_expenses_list`: One-to-Many relationship with `RecurringExpense`.

- **Validation Methods:**
  - `validate_name(self, key, name)`: Ensures the category name is not longer than 50 characters.

---

#### 4. **RecurringExpense Model**
The `RecurringExpense` model represents expenses that occur on a recurring basis, such as daily, weekly, or monthly payments.

- **Table Name:** `recurring_expense`

- **Fields:**
  | **Field Name**      | **Type**       | **Description**                                      | **Constraints**        |
  |---------------------|----------------|------------------------------------------------------|------------------------|
  | `id`                | `Integer`      | Unique identifier for the recurring expense          | Primary Key            |
  | `amount`            | `Float`        | The amount spent for each recurrence                 | Not Null               |
  | `type_expense`      | `String(255)`  | Type of recurring expense                            | Not Null               |
  | `description_expense` | `String(255)` | Description of the recurring expense                 | Not Null               |
  | `recurrence`        | `String(255)`  | Recurrence type (daily, weekly, monthly, yearly)     | Not Null               |
  | `start_date`        | `DateTime`     | Start date of the recurring expense                  | Not Null               |
  | `end_date`          | `DateTime`     | End date of the recurring expense                    | Not Null               |
  | `user_id`           | `Integer`      | Reference to the user who created the expense        | Foreign Key (`user.id`)|
  | `category_id`       | `Integer`      | Reference to the category of the expense             | Foreign Key (`category.id`) |

- **Relationships:**
  - `user`: Many-to-One relationship with `User`.
  - `category`: Many-to-One relationship with `Category`.

- **Validation Methods:**
  - `validate_recurrence(self, key, recurrence)`: Ensures the recurrence value is one of ['daily', 'weekly', 'monthly', 'yearly'].
  - `validate_dates(self, key, date)`: Ensures the `start_date` and `end_date` are valid and that `end_date` is not before `start_date`.

---

#### 5. **Notification Model**
The `Notification` model stores messages or notifications sent to users.

- **Table Name:** `notification`

- **Fields:**
  | **Field Name**  | **Type**       | **Description**                                      | **Constraints**        |
  |-----------------|----------------|------------------------------------------------------|------------------------|
  | `id`            | `Integer`      | Unique identifier for the notification               | Primary Key            |
  | `user_id`       | `Integer`      | Reference to the user receiving the notification     | Foreign Key (`user.id`)|
  | `message`       | `String(255)`  | The notification message                             | Not Null               |
  | `type`          | `String(50)`   | Type of notification (e.g., reminder, alert)         | Not Null               |
  | `created_at`    | `DateTime`     | Timestamp when the notification was created          | Default: `datetime.utcnow` |
  | `is_read`       | `Boolean`      | Whether the notification has been read by the user   | Default: `False`       |

- **Relationships:**
  - `user`: Many-to-One relationship with `User`.

---

### **Validation Functions**

The following validation functions are used throughout the models to enforce data integrity:

1. **`validate_email(email)`**
   - Ensures the email follows a standard format using regex.
   - Raises `ValueError` if the email is invalid.

2. **`validate_username(username)`**
   - Ensures the username only contains alphanumeric characters and underscores.
   - Raises `ValueError` if the username is invalid.

3. **`validate_password(password)`**
   - Ensures the password is at least 8 characters long.
   - Raises `ValueError` if the password is too short.

4. **`validate_amount(amount)`**
   - Ensures the amount is greater than 0.
   - Raises `ValueError` if the amount is invalid.

5. **`validate_date(date)`**
   - Ensures the date is a valid `datetime` object.
   - Raises `ValueError` if the date is invalid.

6. **`validate_recurrence(recurrence)`**
   - Ensures the recurrence is one of ['daily', 'weekly', 'monthly', 'yearly'].
   - Raises `ValueError` if the recurrence value is invalid.

---

### **Relationships Between Models**

- A **User** can have multiple **Expenses**, **RecurringExpense**, and **Notification** records.
- An **Expense** and a **RecurringExpense** must belong to a **User** and a **Category**.
- A **Category** groups multiple **Expenses** and **RecurringExpense** records.
- **Notifications** are sent to **Users** and can be marked as read or deleted.

---

### **Example of Data Relationships:**

- A user with ID `1` can have multiple expenses in categories such as "Food" or "Rent."
- Each recurring expense (e.g., monthly rent payments) can be tracked separately with a start and end date.
- Notifications may be sent to users when certain conditions are met (e.g., expense limits exceeded).

---
