# AI Email HTML Writer

An AI-powered tool that converts Figma designs into responsive HTML emails.

## Features

- Convert Figma designs to responsive HTML emails
- AI-powered component matching and interpolation
- Secure user authentication
- Email preview and validation
- Template management

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
# Edit .env with your configuration
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

To run the tests:
```bash
cd backend
pytest
```

## Authentication

The application uses JWT-based authentication. Users need to:
1. Register with email and password
2. Login to get an access token
3. Use the token in the Authorization header for protected endpoints

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 