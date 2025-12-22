#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d node_modules ]; then
  npm install
fi

PORT=${PORT:-3000}
(npm run dev -- --hostname 0.0.0.0 --port "$PORT" &)
SERVER_PID=$!

sleep 3
if command -v open >/dev/null; then
  open "http://localhost:${PORT}" >/dev/null 2>&1 || true
fi

wait $SERVER_PID
