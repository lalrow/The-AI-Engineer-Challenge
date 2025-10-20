from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
import os
import json
import numpy as np
from backend.search_client import search_top_k

@tool
def retriever_tool(query: str, api_key: str) -> str:
    """Retrieve relevant context from Qdrant vector database for science curriculum questions."""
    docs = search_top_k(query, k=4, api_key=api_key)
    return "\n\n".join([d.page_content for d in docs])

def retrieve_context(state):
    """Retrieve top-k relevant text from Qdrant (R step of RAG)."""
    if state.get("context"): # Only retrieve if context is empty
        return state
    try:
        docs = search_top_k(state["question"], k=4, api_key=state.get("api_key"))
        context = "\n\n".join([d.page_content for d in docs])
        
        # Future-proof: signal if retrieval fails
        if not context or context.strip() == "":
            state["context"] = "Qdrant retrieval returned empty. Tavily available for fallback."
        else:
            state["context"] = context
            
    except Exception as e:
        state["context"] = f"Error retrieving context: {e}. Tavily fallback available."
    return state


def diagnose_node(state):
    """Evaluate answer using semantic similarity (same as retrieval test)."""
    question = state.get("question", "")
    answer = state.get("answer", "")
    context = state.get("context", "")
    api_key = state.get("api_key")

    # Compute similarity score using embeddings (same as test_retrieval_similarity.py)
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key or os.getenv("OPENAI_API_KEY")
    )
    
    # Get embeddings for answer and context
    answer_embedding = embeddings.embed_query(answer)
    context_embedding = embeddings.embed_query(context)
    
    # Compute cosine similarity
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    similarity_score = cosine_similarity(answer_embedding, context_embedding)
    
    # Use LLM for qualitative feedback based on similarity score
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
    )

    prompt = f"""You are a science diagnostician agent. The student's answer has been evaluated with a similarity score of {similarity_score:.3f} against the reference context.

Student Question: {question}
Student Answer: {answer}
Reference Context: {context}
Similarity Score: {similarity_score:.3f}

Based on this score:
- 0.8-1.0: Excellent, comprehensive answer aligned with context
- 0.6-0.8: Good answer with some alignment to context
- 0.4-0.6: Acceptable but basic answer, missing key details from context
- Below 0.4: Answer needs significant improvement

Provide qualitative feedback in this JSON structure (no markdown):
{{
  "evaluation": "<brief assessment explaining why the score is {similarity_score:.3f}>",
  "next_step": "<suggested follow-up question or activity>",
  "feedback": "<constructive feedback for improving the answer>"
}}"""

    result = llm.invoke(prompt).content

    try:
        parsed = json.loads(result)
    except Exception:
        # Attempt to clean and parse if it's wrapped in markdown
        try:
            cleaned_result = result.replace("```json\n", "").replace("\n```", "")
            parsed = json.loads(cleaned_result)
        except Exception:
            parsed = {
                "evaluation": "Could not parse LLM response.",
                "next_step": "Retry with clearer instructions.",
                "feedback": "Agent output could not be parsed.",
            }
    
    # Add the similarity score to the response
    parsed["score"] = float(similarity_score)
    
    state["agent_response"] = parsed
    return state


def build_graph_with_api_key(api_key: str):
    # --- Tool Belt: Qdrant Retriever + Tavily Fallback ---
    from langchain_community.tools.tavily_search import TavilySearchResults
    
    tavily_tool = TavilySearchResults(
        max_results=5,
        api_key=os.getenv("TAVILY_API_KEY")
    )
    tool_belt = [retriever_tool, tavily_tool]
    
    # Bind tools to model (makes them available for future use)
    model_with_tools = ChatOpenAI(
        model="gpt-4.1-mini", 
        temperature=0,
        api_key=api_key
    ).bind_tools(tool_belt)
    
    # Continue with existing graph definition...
    graph = StateGraph(dict)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("diagnose", diagnose_node)
    graph.set_entry_point("retrieve_context")
    graph.add_edge("retrieve_context", "diagnose")
    graph.add_edge("diagnose", END)
    return graph.compile(checkpointer=MemorySaver())

# Remove for backward compatibility - no longer needed with explicit API key in FastAPI
# agent_graph = build_graph()
