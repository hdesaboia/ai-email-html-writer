# AI Email HTML Writer

A full-stack application for generating HTML email templates using AI.

## Project Structure

```
.
├── backend/           # FastAPI backend
│   └── requirements.txt
├── frontend/          # React frontend
│   └── package.json
└── docs/             # Project documentation
```

## Technology Stack

### Frontend
- React 18 with TypeScript
- Material-UI for UI components
- Redux Toolkit for state management
- React Router for navigation
- Socket.IO for real-time features
- Axios for HTTP requests

### Backend
- FastAPI for the web framework
- SQLAlchemy for database ORM
- PostgreSQL for the database
- JWT for authentication
- Alembic for database migrations

## Development Setup

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8 or higher
- PostgreSQL

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

## Dependencies

### Frontend Dependencies
- `@mui/material`: Material Design components
- `@reduxjs/toolkit`: State management
- `react-router-dom`: Routing
- `socket.io-client`: Real-time communication
- `axios`: HTTP client

### Backend Dependencies
- `fastapi`: Web framework
- `sqlalchemy`: Database ORM
- `python-jose`: JWT implementation
- `alembic`: Database migrations
- `pytest`: Testing framework

## Contributing

1. Create a feature branch from `development`
2. Make your changes
3. Submit a pull request for review

## License

[Add your license information here] 