<!-- 74738cbf-a058-47c6-8b97-819bc3cc66b9 c974f046-6808-412e-b0ef-94d5043ad338 -->
# Wire Retriever to Diagnostician API

## Architecture

- **Retriever Module (Python)**: Update existing `load_pdf_to_qdrant.py` to use `RecursiveCharacterTextSplitter` and structured metadata
- **FastAPI Search Endpoint**: Add `/api/search` to query Qdrant and return top-k chunks
- **Diagnostician API**: Update Next.js route to call FastAPI search, then evaluate with grounded context

## Step 1: Update Python Retriever Script

**File**: `projects/diagnostician-agent/retriever/load_pdf_to_qdrant.py`

Changes:

- Replace `chunk_text()` with LangChain's `RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)`
- Add environment variables: `QDRANT_URL` (defaults to `:memory:`), `COLLECTION_NAME` (defaults to `science_curriculum_g3_g6`)
- Update metadata to include `{"topic": "pollination", "grade": 3, "strand": "life systems"}`
- Print total chunks inserted with collection name

## Step 2: Add FastAPI Search Endpoint

**File**: `api/app.py`

Add new endpoint `/api/search`:

```python
@app.post("/api/search")
async def search_qdrant(request: SearchRequest):
    # SearchRequest: query (str), top_k (int, default 4), api_key (str)
    # 1. Generate query embedding using OpenAI
    # 2. Search Qdrant collection for top_k results
    # 3. Return [{"text": chunk, "score": similarity, "metadata": {...}}]
```

Requires:

- `SearchRequest` Pydantic model with `query`, `top_k`, `api_key`
- Qdrant client initialization (reuse or create in-memory instance)
- OpenAI embedding generation for query

## Step 3: Update Diagnostician API Route

**File**: `frontend/src/app/api/diagnostician/route.ts`

Changes:

1. Accept `{ apiKey, question, answer }` (remove hardcoded `context`)
2. Call `http://localhost:8000/api/search` with `{query: question, top_k: 4, api_key: apiKey}`
3. Build context string from search results: `results.map(r => r.text).join('\n\n')`
4. Update OpenAI prompt:
```
Use the provided context to evaluate if the student's answer is correct.

Context:
${context}

Question: ${question}
Student Answer: ${answer}

Return JSON: {"score": 0-1, "feedback": "brief explanation"}
```

5. Parse JSON response and return `{ evaluation: {score, feedback}, sources: results }`

## Step 4: Update Quiz UI

**File**: `frontend/src/app/quiz/page.tsx`

Changes:

- Remove hardcoded `context` field and state
- Update `handleSubmit` to send only `{ apiKey, question, answer }`
- Display sources in result section if available

## Testing

### Test Retriever

```bash
export OPENAI_API_KEY=sk-...
uv run python projects/diagnostician-agent/retriever/load_pdf_to_qdrant.py \
  --pdf ./public/pdfs/grade3/bees.pdf
```

### Test Search Endpoint

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"What is pollination?","top_k":4,"api_key":"sk-..."}'
```

### Test End-to-End

```bash
curl -X POST http://localhost:3000/api/diagnostician \
  -H "Content-Type: application/json" \
  -d '{"apiKey":"sk-...","question":"What is pollination?","answer":"Transfer of pollen"}'
```

Expected: `{"evaluation":{"score":0.9,"feedback":"..."},"sources":[...]}`

### To-dos

- [ ] Update load_pdf_to_qdrant.py with RecursiveCharacterTextSplitter and metadata
- [ ] Add /api/search endpoint to FastAPI (api/app.py)
- [ ] Update diagnostician route.ts to call search and use grounded context
- [ ] Remove context field from quiz page and display sources
- [ ] Test PDF ingestion into Qdrant
- [ ] Test FastAPI search endpoint
- [ ] Test full diagnostician flow with retrieval