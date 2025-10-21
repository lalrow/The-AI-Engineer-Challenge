#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Loading environment variables from .env..."
set -a && source .env && set +a

echo "Running test suite..."
uv run pytest -v

