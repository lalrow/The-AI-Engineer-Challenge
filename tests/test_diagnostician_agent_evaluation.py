import os
import sys
import json
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from backend.agent.diagnostician_agent import build_graph_with_api_key

# For testing, use your real or dummy key
DUMMY_API_KEY = os.getenv("OPENAI_API_KEY", "test-api-key")

def run_agent(question, answer, context):
    """Helper to invoke the Diagnostician Agent graph."""
    agent_graph = build_graph_with_api_key(DUMMY_API_KEY)
    result = agent_graph.invoke(
        {
            "question": question,
            "answer": answer,
            "context": context,
            "api_key": DUMMY_API_KEY,
        },
        config={"configurable": {"thread_id": "test-thread-001"}}
    )
    return result.get("agent_response", {})

def test_diagnostician_agent_evaluation():
    # === Load baseline & grounded answers ===
    baseline_answer = open("tests/baseline_answer.txt").read().strip()
    grounded_answer = open("tests/grounded_answer.txt").read().strip()

    # === Common question + context (same as retrieval test) ===
    question = "What is pollination?"
    context = (
        "Pollination allows plants to make seeds and fruits. "
        "After finishing with one flower, the bee zips to another. "
        "Some of the pollen from her body rubs off onto the second flower."
    )

    print("\n🧪 Running Diagnostician Agent Evaluation Test...")

    # === Evaluate baseline answer ===
    baseline_result = run_agent(question, baseline_answer, context)
    print("Baseline Result:", json.dumps(baseline_result, indent=2))

    # === Evaluate grounded answer ===
    grounded_result = run_agent(question, grounded_answer, context)
    print("Grounded Result:", json.dumps(grounded_result, indent=2))

    # === Assertions ===
    for key in ["score", "evaluation", "next_step", "feedback"]:
        assert key in baseline_result, f"Missing '{key}' in baseline result"
        assert key in grounded_result, f"Missing '{key}' in grounded result"

    # Check numeric ranges
    assert 0.0 <= baseline_result["score"] <= 1.0
    assert 0.0 <= grounded_result["score"] <= 1.0

    # Expect grounded > baseline
    print(f"🔍 Scores: baseline={baseline_result["score"]:.2f}, grounded={grounded_result["score"]:.2f}")
    assert grounded_result["score"] > baseline_result["score"], "Grounded score should be higher"

    # Optional: ensure they roughly align with retrieval similarity thresholds
    assert baseline_result["score"] >= 0.4, "Baseline score too low (<0.4)"
    assert grounded_result["score"] >= 0.8, "Grounded score too low (<0.8)"

    print("✅ Diagnostician Agent Evaluation Test passed successfully!")
