import os
import sys
import json
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from backend.agent.diagnostician_agent import build_graph_with_api_key

# For testing, we can use a dummy API key
DUMMY_API_KEY = os.getenv("OPENAI_API_KEY", "test-api-key")

def test_diagnostician_agent_evaluation():
    input_state = {
        "question": "Why do bees visit flowers?",
        "answer": "Because they collect pollen.",
        "context": "Bees visit flowers to collect nectar and pollen for food. Pollination happens as pollen moves between flowers.",
        "api_key": DUMMY_API_KEY # Pass API key in state for agent
    }

    agent_graph = build_graph_with_api_key(DUMMY_API_KEY)
    result = agent_graph.invoke(input_state, config={"configurable": {"thread_id": "test_thread"}})
    agent_response = result.get("agent_response", {})

    assert isinstance(agent_response, dict)
    assert "score" in agent_response
    assert "evaluation" in agent_response
    assert "next_step" in agent_response
    assert "feedback" in agent_response
    assert 0.0 <= agent_response["score"] <= 1.0
    # Further assertions can be added here to check content of evaluation, next_step, feedback
