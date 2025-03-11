# TrustCall API

TrustCall is a RESTful API designed for managing users, contacts, and spam reports. It allows users to register, add contacts, mark phone numbers as spam, and perform searches in a global phonebook with spam tracking.

## Overview

### Key Features:
- User authentication and authorization using JWT.
- Global phonebook with spam tracking.
- Contact management.
- Phone number and name search with caching.
- Spam reporting.
- Custom rate limiting for abuse prevention.

## Technologies Used
- **Django**: Backend framework.
- **Django REST Framework (DRF)**: For building RESTful APIs.
- **JWT Authentication**: For secure API access.
- **Phonenumbers**: Library for phone number validation.
- **Django Caching**: For storing and retrieving search results.
- **Custom Throttling**: To limit excessive API requests.

## How to Run the Code

### Prerequisites
1. Python 3.x installed.
2. PostgreSQL/MySQL or any preferred database set up.
3. Django and Django REST Framework installed.
4. `pip` for installing dependencies.

### Steps to Run
1. **Navigate to the Project Directory:**
   ```bash
   cd TrustCall
   ```

2. **Create a Virtual Environment (Optional but Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database:**
   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Access the server at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## API Endpoints

### 1. User Registration
- **Endpoint:** `POST /api/register/`
- **Description:** Register a new user and add them to the global phonebook.
- **Request Body:**
  ```json
  {
    "username": "john_doe",
    "password": "password123",
    "phone_number": "+911234567890"
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "username": "john_doe",
    "phone_number": "+911234567890",
    "email_address": null
  }
  ```

### 2. Add Contact
- **Endpoint:** `POST /api/add-contact/`
- **Description:** Allows authenticated users to add a contact and update the global phonebook.
- **Request Body:**
  ```json
  {
    "name": "Alice",
    "phone_number": "+911234567891"
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "name": "Alice",
    "phone_number": "+911234567891",
    "user": 1
  }
  ```

### 3. Mark Spam
- **Endpoint:** `POST /api/mark-spam/`
- **Description:** Allows authenticated users to report a phone number as spam.
- **Request Body:**
  ```json
  {
    "phone_number": "+911234567891"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Spam reported successfully"
  }
  ```

### 4. Search by Name
- **Endpoint:** `GET /api/search-by-name/`
- **Description:** Search for contacts by name in the global phonebook.
- **Query Parameters:**
  - `query`: Name to search for (e.g., `Alice`).
- **Example Request:**
  ```http
  GET /api/search-by-name/?query=Alice
  ```
- **Response:**
  ```json
  [
    {
      "name": "Alice",
      "phone_number": "+911234567891",
      "spam_likelihood": 30
    }
  ]
  ```

### 5. Search by Phone Number
- **Endpoint:** `GET /api/search-by-phone/`
- **Description:** Search for a phone number in the global phonebook.
- **Query Parameters:**
  - `query`: Phone number to search for (e.g., `+911234567891`).
- **Example Request:**
  ```http
  GET /api/search-by-phone/?query=+911234567891
  ```
- **Response:**
  ```json
  {
    "name": "Alice",
    "phone_number": "+911234567891",
    "spam_likelihood": 30,
    "email": null
  }
  ```

### 6. JWT Token Obtain
- **Endpoint:** `POST /api/token/`
- **Description:** Get a JWT token for authenticated API access.
- **Request Body:**
  ```json
  {
    "username": "john_doe",
    "password": "password123"
  }
  ```
- **Response:**
  ```json
  {
    "access": "your-access-token",
    "refresh": "your-refresh-token"
  }
  ```

### 7. JWT Token Refresh
- **Endpoint:** `POST /api/token/refresh/`
- **Description:** Refresh the JWT token.
- **Request Body:**
  ```json
  {
    "refresh": "your-refresh-token"
  }
  ```
- **Response:**
  ```json
  {
    "access": "new-access-token"
  }
  ```

## Additional Features

### Caching
- Search results are cached for 5 minutes (300 seconds) to improve performance and reduce database queries.

### Indexing
- Database indexing on the `phone_number` field ensures efficient search operations.

### Throttling
- Custom rate limits of 100 requests per minute for endpoints like `/api/search-by-name/` and `/api/search-by-phone/`.
- Exceeding the limit results in a `429 Too Many Requests` response.

### Authentication
- JWT-based authentication.
  - Use `/api/token/` to obtain tokens.
  - Include the token in the `Authorization` header for authenticated endpoints (e.g., `Bearer your-access-token`).

## Notes
1. **User Registration:** Register using `/api/register/` and obtain tokens via `/api/token/`.
2. **Token Expiry:** Tokens expire after 1 hour. Refresh tokens via `/api/token/refresh/`.
3. **Database:** Replace the NeonDB URL if using a different database.
4. **Dummy Data Generation:** Use the provided `dummy_data_generator` file to generate test data with Faker.
5. **Phone Number Format:** Only Indian phone numbers (`+91`) are supported.

## Conclusion
The TrustCall API offers a simple yet effective platform for managing contacts, spam reports, and global phonebook searches. With robust features like JWT authentication, caching, and throttling, it ensures secure and efficient operations.

---

For any issues or contributions, feel free to open a pull request or raise an issue!
