# Merge Instructions: RAGAS Evaluation Integration

## Branch Information
- **Feature Branch:** `feature/certification-challenge`
- **Target Branch:** `main`
- **Feature:** RAGAS-based evaluation framework for Diagnostician Agent

## What Was Added

This feature adds comprehensive RAGAS evaluation to quantify RAG pipeline quality using Session 8 methodology:

### Files Added
- `tests/evals/baseline_eval.csv` - 5 minimal answer examples for baseline evaluation
- `tests/evals/grounded_eval.csv` - 5 detailed contextually-grounded answer examples
- `tests/evals/run_ragas_eval.py` - Main RAGAS evaluation script
- `tests/evals/README.md` - Comprehensive usage documentation
- `tests/evals/baseline_ragas_results.csv` - Generated baseline evaluation results
- `tests/evals/grounded_ragas_results.csv` - Generated grounded evaluation results
- `tests/evals/phase2_ragas_comparison.csv` - Comparison metrics with deltas

### Files Modified
- `pyproject.toml` - Added `ragas==0.2.10` and `datasets>=2.0.0` dependencies

### Metrics Evaluated
- **Faithfulness** - Is the answer grounded in retrieved context?
- **Context Recall** - Does context cover what's in ground truth?
- **Context Precision** - Are retrieved chunks relevant to the question?
- **Answer Relevancy** - Is answer semantically aligned with question?

## How to Run

After merging, you can run the RAGAS evaluation with:

```bash
uv sync
uv run python tests/evals/run_ragas_eval.py
```

Expected runtime: 2-5 minutes

## Merge Options

### Option 1: GitHub Pull Request (Recommended)

1. **Push the feature branch:**
   ```bash
   git push origin feature/certification-challenge
   ```

2. **Create PR via GitHub UI:**
   - Go to: https://github.com/YOUR_USERNAME/The-AI-Engineer-Challenge
   - Click "Compare & pull request"
   - Title: "Add RAGAS Evaluation Framework for Diagnostician Agent"
   - Description: Reference this MERGE.md file
   - Click "Create pull request"

3. **Review and merge:**
   - Review the changes in GitHub UI
   - Check that CI passes (if configured)
   - Click "Merge pull request"
   - Select merge strategy (recommend "Squash and merge" for clean history)
   - Confirm merge

### Option 2: GitHub CLI (Fast)

1. **Push the feature branch:**
   ```bash
   git push origin feature/certification-challenge
   ```

2. **Create and merge PR:**
   ```bash
   # Create PR
   gh pr create \
     --title "Add RAGAS Evaluation Framework for Diagnostician Agent" \
     --body "$(cat MERGE.md)" \
     --base main \
     --head feature/certification-challenge
   
   # Review PR (optional)
   gh pr view
   
   # Merge PR (after review)
   gh pr merge --squash --delete-branch
   ```

### Option 3: Local Merge (Quick)

⚠️ **Warning:** Only use if you're the sole contributor and don't need code review.

```bash
# Switch to main branch
git checkout main

# Merge feature branch
git merge feature/certification-challenge --no-ff

# Delete feature branch (optional)
git branch -d feature/certification-challenge

# Push to origin
git push origin main
```

## Testing After Merge

Verify the integration works:

```bash
# 1. Sync dependencies
uv sync

# 2. Run RAGAS evaluation
uv run python tests/evals/run_ragas_eval.py

# 3. Verify output files created
ls -lh tests/evals/*.csv

# 4. Run existing tests to ensure no regression
uv run pytest tests/test_retrieval_similarity.py
uv run pytest tests/test_diagnostician_agent_evaluation.py
```

## Integration with Phase 2

The `phase2_ragas_comparison.csv` file contains key metrics for Phase 2 reporting:

```csv
Metric,Baseline,Grounded,Δ (Improvement)
faithfulness,0.867,0.876,+0.010
context_recall,0.933,0.633,-0.300
context_precision,1.000,1.000,+0.000
answer_relevancy,0.751,0.729,-0.022
```

These metrics demonstrate:
- Quantitative evaluation of RAG pipeline quality
- Comparison between baseline and grounded answers
- Session 8 methodology applied to Diagnostician Agent

## Dependencies Added

- **ragas==0.2.10** - Evaluation framework from Session 8
- **datasets>=2.0.0** - Required by RAGAS for dataset handling
- **pandas** (already present) - For CSV handling
- **numpy** (already present) - For computing metric averages

## Notes

- This is eval-only scope - no changes to agent code
- Builds on existing `test_retrieval_similarity.py` and `test_diagnostician_agent_evaluation.py`
- Aligns with methodology from `AGENT_SIMILARITY_SCORING.md`
- Ready for Phase 2 Loom demo

## Questions?

See `tests/evals/README.md` for detailed usage instructions and metric interpretations.


## Database details 
1. 📘 Source of Truth for Qdrant

Cursor must always read the file MERGE.md (or QDRANT_CONFIG.md if renamed) before running or editing any scripts related to Qdrant.

That file defines the single Qdrant instance location.

Never create or use:

:memory: databases

Docker Qdrant instances

Cloud-hosted Qdrant URLs

✅ Only use local persistent Qdrant (e.g., http://localhost:6333 or local directory path).
