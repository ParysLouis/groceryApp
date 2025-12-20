# Grocery App API (offline-friendly)

This repository contains a minimal grocery list API implemented with lightweight, built-in stand-ins for popular libraries (FastAPI, SQLAlchemy, and Pydantic). Everything required to run and test the service is checked into the repository so it works in offline or proxied environments without pulling packages from PyPI.

## Running the tests

```bash
pytest
```

The test suite boots the application and exercises the CRUD endpoints using the bundled test client.

## Why vendored dependencies?

The environment used to validate this project blocks external package downloads. To keep the developer experience smooth, small compatibility shims for FastAPI, SQLAlchemy, and Pydantic live in the `fastapi/`, `sqlalchemy/`, and `pydantic/` directories respectively. They provide just enough surface area for the app and tests to run while retaining the same public APIs expected by the codebase.