from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
import os
from typing import List
from langchain_core.documents import Document

def search_top_k(query: str, k: int = 4, api_key: str = None) -> List[Document]:
    """Search top-k chunks from Qdrant collection."""
    qdrant_url = os.getenv("QDRANT_URL", ":memory:")
    collection_name = os.getenv("COLLECTION_NAME", "science_curriculum_g3_g6")
    effective_api_key = api_key or os.getenv("OPENAI_API_KEY", "")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=effective_api_key)
    vector = embeddings.embed_query(query)

    if str(qdrant_url).startswith("http"):
        client = QdrantClient(url=qdrant_url)
    elif qdrant_url == ":memory:":
        client = QdrantClient(location=":memory:")
    else:
        client = QdrantClient(path=qdrant_url)

    results = client.search(collection_name=collection_name, query_vector=vector, limit=k)
    
    # Convert search results to LangChain-compatible Document objects
    documents = []
    for hit in results:
        content = hit.payload.get("content", "")
        metadata = hit.payload.get("metadata", {})
        documents.append(Document(page_content=content, metadata=metadata))
    
    return documents
