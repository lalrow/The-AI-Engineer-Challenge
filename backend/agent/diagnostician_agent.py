from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
import os


def diagnose_node(state):
    """Agent node to evaluate student's answer and plan next diagnostic step."""
    question = state.get("question", "")
    answer = state.get("answer", "")
    context = state.get("context", "")
    api_key = state.get("api_key")
    
    # Use provided API key or fall back to environment variable
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0.2,
        api_key=api_key if api_key else os.getenv("OPENAI_API_KEY")
    )

    prompt = f"""You are a science diagnostician agent. Evaluate the student's answer and return ONLY valid JSON (no markdown).

Student Question: {question}
Student Answer: {answer}
Context: {context}

Return this exact JSON structure:
{{
  "score": <float between 0.0 and 1.0>,
  "evaluation": "<brief assessment>",
  "next_step": "<suggested follow-up question or activity>",
  "feedback": "<constructive feedback for the student>"
}}"""

    result = llm.invoke(prompt)
    state["agent_response"] = result.content
    return state


def build_graph():
    """Build graph with environment-based API key (backward compatibility)"""
    graph = StateGraph(dict)
    graph.add_node("diagnose", diagnose_node)
    graph.set_entry_point("diagnose")
    graph.add_edge("diagnose", END)
    return graph.compile()


def build_graph_with_api_key(api_key: str):
    """Build graph with explicit API key"""
    graph = StateGraph(dict)
    graph.add_node("diagnose", diagnose_node)
    graph.set_entry_point("diagnose")
    graph.add_edge("diagnose", END)
    return graph.compile()


# Keep for backward compatibility
agent_graph = build_graph()
