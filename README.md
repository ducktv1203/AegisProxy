# AegisProxy

**A Secure AI Gateway & Dashboard**

AegisProxy intercepts and sanitizes LLM traffic to prevent PII leakage and prompt injection attacks, complete with a modern administrative dashboard.

## Project Structure

This is a **monorepo** containing both the backend proxy and frontend dashboard:

- **[`backend/`](backend/)**: Python/FastAPI application handling the core proxy logic, PII detection (Presidio), and injection defense.
- **[`frontend/`](frontend/)**: React/Vite application for the admin dashboard, monitoring, and configuration.

## Getting Started

### Backend

```bash
cd backend
# Install dependencies
pip install -e "."
# Run server
uvicorn aegis.main:run --reload
```

### Frontend

```bash
cd frontend
# Install dependencies
npm install
# Run dev server
npm run dev
```

## Documentation

See [Implementation Plan](implementation_plan.md) for detailed architecture.
