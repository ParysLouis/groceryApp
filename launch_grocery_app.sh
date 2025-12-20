#!/usr/bin/env bash
set -euo pipefail

# Start the Grocery App API from the repository root.
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

# Activate local virtual environment if it exists.
if [ -d "$REPO_DIR/.venv" ]; then
  # shellcheck source=/dev/null
  source "$REPO_DIR/.venv/bin/activate"
fi

if ! command -v uvicorn >/dev/null 2>&1; then
  echo "uvicorn is required. Install dependencies with: pip install -r requirements.txt"
  exit 1
fi

echo "Starting Grocery App API on http://127.0.0.1:8000 ..."
exec uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
