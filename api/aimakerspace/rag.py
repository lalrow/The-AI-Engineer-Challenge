import numpy as np
from typing import List, Dict, Any
from openai import OpenAI


class RAG:
    """Simple RAG implementation using OpenAI embeddings and chat completions"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.documents = []
        self.embeddings = []
    
    def add_document(self, text: str):
        """Add a document to the RAG system"""
        # Split text into chunks
        chunks = self._split_text(text)
        self.documents.extend(chunks)
        
        # Generate embeddings for chunks
        for chunk in chunks:
            embedding = self._get_embedding(chunk)
            self.embeddings.append(embedding)
    
    def _split_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return [0.0] * 1536  # Default embedding size
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def query(self, question: str) -> str:
        """Query the RAG system"""
        if not self.documents:
            return "No documents have been added to the RAG system yet."
        
        # Get embedding for the question
        question_embedding = self._get_embedding(question)
        
        # Find most similar documents
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(question_embedding, doc_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity and get top 3
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_docs = [self.documents[i] for i, _ in similarities[:3]]
        
        # Create context from top documents
        context = "\n\n".join(top_docs)
        
        # Generate response using OpenAI
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a helpful assistant. Answer the user's question based ONLY on the provided context. If the answer cannot be found in the context, say 'I cannot find the answer in the provided documents.'\n\nContext:\n{context}"
                    },
                    {"role": "user", "content": question}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

