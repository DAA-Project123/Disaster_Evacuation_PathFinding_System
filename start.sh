#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${ROOT}"
cd "${ROOT}/backend"
uvicorn main:app --reload --port 8000 &
BACK_PID=$!
cd "${ROOT}/frontend"
bun run dev &
FRONT_PID=$!
trap 'kill $BACK_PID $FRONT_PID 2>/dev/null || true' EXIT
wait
