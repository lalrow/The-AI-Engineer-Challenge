# MERGE Instructions - Kids Science Tutor with Persistent RAG

## Branch Information
- **Feature Branch**: `feature/rag-persistence-and-bees`
- **Target Branch**: `main`
- **Purpose**: FastAPI-based RAG flow (no SQLite), PyMuPDFLoader PDF parsing, OpenAI embeddings, state persisted via JSON index, Next.js API → FastAPI forwarding

## Changes Summary
This branch transforms the application into a comprehensive Kids Science Tutor with persistent RAG functionality:

### Backend (FastAPI) & RAG Changes
- ✅ **FastAPI RAG Backend**: Consolidated RAG to Python FastAPI (`api/app.py`)
- ✅ **PDF Parsing with PyMuPDFLoader**: Robust text extraction via LangChain `PyMuPDFLoader`
- ✅ **Chunking**: `CharacterTextSplitter` for clean, overlapping chunks
- ✅ **OpenAI Embeddings**: Uses `text-embedding-3-small`
- ✅ **State Persistence (No SQLite)**: RAG documents + embeddings saved/loaded via JSON index at `/tmp/rag_index.json` (`save_state`/`load_state`)
- ✅ **Next.js → FastAPI**: Frontend API routes forward to FastAPI for upload, status, and chat
- ✅ **Env-based API Key**: Reads `OPENAI_API_KEY` from environment

### Kids Science Tutor Features
- ✅ **Kid Login System**: Name + PIN authentication (`/login`)
- ✅ **Reading Sessions**: Dynamic content from vector search, 30-line chunks, 5-minute timer
- ✅ **Adaptive Quizzing**: OpenAI-generated questions from PDF content, tracks previous questions
- ✅ **Progress Tracking**: Topics completed, quiz scores, session history
- ✅ **Parent Reports**: Comprehensive progress dashboard (`/report/[kidId]`)
- ✅ **10 Grade-3 Science PDFs**: Auto-generated content (Planets, Constellations, Rocks, etc.)

### Admin & RAG Features  
- ✅ **PDF Upload System**: Uploads forwarded to FastAPI; text extracted, chunked, embedded
- ✅ **Vector Store (In-Memory + JSON Index)**: Cosine similarity over embeddings; index saved to `/tmp/rag_index.json`
- ✅ **RAG Status**: `/api/rag-status` (FastAPI + Next.js forwarder)
- ✅ **Health Monitoring**: `/api/health`
- ✅ **Landing Page**: Admin tools, system health, Kids Tutor navigation

### Technical Improvements
- ✅ **File Organization**: Moved `lib/db.ts` to `frontend/lib/db.ts` for better Next.js integration
- ✅ **Import Path Fixes**: Corrected all relative imports across API routes
- ✅ **Error Handling**: Comprehensive logging and error recovery
- ✅ **UI Fixes**: Quiz option text visibility, responsive design improvements

## Merge Options

### New Branch: feature/certification-challenge

This branch introduces the Certification Challenge scaffold alongside existing work:
- Adds `projects/diagnostician-agent/` with `graph/`, `retriever/`, `eval/`, `tests/`, and `README.md`.
- Adds Next.js API route `frontend/src/app/api/diagnostician/route.ts`.
- Adds minimal quiz UI `frontend/src/app/quiz/page.tsx`.

Create a PR targeting `main`:
```bash
git push origin feature/certification-challenge
gh pr create --base main --head feature/certification-challenge \
  --title "Certification Challenge: diagnostician scaffold" \
  --body "Adds diagnostician agent scaffold with API and quiz page."
```
Merge via GitHub UI or:
```bash
gh pr merge --squash --auto
```

### Option 1: GitHub Pull Request (Recommended)

#### Step 1: Push the feature branch
```bash
git push origin feature/rag-persistence-and-bees
```

#### Step 2: Create Pull Request
1. Go to your GitHub repository
2. Click "Compare & pull request" for the `feature/rag-persistence-and-bees` branch
3. Fill in the PR details:
- **Title**: "FastAPI RAG: PyMuPDFLoader, JSON index persistence, Next.js forwarding"
- **Description**: Copy the changes summary from above
4. Assign reviewers if needed
5. Click "Create pull request"

#### Step 3: Review and Merge
1. Review the changes in the GitHub interface
2. Run any automated tests/checks
3. Click "Merge pull request" 
4. Choose merge type:
   - **"Create a merge commit"** - Preserves branch history
   - **"Squash and merge"** - Combines all commits into one clean commit
   - **"Rebase and merge"** - Replays commits without merge commit
5. Confirm the merge
6. Delete the feature branch after successful merge

### Option 2: GitHub CLI (Command Line)

#### Prerequisites
```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Authenticate with GitHub
gh auth login
```

#### Step 1: Push and create PR
```bash
# Push the feature branch
git push origin feature/rag-persistence-and-bees

# Create pull request via CLI
gh pr create \
  --title "FastAPI RAG: PyMuPDFLoader, JSON index persistence, Next.js forwarding" \
  --body "Consolidate RAG in FastAPI, switch to PyMuPDFLoader, add CharacterTextSplitter, persist RAG state to /tmp/rag_index.json (no SQLite), and forward Next.js API routes to FastAPI for upload/status/chat." \
  --base main \
  --head feature/rag-persistence-and-bees
```

#### Step 2: Review and merge via CLI
```bash
# View the PR
gh pr view

# Merge the PR (choose one option):
# Option A: Merge commit
gh pr merge --merge

# Option B: Squash merge (recommended for feature branches)
gh pr merge --squash

# Option C: Rebase merge
gh pr merge --rebase
```

#### Step 3: Cleanup
```bash
# Delete the feature branch locally
git branch -d feature/rag-persistence-and-bees

# Delete the remote feature branch
git push origin --delete feature/rag-persistence-and-bees
```

## Post-Merge Verification

After merging, verify the deployment works correctly:

1. **Check Vercel Deployment**: Ensure the app redeploys automatically
2. **Test Core Functionality**:
   ```bash
   curl -s https://your-app.vercel.app/api/health
   curl -s https://your-app.vercel.app/api/kids/login -d '{"name":"Test","pin":"1234"}'
   ```
3. **Test Kids Tutor Flow**: 
   - Visit `/login` and create a test kid
   - Start a reading session at `/read/[kidId]`
   - Complete quiz and check progress at `/report/[kidId]`
4. **Test Admin Features**:
   - Upload a PDF via the landing page
   - Use "Rebuild Vector DB" button
   - Check system health endpoint

## Rollback Plan (If Issues Occur)

If problems arise after merging:

```bash
# Find the merge commit hash
git log --oneline -10

# Revert the merge commit
git revert -m 1 <merge-commit-hash>

# Push the revert
git push origin main
```

## Notes
- **Storage**: RAG state saved to `/tmp/rag_index.json` (ephemeral in serverless; persists during process lifecycle). No SQLite.
- **Auto-Initialization**: Upload PDFs manually or via UI; RAG state persists via JSON save/load
- **Environment Variables**: `OPENAI_API_KEY` required for embeddings and chat
- **PDF Parsing**: Uses `PyMuPDFLoader`; chunking via `CharacterTextSplitter`

---
**Created**: September 23, 2025  
**Author**: AI Assistant  
**Branch**: feature/activity-2-kids-tutor-quiz → main
