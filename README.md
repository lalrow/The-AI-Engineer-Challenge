## 🧰 Look at REPORT.md file for Documentation of Deliverables

## 🚀 Quick Start (Recommended)

The easiest way to start the application is using the provided startup scripts. These scripts automatically load environment variables from `.env` file.

### Start Both Services
```bash
./start-all.sh
```

This will:
- Load all environment variables from `.env` (OPENAI_API_KEY, TAVILY_API_KEY, COHERE_API_KEY, etc.)
- Start backend on http://localhost:8000 in background
- Start frontend on http://localhost:3000 in background
- Display service PIDs and log file locations

### Start Services Individually

**Backend only:**
```bash
./start-backend.sh
```

**Frontend only:**
```bash
./start-frontend.sh
```

**Run tests:**
```bash
./run-tests.sh
```

### Manual Start (Alternative)

If you prefer to start services manually:

**Backend:**
```bash
set -a && source .env && set +a
uv run python api/app.py
```

**Frontend:**
```bash
cd frontend && npm run dev -- --port 3000
```

### View Logs

After starting with `start-all.sh`:
```bash
# Backend logs
tail -f .cursor/.agent-tools/backend.log

# Frontend logs
tail -f .cursor/.agent-tools/frontend.log
```

### Important Notes

- **Environment Variables:** All scripts automatically load `.env` file. Ensure your `.env` contains:
  - `OPENAI_API_KEY`
  - `TAVILY_API_KEY`
  - `COHERE_API_KEY`
  - `QDRANT_URL` (defaults to `./qdrant_local`)

- **Qdrant Database:** The application uses a single persistent Qdrant instance at `./qdrant_local` (never :memory:, Docker, or cloud URLs per MDC rules)

- **First Time Setup:**
  ```bash
  # Install dependencies
  uv sync --extra dev
  
  # Install frontend dependencies
  cd frontend && npm install