from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


def diagnose_node(state):
    """Agent node to evaluate student's answer and plan next diagnostic step."""
    question = state.get("question", "")
    answer = state.get("answer", "")
    context = state.get("context", "")

    prompt = f"""
    You are a science diagnostician agent.
    Student Question: {question}
    Student Answer: {answer}
    Context: {context}
    Return JSON with fields: 'evaluation', 'next_step', 'feedback'.
    """

    result = llm.invoke(prompt)
    state["agent_response"] = result.content
    return state


def build_graph():
    graph = StateGraph(dict)
    graph.add_node("diagnose", diagnose_node)
    graph.set_entry_point("diagnose")
    graph.add_edge("diagnose", END)
    return graph.compile()


agent_graph = build_graph()
