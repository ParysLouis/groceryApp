# Grocery App API (offline-friendly)

This repository contains a minimal grocery list API implemented with lightweight, built-in stand-ins for popular libraries (Fast
API, SQLAlchemy, and Pydantic). Everything required to run and test the service is checked into the repository so it works in of
fline or proxied environments without pulling packages from PyPI.

## Getting started locally

Follow these steps to clone the project and run the API on your laptop.

1. **Install prerequisites**
   - Python 3.11+ is recommended. Virtual environments keep the dependencies isolated from your system Python.
2. **Clone the repository**
   ```bash
   git clone https://github.com/<your-org>/groceryApp.git
   cd groceryApp
   ```
3. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   # On Windows use: .venv\\Scripts\\activate
   ```
4. **Install runtime dependencies**
   - If you have internet access, installing the pinned dependencies provides the full FastAPI/SQLAlchemy stack:
     ```bash
     pip install -r requirements.txt
     ```
   - If you're offline, the vendored shims in `fastapi/`, `sqlalchemy/`, and `pydantic/` are enough to run the tests and service; `uvicorn` is the only binary you may need to install separately for local serving.
5. **Run the API with a single command**
   ```bash
   python -m app
   ```
   This starts Uvicorn with auto-reload enabled on `http://127.0.0.1:8000`. You can pass flags such as `--host 0.0.0.0`, `--port 8080`, or `--no-reload` to customize the server.
   Interactive API docs are available at `http://127.0.0.1:8000/docs`.

## Running the tests

```bash
pytest
```

The test suite boots the application and exercises the CRUD endpoints using the bundled test client.

## Why vendored dependencies?

The environment used to validate this project blocks external package downloads. To keep the developer experience smooth, small
compatibility shims for FastAPI, SQLAlchemy, and Pydantic live in the `fastapi/`, `sqlalchemy/`, and `pydantic/` directories res
pectively. They provide just enough surface area for the app and tests to run while retaining the same public APIs expected by t
he codebase.

