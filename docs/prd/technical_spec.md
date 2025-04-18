# Technical Specifications

## System Architecture

### Components
1. Frontend Web Interface
   - Description: User interface for email developers
   - Responsibilities:
     - Design input handling
     - Preview rendering
     - AI decision display
     - User override interface
   - Interfaces:
     - Figma API
     - Backend API
     - Preview renderer

2. AI Backend Service
   - Description: Core AI processing engine
   - Responsibilities:
     - Figma design parsing
     - Component matching
     - HTML generation
     - Decision logging
   - Interfaces:
     - Figma API
     - HTML library
     - Snippet database

3. Snippet Management System
   - Description: Local snippet library handler
   - Responsibilities:
     - CSV file ingestion
     - Snippet storage
     - Version control
   - Interfaces:
     - File system
     - Backend API

## Technology Stack

### Frontend
- Framework: React.js
- UI Library: Material-UI
- State Management: Redux
- Testing Framework: Jest + React Testing Library

### Backend
- Language: Python
- Framework: FastAPI
- Database: PostgreSQL
- API: REST + WebSocket (for real-time updates)

### Infrastructure
- Hosting: AWS
- CI/CD: GitHub Actions
- Monitoring: Prometheus + Grafana

## Data Models

### Figma Design
```json
{
  "design_id": "string",
  "node_id": "string",
  "components": [
    {
      "id": "string",
      "type": "string",
      "properties": "object"
    }
  ],
  "styles": "object"
}
```

### HTML Template
```json
{
  "template_id": "string",
  "html": "string",
  "components": [
    {
      "id": "string",
      "type": "string",
      "interpolations": "array"
    }
  ],
  "snippets": "array"
}
```

## API Specifications

### Convert Design to HTML
- Method: POST
- Path: /api/v1/convert
- Request Body:
```json
{
  "figma_design_id": "string",
  "node_id": "string",
  "options": {
    "include_preview": "boolean",
    "include_decisions": "boolean"
  }
}
```
- Response Body:
```json
{
  "html": "string",
  "preview_url": "string",
  "decisions": "array",
  "components": "array"
}
```
- Status Codes:
  - 200: Success
  - 400: Bad Request
  - 401: Unauthorized
  - 500: Server Error

### Get AI Decisions
- Method: GET
- Path: /api/v1/decisions/{conversion_id}
- Response Body:
```json
{
  "component_mappings": "array",
  "interpolation_logic": "array",
  "snippets_used": "array",
  "template_reuse": "object"
}
```
- Status Codes:
  - 200: Success
  - 404: Not Found
  - 500: Server Error 