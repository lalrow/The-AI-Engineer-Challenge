import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from backend.agent.diagnostician_agent import agent_graph

if __name__ == "__main__":
    input_state = {
        "question": "Why do bees visit flowers?",
        "answer": "Because they collect pollen.",
        "context": "Bees visit flowers to collect nectar and pollen for food. Pollination happens as pollen moves between flowers."
    }

    result = agent_graph.invoke(input_state)
    print(result["agent_response"])
