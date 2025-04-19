# AI Email HTML Writer

An AI-powered tool that converts Figma designs into responsive HTML emails.

## Features

- Convert Figma designs to responsive HTML emails
- AI-powered component matching and interpolation
- Secure user authentication with JWT tokens
- Email preview and validation
- Template management
- Comprehensive test suite

## Setup

### Backend

1. Create and activate virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration:
# - SECRET_KEY: Random string for JWT token signing
# - ALGORITHM: JWT algorithm (default: HS256)
# - ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time
# - DATABASE_URL: PostgreSQL connection string
```

4. Initialize database:
```bash
python init_db.py
```

5. Run the backend:
```bash
uvicorn app.main:app --reload
```

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm start
```

## Testing

The backend includes a comprehensive test suite using pytest. To run the tests:

```bash
cd backend
pytest
```

### Test Coverage
- User authentication (registration, login, token validation)
- User management (CRUD operations)
- Database operations
- API endpoints

## Authentication

The application uses JWT-based authentication with the following flow:

1. Register a new user:
   - Endpoint: POST /api/v1/auth/register
   - Required fields: email, password

2. Login to get access token:
   - Endpoint: POST /api/v1/auth/login
   - Required fields: email, password
   - Returns: access_token and token_type

3. Use the token in protected endpoints:
   - Add to request header: Authorization: Bearer <access_token>

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Template Management Endpoints

#### Create Template
```http
POST /api/v1/templates/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "My Template",
    "description": "A responsive email template",
    "html_content": "<html><body>...</body></html>",
    "is_public": false,
    "figma_url": "https://figma.com/file/...",
    "figma_file_key": "abc123",
    "figma_node_id": "node123"
}
```

#### List User's Templates
```http
GET /api/v1/templates/
Authorization: Bearer <access_token>
```

#### Get Template by ID
```http
GET /api/v1/templates/{template_id}
Authorization: Bearer <access_token>
```

#### Update Template
```http
PUT /api/v1/templates/{template_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "Updated Template",
    "description": "Updated description",
    "html_content": "<html><body>Updated content</body></html>",
    "is_public": true
}
```

#### Delete Template
```http
DELETE /api/v1/templates/{template_id}
Authorization: Bearer <access_token>
```

#### List Public Templates
```http
GET /api/v1/templates/public/
```

#### Get Template by Figma Data
```http
GET /api/v1/templates/figma/{file_key}?node_id={node_id}
Authorization: Bearer <access_token>
```

### Response Codes

- 200: Success
- 201: Created
- 400: Bad Request (e.g., invalid data, insufficient permissions)
- 401: Unauthorized (missing or invalid token)
- 404: Not Found
- 422: Validation Error

### Template Schema

```json
{
    "id": 1,
    "name": "Template Name",
    "description": "Template description",
    "html_content": "<html><body>...</body></html>",
    "is_public": false,
    "owner_id": 1,
    "created_at": "2024-04-19T12:00:00",
    "updated_at": "2024-04-19T12:00:00",
    "figma_url": "https://figma.com/file/...",
    "figma_file_key": "abc123",
    "figma_node_id": "node123"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Development Status

### Phase 1: Core Infrastructure (In Progress)
- [x] Backend setup with FastAPI
- [x] Database configuration with SQLAlchemy
- [x] User authentication system
- [x] Basic CRUD operations
- [x] Test infrastructure
- [x] Email Template model and CRUD
- [ ] Email generation service
- [ ] Frontend authentication components
- [ ] Frontend template management 