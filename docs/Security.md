---

# Security Policy

The security of the Expense Tracker API is a top priority, and we are committed to protecting our users' data and privacy. This document outlines our security practices and how to report security vulnerabilities.

## Supported Versions

We actively maintain and provide security updates for the following versions of the Expense Tracker API:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark:  |
| 0.x     | :x:                |

We encourage users to always update to the latest version to benefit from the most recent security improvements.

---

## Reporting a Vulnerability

If you discover a security vulnerability in the Expense Tracker API, please follow the guidelines below to report it responsibly:

1. **Email us directly**: Send a detailed description of the vulnerability to [kiflunahom1994@gmail.com]. Include:
   - The nature of the vulnerability.
   - Steps to reproduce the issue.
   - Any possible fixes or mitigations (if known).

2. **Response time**: We are committed to investigating all security issues promptly and will acknowledge receipt of your report within 48 hours.

3. **Fixing the issue**: After assessing the vulnerability, we will take appropriate steps to patch the issue. You will be notified once the issue has been resolved and a security update has been released.

---

## Security Best Practices

Here are some of the security measures implemented in the Expense Tracker API:

### 1. **JWT Authentication**

- We use **JSON Web Tokens (JWT)** for securing API requests. Only authenticated users can access protected routes.
- JWT tokens include a secret key for validation, and expired or tampered tokens are rejected.

### 2. **Password Security**

- User passwords are hashed using **bcrypt** before being stored in the database, ensuring that plain-text passwords are never stored.
- A minimum password length is enforced to ensure stronger password security.

### 3. **Input Validation**

- We validate all incoming data to prevent common security issues such as **SQL Injection** and **Cross-Site Scripting (XSS)**. This includes sanitizing user inputs, validating email formats, and restricting allowed input ranges.

### 4. **CSRF Protection**

- Although the API is primarily designed for JSON-based requests, **CSRF protection** is disabled for API requests but can be enabled if the application is integrated with forms.

### 5. **Data Encryption**

- For production environments, all API traffic should be encrypted using **SSL/TLS** to prevent data interception or man-in-the-middle attacks.

### 6. **Rate Limiting**

- Implement rate limiting on certain endpoints, such as login and registration, to mitigate brute force attacks.

---

## Security Updates

We regularly review our code for potential security vulnerabilities. If any vulnerabilities are discovered, we will:
- Provide timely patches to resolve them.
- Notify all users of critical updates through the project repository.

---

## Vulnerability Disclosure Program

We follow a **responsible disclosure policy**. This means that if you report a vulnerability responsibly:
- We will not pursue legal action against you.
- We will work with you to verify and resolve the issue.
- You will receive recognition in the changelog (with your consent) once the issue has been addressed.

---

## Contact

For all security-related concerns, please reach out to our security team:

- **Email**: [kiflunahom1994@gmail.com]

---

By following the above guidelines and practices, we aim to keep the Expense Tracker API safe and secure for all users. Thank you for helping us maintain security and reliability.

---