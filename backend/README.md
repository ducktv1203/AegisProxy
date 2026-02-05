# AegisProxy Backend

This is the Python/FastAPI backend for AegisProxy.

## Development

1. Create virtual environment:

   ```bash
   python -m venv .venv
   ```

2. Install dependencies:

   ```bash
   .\.venv\Scripts\pip install -e .
   ```

3. Run server:
   ```bash
   .\.venv\Scripts\python -m uvicorn aegis.main:app --reload
   ```
