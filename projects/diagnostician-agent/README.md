# Foundational Skill Diagnostician Agent
Part of AI Makerspace Certification Challenge

## What is this?
Lightweight diagnostician that evaluates short free-form answers using OpenAI and a clean Next.js API route. Optional retriever scaffold is included for future RAG.

## Quick Start
1) Set env for frontend
```
cd frontend
echo "OPENAI_API_KEY=your_key_here" > .env.local
npm run dev
```
Visit http://localhost:3000/quiz

2) Call API directly
```
curl -s http://localhost:3000/api/diagnostician \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is pollination?","answer":"transfer of pollen","context":"Pollination enables seeds"}'
```

## Files
- API route: `frontend/src/app/api/diagnostician/route.ts`
- Minimal UI: `frontend/src/app/quiz/page.tsx`
- Retriever (optional): `projects/diagnostician-agent/retriever/load_pdf_to_qdrant.py`
- Eval examples: `projects/diagnostician-agent/eval/examples.json`
- Eval runner: `projects/diagnostician-agent/eval/run.ts`

## Retriever Scaffold (optional)
Embeds PDF chunks using SemanticChunker and upserts into persistent Qdrant (./qdrant_local).
```
export OPENAI_API_KEY=your_key_here
uv run python projects/diagnostician-agent/retriever/load_pdf_to_qdrant.py \
  --pdf ./public/pdfs/grade3/bees.pdf
```

Per MDC rules: Uses persistent Qdrant only (never :memory:, Docker, or cloud URLs).

## Eval Harness
With frontend running on port 3000:
```
FRONTEND_BASE_URL=http://localhost:3000 npx ts-node projects/diagnostician-agent/eval/run.ts
```

## Deploy
Ensure Vercel has `OPENAI_API_KEY` set. `/quiz` and `/api/diagnostician` work on preview/prod.
