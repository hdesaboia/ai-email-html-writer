# Project Setup Documentation

## Development Environment

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git
- GitHub account
- Figma account with API access
- PostgreSQL 13+
- Redis (optional, for caching)

### Initial Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-email-html-writer.git
cd ai-email-html-writer
```

2. Set up Python virtual environment:
```bash
python3.9 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Set up environment variables:
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

5. Initialize database:
```bash
python init_db.py
```

6. Run tests:
```bash
python -m pytest
```

## Project Structure

```
ai-email-html-writer/
├── backend/           # Backend service
│   ├── app/          # Application code
│   ├── tests/        # Test files
│   └── requirements.txt
├── frontend/         # Frontend application
├── docs/             # Documentation
│   ├── prd/          # Product requirements
│   ├── technical_specs/  # Technical specifications
│   └── original/     # Original documents
└── README.md         # Project overview
```

## Development Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and run tests:
```bash
python -m pytest
```

3. Commit your changes:
```bash
git add .
git commit -m "feat: description of your changes"
```

4. Push your branch:
```bash
git push origin feature/your-feature-name
```

5. Create a Pull Request on GitHub

## Testing

The project includes both unit tests and integration tests:

```bash
# Run all tests
python -m pytest

# Run only unit tests
python -m pytest tests/unit

# Run only integration tests
python -m pytest tests/integration
```

### Test Requirements
- Unit tests use mock data and don't require real API credentials
- Integration tests require a real Figma access token
- See README.md for detailed test setup instructions

## Deployment

Deployment instructions will be added as the project evolves. 