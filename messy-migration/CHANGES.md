# Refactored code changes

## Major Issues Identified

- **Raw SQL Injection Risk :** Many queries used string interpolation, exposing the app to severe injection attacks.
- **Plaintext Password Storage:** User passwords were stored and matched in plaintext, compromising security.
- **Lack of Input Validation:** Email and password formats were not consistently validated before database operations.
- **No Authentication/Authorization:** Sensitive endpoints could be accessed without restriction.
- **Unclear or Inconsistent Error Handling:** Errors were not always managed gracefully with consistent HTTP status codes.

## Changes Made and Why

- **Parameterized SQL Queries:** Replaced all raw string SQL queries with parameterized queries (`?` placeholders) to eliminate SQL injection vulnerabilities.
- **Password Hashing:** Implemented password hashing and verification using `werkzeug.security` to secure user credentials.
- **Per-request DB Connections:** Refactored database connection logic to open and close connections per request, avoiding global shared connections and improving thread safety.
- **Input Validation:** Centralized email and password validation logic to ensure only valid and well-formed data is processed.
- **Error Handling:** Added error handlers for common HTTP errors and improved API responses with proper status codes and informative JSON messages.
- **Email Uniqueness Handling:** Assumed and enforced email uniqueness via a database constraint, catching and reporting duplicates gracefully.
- **Basic Testing Added:** Added minimal tests using Postman and Python test scripts to verify critical functionality like user creation, login, and search.

## Assumptions and Trade-offs

- **Authentication Tokens Not Implemented:** Due to time constraints, full session or token-based authentication was postponed. The `login` endpoint returns success but doesn’t issue JWT or cookies.


## What Would I Do with More Time

- Enhance Input Validation: Implement more comprehensive and robust validation of all user inputs (e.g., stricter email/password policies, validation libraries, better error messages).
- Implement JWT or session-based authentication to secure all sensitive endpoints.
- Add logging and monitoring for auditability and debugging.
- Explore deployment ready configurations, such as disabling debug mode and using production WSGI servers.

---
