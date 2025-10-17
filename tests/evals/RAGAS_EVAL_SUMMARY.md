## RAGAS Evaluation Summary – Diagnostician Agent (Phase 2)

### Scope
- Evals-only integration using RAGAS; no changes to agent logic, APIs, retriever, or frontend.
- Added datasets, evaluation script, docs, and deps to support standalone runs.

### What Was Added
- `tests/evals/baseline_eval.csv` (10 Q/A pairs with minimal answers)
- `tests/evals/grounded_eval.csv` (10 Q/A pairs with grounded answers)
- `tests/evals/run_ragas_eval.py` (RAGAS evaluation script with validation)
- `tests/evals/README.md` (methodology, how-to, metric explanations)
- `tests/evals/RAGAS_EVAL_SUMMARY.md` (this file)
- Outputs: `baseline_ragas_results.csv`, `grounded_ragas_results.csv`, `phase2_ragas_comparison.csv`
- `pyproject.toml` deps: `ragas==0.2.10`, `datasets>=2.0.0`

### How to Run
```bash
uv sync
uv run python tests/evals/run_ragas_eval.py
```

### Metrics Used (Session 8 alignment)
- Faithfulness: Answer grounded in retrieved context
- Context Recall: Retrieved context covers ground truth
- Context Precision: Retrieved chunks relevant to question
- Answer Relevancy: Answer aligns with question

### Dataset Columns
- `user_input` (question)
- `response` (answer)
- `reference` (ground truth)
- `retrieved_contexts` (list[str] of retrieved chunks)

### Results Snapshot (10-Question Golden Dataset)

| Metric | Baseline | Grounded | Δ (Improvement) | Status |
| --- | ---:| ---:| ---:| :---: |
| faithfulness | 0.950 | 0.929 | -0.021 | ⚠️ |
| context_recall | 0.850 | 0.883 | +0.033 | ✅ |
| context_precision | 1.000 | 1.000 | ±0.000 | ➖ |
| answer_relevancy | 0.787 | 0.887 | +0.099 | ✅ |

**Average Improvement**: +0.028 across all metrics

Notes:
- Dataset contains 10 manually-curated Q/A pairs from "Bees and Pollination" corpus
- Contexts are identical between baseline and grounded datasets
- Baseline answers: 1-2 sentences (minimal)
- Grounded answers: 2-3 sentences (context-integrated)
- Answer relevancy shows strongest improvement (+0.099)
- Context precision perfect (1.0) for both, indicating high-quality retrieval

### Key Script Excerpts
Load data and parse retrieved contexts:
```python
baseline_df = pd.read_csv(baseline_path)
baseline_df['retrieved_contexts'] = baseline_df['retrieved_contexts'].apply(ast.literal_eval)
grounded_df = pd.read_csv(grounded_path)
grounded_df['retrieved_contexts'] = grounded_df['retrieved_contexts'].apply(ast.literal_eval)
```

Initialize LLM + embeddings (matches agent config):
```python
llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))
embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small"))
```

Define metrics and evaluate datasets:
```python
metrics = [faithfulness, context_recall, context_precision, answer_relevancy]
baseline_results = evaluate(dataset=baseline_dataset, metrics=metrics, llm=llm, embeddings=embeddings)
grounded_results = evaluate(dataset=grounded_dataset, metrics=metrics, llm=llm, embeddings=embeddings)
```

Compute metric means and deltas:
```python
baseline_score = np.mean(baseline_results[metric.name])
grounded_score = np.mean(grounded_results[metric.name])
delta = grounded_score - baseline_score
```

### Confirmation: Evals-Only
- No edits to `backend/agent/diagnostician_agent.py`, APIs, or frontend code.
- All additions are confined to `tests/evals/` and dependency updates in `pyproject.toml`.


