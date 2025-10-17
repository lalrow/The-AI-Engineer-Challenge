# Agent Similarity Scoring Implementation

## Problem
The diagnostician agent was using **LLM-based subjective scoring**, which gave inconsistent results compared to the retrieval similarity test. The baseline answer (basic definition) was receiving 0.9 score instead of ~0.57.

## Solution
Updated the agent to use **semantic similarity scoring** (cosine similarity between embeddings) - the same technique as `test_retrieval_similarity.py`.

## Changes Made

### File: `backend/agent/diagnostician_agent.py`

1. **Added imports:**
   - `OpenAIEmbeddings` from langchain_openai
   - `numpy` for cosine similarity calculation

2. **Updated `diagnose_node()` function:**
   - Computes embeddings for student answer and retrieved context
   - Calculates cosine similarity score (0.0-1.0)
   - Uses LLM only for qualitative feedback based on the similarity score
   - Returns objective similarity score instead of subjective LLM judgment

## Results

### Agent Scoring (Similarity-Based)
- **Baseline Answer**: 0.530 score
- **Grounded Answer**: 0.864 score

### Retrieval Test Scoring (Cosine Similarity)
- **Baseline Answer**: 0.572 similarity
- **Grounded Answer**: 0.914 similarity

### Comparison
| Answer Type | Agent Score | Retrieval Test | Difference |
|-------------|-------------|----------------|------------|
| Baseline    | 0.530       | 0.572          | -0.042     |
| Grounded    | 0.864       | 0.914          | -0.050     |

The scores are now **consistent and objective**, with minor variations due to:
- Agent compares answer vs full retrieved context
- Retrieval test compares answer vs concatenated top-2 chunks
- Different chunk combinations may produce slightly different embeddings

## Benefits

✅ **Consistent Scoring**: Frontend and agent now use the same evaluation technique
✅ **Objective Evaluation**: Based on mathematical similarity, not LLM interpretation
✅ **Predictable Results**: Same answer will get similar scores across different runs
✅ **Better Differentiation**: Basic answers (~0.53) vs detailed answers (~0.86)
✅ **All Tests Pass**: Maintains compatibility with existing test suite

## Score Interpretation

- **0.8-1.0**: Excellent, comprehensive answer aligned with context
- **0.6-0.8**: Good answer with some alignment to context  
- **0.4-0.6**: Acceptable but basic answer, missing key details from context
- **Below 0.4**: Answer needs significant improvement

## Technical Details

The similarity scoring works by:
1. Retrieving top-k relevant chunks from Qdrant (RAG retrieval step)
2. Concatenating retrieved chunks into context string
3. Generating embeddings for student answer using `text-embedding-3-small`
4. Generating embeddings for retrieved context using same model
5. Computing cosine similarity: `dot(a, b) / (||a|| * ||b||)`
6. Using LLM to provide qualitative feedback based on the numeric score

This ensures the evaluation is grounded in semantic similarity between the student's answer and the knowledge base.

## Session Summary (Chat History)

- Initialized persistent Qdrant at `QDRANT_URL=./qdrant_local`; loaded 11 Grade 3 PDFs (incl. Bees_and_Pollination.pdf).
- Started backend FastAPI (`uv run python api/app.py`), resolved port 8000 conflicts by killing prior processes.
- Verified `/api/search` and `/api/evaluate` endpoints; ensured `.env` keys loaded.
- Ran tests multiple times:
  - `tests/test_diagnostician_agent.py`
  - `tests/test_diagnostician_agent_evaluation.py`
  - `tests/test_retrieval_similarity.py`
- Debugged mismatch where frontend scored baseline ~0.9; root cause: agent used LLM-only judgment.
- Implemented Agentic RAG with objective similarity scoring (embeddings cosine similarity) to align with retrieval test.
- Restarted backend; killed and restarted frontend on request; re-ran tests until all green (3/3).
- Confirmed end-to-end: retriever → embeddings → Qdrant search → similarity scoring → LLM feedback.

### We must use RAG
- Retrieval from Qdrant is mandatory before evaluation.
- Similarity score is computed between the student's answer and retrieved context.
- LLM is used only for qualitative feedback (grounded, not replacing the numeric score).

### Results Comparison

| Method | Baseline Score | Grounded Score |
|---|---:|---:|
| Retrieval Test | 0.572 | 0.914 |
| Updated Agent | 0.530 | 0.864 |
| Difference | -0.042 | -0.050 |

