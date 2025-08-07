# Project Setup & Installation Guide

Welcome to the **Portal-X Event Aggregator API**! This guide provides detailed instructions on setting up and running the project on your local machine.

---

## Prerequisites

Ensure you have the following installed on your system:

- Python (>=3.8)
- pip (Python package manager)
- virtualenv (Optional but recommended)
- PostgreSQL (or SQLite for development)
- Redis (optional, for background task management)
- Git

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/NoirlabsDev/portal-x-events.git
cd portal-x-events
```

---

## Step 2: Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate  # For Windows
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements/local.txt
```

---

## Step 4: Create and Configure `.env` File

Create a `.env` file in the project's root directory and add the following environment variables:

```ini
SECRET_KEY=your-secret-key
DEFAULT_FROM_EMAIL=your-email@example.com
DEFAULT_SUPPORT_EMAIL=support@example.com
DEBUG=True  # Set False in production
ACCOUNT_USERNAME_BLACKLIST=admin,root,superuser
ALLOWED_HOSTS=127.0.0.1,localhost
SERP_API_KEY=your-serp-api-key
SERP_API_ENDPOINT=https://serpapi.com/search OR https://2e6f913b-08d8-4465-9f79-3fecc6edc280.mock.pstmn.io
```

> ⚠️ **Note:** Never commit your `.env` file to version control, only use `https://2e6f913b-08d8-4465-9f79-3fecc6edc280.mock.pstmn.io` in development.

---

## Step 5: Apply Database Migrations

```bash
python manage.py migrate
```

If you are using PostgreSQL, ensure you have updated `DATABASES` settings in `settings.py` or your `.env` file.

---

## Step 6: Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to set up an admin account.

---

## Step 7: Start the Development Server

```bash
python manage.py runserver
```

Access the API at: `http://localhost:8000/`

---

## Step 8: Obtain an Authentication Token

This project uses **Bearer Token Authentication**. First, generate a token for your user:

```bash
python manage.py drf_create_token <username>
```

Then, include this token in the `Authorization` header when making API requests:

```bash
Authorization: Bearer YOUR_TOKEN_HERE
```

---

## Step 9: API Response Structure

All API responses are structured in the following format:

```json
{
  "status": "[string]",
  "success": "[boolean]",
  "message": "[string]",
  "data": "[object]"
}
```

Example successful response:

```json
{
  "status": "success",
  "success": true,
  "message": "Request successful",
  "data": { "id": 1, "name": "Sample Event" }
}
```

Example error response:

```json
{
  "status": "error",
  "success": false,
  "message": "An error occurred",
  "data": null
}
```

---

## Step 10: Running Tests

Run tests to ensure everything is working correctly:

```bash
python manage.py test
```

---

## Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure `ALLOWED_HOSTS` properly
3. Use a production-ready database (PostgreSQL, MySQL, etc.)
4. Serve static files using AWS S3, DigitalOcean Spaces, or Whitenoise
5. Use a WSGI server like Gunicorn

---

## API Documentation

Once the server is running, API documentation can be accessed at:

```plaintext
http://127.0.0.1:8000/api/docs/
```

---

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make changes and commit (`git commit -m 'Added new feature'`)
4. Push to GitHub (`git push origin feature-branch`)
5. Create a Pull Request

---

### Need Help?

For any issues, feel free to open an [issue](https://github.com/NoirlabsDev/portal-x-events/issues) on GitHub or contact **Ruby** at `ruby@noirlabs.org`.
