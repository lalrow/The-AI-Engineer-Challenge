# Cursor Tasks Management

A concise guide to manage implementation tasks in this repo when using Cursor.

## Core Principles
- Single feature at a time; work on a feature branch
- Commit small, meaningful edits with clear messages
- Keep tasks actionable (verb-led) and ≤ 14 words
- Update status often: pending → in_progress → completed
- Prefer parallel read-only searches; serialize edits

## Typical Task States
- pending: planned, not started
- in_progress: actively working; only one at a time
- completed: finished and verified (tests/docs updated)
- cancelled: no longer needed

## Suggested Workflow
1. Create a feature branch
2. Define todos for the feature
3. Execute tasks; keep one in progress
4. Run tests; lint if needed
5. Commit with context-rich messages
6. Update docs (README/AGENT_SIMILARITY_SCORING.md)
7. Open PR with summary and test results

## Commit Hygiene
- Reference affected files/components
- Summarize impact and user-visible changes
- Note test coverage and any migrations

## Branching
- feature/<short-feature-name>
- fix/<short-bug-name>
- docs/<short-docs-topic>

## PR Template (TL;DR)
- What: brief summary
- Why: problem addressed
- How: high-level changes
- Tests: results and scope
- Risk: known risks/rollbacks

## Useful Commands
- Start backend: `uv run python api/app.py`
- Run tests: `uv run pytest -v`
- Load PDFs to Qdrant: see `.cursor/preflight.qdrant`
- Set Qdrant path: `QDRANT_URL=./qdrant_local`

## Notes
- Always load `.env` before backend tasks
- Avoid dummy API keys; use real `OPENAI_API_KEY`
- Keep Qdrant populated with grade3 PDFs before evaluations
