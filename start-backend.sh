#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Loading environment variables from .env..."
set -a && source .env && set +a

echo "Starting backend on :8000..."
uv run python api/app.py

