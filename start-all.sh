#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Loading environment variables from .env..."
set -a && source .env && set +a

echo "Starting backend on :8000..."
nohup uv run python api/app.py > .cursor/.agent-tools/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

echo "Starting frontend on :3000..."
cd frontend
nohup npm run dev -- --port 3000 > ../.cursor/.agent-tools/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

cd ..
sleep 2
curl -s http://localhost:8000/api/health && echo " - Backend health check OK" || echo " - Backend not responding yet"

echo ""
echo "Services started:"
echo "  Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
echo "  Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "Logs:"
echo "  Backend:  tail -f .cursor/.agent-tools/backend.log"
echo "  Frontend: tail -f .cursor/.agent-tools/frontend.log"

