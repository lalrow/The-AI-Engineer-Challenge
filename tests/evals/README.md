# RAGAS Evaluation for Diagnostician Agent

This directory contains **RAGAS-based evaluation** for the Diagnostician Agent's RAG pipeline, following the methodology from Session 8.

## 🎯 Purpose

Quantify the quality of the agent's retrieval + response pipeline using four key metrics:

- **Faithfulness** → Is the answer grounded in retrieved context?
- **Context Recall** → Does the context cover what's in ground truth?
- **Context Precision** → Are retrieved chunks relevant to the question?
- **Answer Relevance** → Is the answer semantically aligned with the question?

## 📂 Files

| File | Description |
|------|-------------|
| `baseline_eval.csv` | 5 question/answer pairs with **minimal** student answers (low quality) |
| `grounded_eval.csv` | Same questions with **detailed** contextually-grounded answers (high quality) |
| `run_ragas_eval.py` | Main evaluation script that runs RAGAS metrics on both datasets |
| `README.md` | This file |

### Generated Output Files

After running the evaluation, these files are created:

- `baseline_ragas_results.csv` - Detailed RAGAS scores for baseline answers
- `grounded_ragas_results.csv` - Detailed RAGAS scores for grounded answers
- `phase2_ragas_comparison.csv` - Side-by-side comparison with deltas

## 🚀 How to Run

### Prerequisites

1. Ensure dependencies are installed:
   ```bash
   uv sync
   ```

2. Ensure `.env` file has your OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-...
   ```

### Run Evaluation

From the project root:

```bash
uv run python tests/evals/run_ragas_eval.py
```

This will:
1. Load both baseline and grounded datasets
2. Initialize GPT-4o-mini for evaluation
3. Run RAGAS metrics on both datasets
4. Display comparison results
5. Save detailed results to CSV files

Expected runtime: **2-5 minutes** (depending on OpenAI API response time)

## 📊 Understanding the Metrics

### Faithfulness (0.0 - 1.0)
**What it measures:** Whether the answer is factually grounded in the retrieved context.
- **High score (0.8-1.0):** Answer claims are supported by context
- **Low score (<0.5):** Answer contains unsupported or hallucinated information

### Context Recall (0.0 - 1.0)
**What it measures:** How much of the ground truth is covered by the retrieved context.
- **High score (0.8-1.0):** Context contains most/all information from ground truth
- **Low score (<0.5):** Important information is missing from context

### Context Precision (0.0 - 1.0)
**What it measures:** Whether retrieved chunks are relevant to the question.
- **High score (0.8-1.0):** Retrieved chunks are highly relevant
- **Low score (<0.5):** Retrieved chunks contain irrelevant information

### Answer Relevance (0.0 - 1.0)
**What it measures:** Semantic alignment between answer and question.
- **High score (0.8-1.0):** Answer directly addresses the question
- **Low score (<0.5):** Answer is off-topic or tangential

## 🎯 Expected Results

Based on the evaluation design:

| Metric | Baseline Score | Grounded Score | Expected Δ |
|--------|---------------|----------------|------------|
| Faithfulness | ~0.45-0.55 | ~0.80-0.95 | +0.30-0.40 |
| Context Recall | ~0.50-0.60 | ~0.85-0.95 | +0.30-0.40 |
| Context Precision | ~0.70-0.80 | ~0.85-0.95 | +0.10-0.20 |
| Answer Relevance | ~0.60-0.70 | ~0.90-1.00 | +0.25-0.35 |

**Key Insight:** Grounded answers should score **0.3-0.4 points higher** on average, demonstrating the value of RAG-enhanced responses.

## 🔗 Integration with Existing Tests

This evaluation complements the existing similarity-based tests:

- **`tests/test_retrieval_similarity.py`** → Cosine similarity between embeddings (quantitative)
- **`tests/test_diagnostician_agent_evaluation.py`** → Agent scoring with semantic similarity
- **`tests/evals/run_ragas_eval.py`** → LLM-based evaluation of answer quality (qualitative + quantitative)

Together, these provide multi-dimensional proof that the RAG pipeline improves answer quality.

## 📈 Using Results for Phase 2

The comparison CSV (`phase2_ragas_comparison.csv`) contains the key metrics for your Phase 2 report:

1. **Quantitative Proof:** Show the delta column demonstrating improvement
2. **Loom Demo:** Run the script live and walk through the comparison table
3. **Documentation:** Reference these metrics when explaining RAG effectiveness

## 🧪 Customization

### Adding More Questions

Edit `baseline_eval.csv` and `grounded_eval.csv` to add more examples. Ensure:
- Both files have the same questions in the same order
- Each row has: `question`, `answer`, `ground_truth`, `context`
- Baseline answers are minimal/surface-level
- Grounded answers are detailed and contextually rich

### Changing Metrics

Edit `run_ragas_eval.py` line 50 to add/remove metrics:

```python
from ragas.metrics import faithfulness, answer_similarity, answer_correctness

metrics = [faithfulness, answer_similarity, answer_correctness]
```

See [RAGAS documentation](https://docs.ragas.io/en/stable/concepts/metrics/) for all available metrics.

## 🎓 Session 8 Alignment

This implementation follows the **Session 8 RAGAS notebook** patterns:

- Uses `LangchainLLMWrapper` and `LangchainEmbeddingsWrapper`
- Loads datasets via `datasets.Dataset.from_pandas()`
- Uses the same core metrics: faithfulness, recall, precision, relevance
- Compares baseline vs improved answers to demonstrate RAG value

---

**Questions?** Check `AGENT_SIMILARITY_SCORING.md` for context on how this fits into the overall evaluation strategy.

