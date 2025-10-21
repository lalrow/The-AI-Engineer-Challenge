#!/bin/bash
set -e
cd "$(dirname "$0")/frontend"

echo "Starting frontend on :3000..."
npm run dev -- --port 3000

