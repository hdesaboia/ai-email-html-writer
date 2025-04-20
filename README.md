# AI Email HTML Writer

An AI-powered tool that converts Figma designs into responsive HTML emails.

## Features

- Convert Figma designs to responsive HTML emails
- AI-powered component matching and interpolation
- Secure user authentication with JWT tokens
- Email preview and validation
- Template management
- Comprehensive test suite
- Figma API integration with caching and retry mechanisms
- Robust error handling for Figma operations

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
# - FIGMA_ACCESS_TOKEN: Your Figma API access token
# - REDIS_URL: Redis connection string for caching (optional)
```

4. Initialize database:
```bash
python init_db.py
```

5. Run Redis (if using caching):
```bash
redis-server
```

6. Run the backend:
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

The project includes both unit tests and integration tests to ensure functionality.

### Unit Tests
Unit tests run with mock data and don't require real API credentials:

```bash
python -m pytest backend/tests/unit/
```

### Integration Tests
Integration tests verify the Figma integration with real API calls:

1. Setup:
   ```bash
   cp backend/tests/integration.env.example backend/tests/integration.env
   ```

2. Configure:
   Edit `backend/tests/integration.env` with your Figma credentials:
   ```
   FIGMA_ACCESS_TOKEN=your_token_here
   FIGMA_FILE_KEY=your_test_file_key
   ```

3. Run:
   ```bash
   python -m pytest backend/tests/integration/
   ```

Note: Integration tests are skipped if Figma credentials are not provided.

### Test Coverage
Generate a coverage report:
```bash
python -m pytest --cov=backend/app backend/tests/
```

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

### Phase 1: Core Infrastructure ✅
- [x] Backend setup with FastAPI
- [x] Database configuration with SQLAlchemy
- [x] User authentication system
- [x] Basic CRUD operations
- [x] Test infrastructure
- [x] Email Template model and CRUD
- [x] Email generation service
- [x] Frontend authentication components
- [x] Frontend template management

### Phase 2: Email-Safe Responsive Design ✅
- [x] Table-based email layout system
- [x] Cross-client compatibility
- [x] Responsive image handling
- [x] Web-safe fonts and colors
- [x] Media queries for mobile devices
- [x] Email-specific CSS handling
- [x] Button and form element support
- [x] Comprehensive test coverage

### Phase 3: AI Integration 🚀
- [ ] OpenAI API integration
- [ ] Component recognition system
- [ ] Style analysis and matching
- [ ] Content generation
- [ ] Layout optimization
- [ ] A/B testing support
- [ ] Performance monitoring
- [ ] User feedback integration

## AI Features

The application uses AI to enhance the email generation process:

1. **Component Recognition**:
   - Analyzes Figma components to identify their purpose
   - Maps components to email-safe HTML patterns
   - Learns from user corrections and feedback

2. **Style Analysis**:
   - Extracts design patterns from Figma files
   - Converts complex styles to email-compatible formats
   - Maintains design fidelity across email clients

3. **Content Generation**:
   - Suggests email copy based on design context
   - Generates responsive variations
   - Optimizes for engagement

4. **Layout Optimization**:
   - Analyzes design hierarchy
   - Suggests mobile-friendly layouts
   - Ensures accessibility compliance

## Figma Integration

The application integrates with the Figma API to convert design files into HTML emails:

1. **Authentication**:
   - Requires a Figma access token (set in .env)
   - Token validation on startup
   - Automatic token refresh handling

2. **Design Access**:
   - Fetch Figma file metadata
   - Retrieve specific nodes and components
   - Access to image assets and styles

3. **Conversion Process**:
   - Recursive node traversal
   - Component mapping to HTML elements
   - Style extraction and application
   - Responsive layout generation

4. **Error Handling**:
   - Validation of API responses
   - Retry mechanism for transient failures
   - Detailed error logging
   - Custom exceptions for specific scenarios

5. **Performance Optimization**:
   - Redis-based caching for API responses
   - Batch processing of node requests
   - Efficient image asset handling

### Figma-Related Endpoints

#### Convert Figma Design
```http
POST /api/v1/templates/from-figma
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "figma_file_key": "abc123",
    "figma_node_id": "1:2",
    "name": "Email Template from Figma",
    "description": "Converted from Figma design"
}
```

#### Validate Figma Access
```http
GET /api/v1/templates/validate-figma
Authorization: Bearer <access_token>
```

#### Get Figma File Preview
```http
GET /api/v1/templates/figma-preview/{file_key}
Authorization: Bearer <access_token>
``` 