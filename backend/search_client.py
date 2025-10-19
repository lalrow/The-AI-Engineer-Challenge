from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_cohere import CohereRerank
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
import os
import time
from typing import List
from langchain_core.documents import Document

def search_top_k(query: str, k: int = 4, api_key: str = None) -> List[Document]:
    """Retrieve top-k documents using LangChain retriever (Session 9 compliant)."""
    
    # Environment (persistent Qdrant per MDC)
    qdrant_url = os.getenv("QDRANT_URL", "./qdrant_local")
    collection_name = os.getenv("COLLECTION_NAME", "science_curriculum_g3_g6")
    effective_api_key = api_key or os.getenv("OPENAI_API_KEY")
    cohere_api_key = os.getenv("COHERE_API_KEY")
    
    if not cohere_api_key:
        raise ValueError("❌ Missing COHERE_API_KEY in environment")
    
    # Qdrant client (persistent only, no :memory:)
    client = (
        QdrantClient(url=qdrant_url)
        if str(qdrant_url).startswith("http")
        else QdrantClient(path=qdrant_url)
    )
    
    # Embeddings and vectorstore
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=effective_api_key)
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
        content_payload_key="content",  # Map Qdrant payload "content" to Document page_content
        metadata_payload_key="metadata"
    )
    
    # Session 9 retriever chain
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    
    # Get base results first
    base_docs = base_retriever.invoke(query)
    
    # Filter out empty documents before reranking
    filtered_docs = [doc for doc in base_docs if doc.page_content and doc.page_content.strip()]
    
    if not filtered_docs:
        return []
    
    # Apply Cohere reranking
    compressor = CohereRerank(model="rerank-v3.5", cohere_api_key=cohere_api_key, top_n=k)
    time.sleep(20)  # Rate limit protection
    
    compressed_docs = compressor.compress_documents(filtered_docs, query)
    return compressed_docs
