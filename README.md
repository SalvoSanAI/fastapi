# FastAPI Posts API

A modern, production-ready RESTful API built with FastAPI and SQLAlchemy ORM for managing posts and users with JWT authentication.

## 🚀 Features

- **RESTful API**: Complete CRUD operations for posts and users
- **Authentication**: JWT-based authentication system
- **Database ORM**: SQLAlchemy for database operations
- **Input Validation**: Pydantic models for request/response validation
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Security**: Password hashing with bcrypt
- **Modern Python**: Type hints and modern Python practices

## 📋 API Endpoints

### Authentication (`/auth`)
- `POST /auth/login` - User login and JWT token generation

### Posts (`/posts`)
- `GET /posts` - Get all posts
- `GET /posts/latest` - Get the latest post
- `GET /posts/{id}` - Get a specific post by ID
- `POST /posts` - Create a new post
- `PUT /posts/{id}` - Update an existing post
- `DELETE /posts/{id}` - Delete a post

### Users (`/users`)
- `GET /users/{id}` - Get user by ID
- `POST /users` - Create a new user

## 🛠️ Tech Stack

- **FastAPI** - Modern web framework for building APIs
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database (configurable)
- **Pydantic** - Data validation and serialization
- **bcrypt** - Password hashing
- **python-jose** - JWT token handling
- **uvicorn** - ASGI server

## 📦 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database

### 1. Clone the repository
```bash
git clone <repository-url>
cd fastapi-posts-api
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the `app/` directory with your database configuration:

```env
database_host=localhost
database_password=your_password
database_name=fastapi
database_user=postgres
database_port=5432
secret_key=your_secret_key_here
algorithm=HS256
access_token_expire_seconds=1800
```

### 5. Database Setup

Ensure PostgreSQL is running and create the database specified in your `.env` file.

## 🏃‍♂️ Running the Application

### Development Server
```bash
cd app
uvicorn main_alchemy:app --reload --host 0.0.0.0 --port 8000
```

### Production Server
```bash
cd app
uvicorn main_alchemy:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## 🔐 Authentication

The API uses JWT tokens for authentication. To access protected endpoints:

1. **Login**: Send a POST request to `/auth/login` with form data:
   - `username`: user's email
   - `password`: user's password

2. **Use Token**: Include the returned token in subsequent requests:
   ```
   Authorization: Bearer <your-jwt-token>
   ```

## 📝 Usage Examples

### Creating a User
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### User Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword"
```

### Creating a Post (Authenticated)
```bash
curl -X POST "http://localhost:8000/posts" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "content": "This is the content of my first post",
    "published": true,
    "rating": 5
  }'
```

### Getting All Posts
```bash
curl -X GET "http://localhost:8000/posts"
```

## 🏗️ Project Structure

```
app/
├── __init__.py
├── config.py              # Application configuration
├── database.py            # Database models and connection
├── main_alchemy.py        # Main FastAPI application
├── oauth2.py              # Authentication utilities
├── schema.py              # Pydantic models
├── utils.py               # Utility functions
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
└── roturs/               # API route modules
    ├── __init__.py
    ├── auth.py           # Authentication endpoints
    ├── post.py           # Post endpoints
    └── user.py           # User endpoints
```

## 🧪 Testing

The application includes comprehensive error handling and validation. Test the API using:

- **Interactive API Docs**: Visit http://localhost:8000/docs
- **Postman Collection**: Import the provided collection for testing
- **curl commands**: Use the examples provided above

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `database_host` | `localhost` | Database host |
| `database_password` | `sa` | Database password |
| `database_name` | `fastapi` | Database name |
| `database_user` | `postgres` | Database username |
| `database_port` | `5432` | Database port |
| `secret_key` | `your_secret_key_here` | JWT secret key |
| `algorithm` | `HS256` | JWT algorithm |
| `access_token_expire_seconds` | `1800` | Token expiration time |

## 🚀 Deployment

### Docker
```bash
docker build -t fastapi-posts-api .
docker run -p 8000:8000 fastapi-posts-api
```

### Docker Compose (with PostgreSQL)
```yaml
version: '3.8'
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: fastapi
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - database_host=db
      - database_password=your_password
      - database_name=fastapi
      - database_user=postgres
    depends_on:
      - db

volumes:
  postgres_data:
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json



## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database ORM provided by [SQLAlchemy](https://www.sqlalchemy.org/)
- Authentication powered by [python-jose](https://python-jose.readthedocs.io/)

## 🐛 Support

For support, email support@example.com or create an issue on the GitHub repository.

---
