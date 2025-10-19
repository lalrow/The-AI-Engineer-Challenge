# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
import sys
import time
import json
import uuid # Added for generating thread_id
import subprocess # Added for subprocess.run
from typing import Optional
from fastapi.responses import StreamingResponse
import io
import numpy as np
from typing import List, Dict, Any
from langchain_text_splitters import CharacterTextSplitter
# No need for dotenv - just use os.getenv directly

# Add project root to Python path for backend imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.agent.diagnostician_agent import build_graph_with_api_key

# Get OpenAI API key from environment variable
DEFAULT_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "test-key")

# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API")

# Import the PDF auto-loader
# from startup_pdf_loader import initialize_pdf_rag_system  # Commented out - file doesn't exist

# File-based storage for user conversations (persists across serverless function calls)
CONVERSATIONS_FILE = "/tmp/conversations.json"
RAG_INDEX_FILE = "/tmp/rag_index.json"

# RAG Class Definition (inlined to avoid import issues in serverless)
class RAG:
    """Simple RAG implementation using OpenAI embeddings and chat completions"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.documents = []
        self.embeddings = []
        self.rag_index_file = RAG_INDEX_FILE # Default to global file

    def add_document(self, text: str, metadata: Dict = None):
        """Add a document to the RAG system with optional metadata"""
        # Use LangChain's text splitter for better chunking
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separator="\n"
        )
        chunks = text_splitter.split_text(text)
        
        # Add chunks with metadata
        for chunk in chunks:
            doc_entry = {
                "text": chunk,
                "metadata": metadata or {}
            }
            self.documents.append(doc_entry)
            
            # Generate embeddings for chunks
            embedding = self._get_embedding(chunk)
            self.embeddings.append(embedding)
    
    def save_state(self):
        """Save the current state of RAG documents and embeddings to a file."""
        try:
            state = {
                "documents": self.documents,
                "embeddings": self.embeddings,
            }
            with open(self.rag_index_file, 'w') as f:
                json.dump(state, f)
            print(f"📚 RAG state saved to {self.rag_index_file}")
        except Exception as e:
            print(f"Error saving RAG state: {e}")

    def load_state(self):
        """Load RAG documents and embeddings from a file."""
        try:
            if os.path.exists(self.rag_index_file):
                with open(self.rag_index_file, 'r') as f:
                    state = json.load(f)
                    self.documents = state.get("documents", [])
                    self.embeddings = state.get("embeddings", [])
                print(f"📚 RAG state loaded from {self.rag_index_file}. Documents: {len(self.documents)}, Embeddings: {len(self.embeddings)}")
                return True
            else:
                print(f"📚 No RAG state file found at {self.rag_index_file}.")
                return False
        except Exception as e:
            print(f"Error loading RAG state: {e}")
            return False
    
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
        
        # Create context from top documents (extract text from document entries)
        context_texts = []
        for doc in top_docs:
            if isinstance(doc, dict):
                context_texts.append(doc["text"])
            else:
                context_texts.append(str(doc))
        context = "\n\n".join(context_texts)
        
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

# Global RAG instance
rag_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize persistent Qdrant and auto-ingest bees PDF if empty"""
    global rag_system

    print("🚀 FastAPI server starting...")

    qdrant_url = os.getenv("QDRANT_URL", "./qdrant_local")
    collection_name = os.getenv("COLLECTION_NAME", "science_curriculum_g3_g6")

    try:
        from qdrant_client import QdrantClient
        # Always use path-based client for local persistence
        if str(qdrant_url).startswith("http"):
            client = QdrantClient(url=qdrant_url)
        else:
            client = QdrantClient(path=qdrant_url)

        try:
            info = client.get_collection(collection_name=collection_name)
            vectors_count = getattr(info, 'vectors_count', 0) or 0
            has_vectors = vectors_count > 0
        except Exception:
            has_vectors = False

        if not has_vectors:
            print("📚 Initializing with Bees PDF ...")
            # Resolve absolute repo root and script/data paths
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            retriever_script = os.path.join(repo_root, "projects", "diagnostician-agent", "retriever", "load_pdf_to_qdrant.py")
            bees_pdf_path = os.path.join(repo_root, "frontend", "public", "pdfs", "grade3", "bees.pdf")
            # If canonical bees.pdf not present, fall back to any uploaded Bees file
            if not os.path.exists(bees_pdf_path):
                uploaded_dir = os.path.join(repo_root, "frontend", "public", "pdfs", "uploaded")
                if os.path.isdir(uploaded_dir):
                    candidates = [f for f in os.listdir(uploaded_dir) if f.lower().endswith('.pdf') and 'bees' in f.lower()]
                    if candidates:
                        bees_pdf_path = os.path.join(uploaded_dir, sorted(candidates)[-1])

            # Pass env explicitly to avoid missing key in subshell
            openai_key = os.getenv("OPENAI_API_KEY", "")
            cmd_list = [
                "uv", "run", "python", f"{retriever_script}", "--pdf", f"{bees_pdf_path}"
            ]
            env = os.environ.copy()
            env["QDRANT_URL"] = qdrant_url
            env["OPENAI_API_KEY"] = openai_key

            print(f"Executing command: {' '.join(cmd_list)}")
            process = subprocess.run(cmd_list, env=env, capture_output=True, text=True)
            if process.returncode != 0:
                print(f"❌ Error populating Qdrant: {process.stderr}", file=sys.stderr)
                raise Exception(f"Qdrant population failed: {process.stderr}")
            else:
                print(f"✅ Qdrant population script output: {process.stdout}")
        else:
            print("✅ Qdrant already populated.")
    except Exception as e:
        print(f"⚠️  Qdrant startup check failed: {e}")

def load_conversations():
    """Load conversations from file"""
    try:
        if os.path.exists(CONVERSATIONS_FILE):
            with open(CONVERSATIONS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_conversations(conversations):
    """Save conversations to file"""
    try:
        with open(CONVERSATIONS_FILE, 'w') as f:
            json.dump(conversations, f)
    except Exception:
        pass

async def initialize_rag_system(api_key: str = None):
    """Initialize the RAG system with OpenAI API key and auto-load PDFs"""
    global rag_system
    try:
        if rag_system is None:
            print("🔄 Initializing RAG system...")
            
            # Use provided API key or fall back to environment variable
            effective_api_key = api_key or DEFAULT_OPENAI_API_KEY
            
            # Check if we have a valid API key
            if effective_api_key == "test-key" or not effective_api_key:
                print("⚠️  Using test API key - RAG will work but with limited functionality")
                print("💡 Set OPENAI_API_KEY in .env file for full functionality")
            
            rag_system = RAG(api_key=effective_api_key)
            
            # Load existing RAG state if available
            rag_system.load_state()
            
            # Simplify initialization messages - RAG class now handles its own state
            if len(rag_system.documents) == 0:
                print("📚 RAG system started empty - upload PDFs to get started.")
            else:
                print(f"📚 RAG system initialized with {len(rag_system.documents)} document chunks.")
                
        return rag_system
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing RAG system: {str(e)}")

def load_rag_index():
    """Load RAG index from file"""
    try:
        if os.path.exists(RAG_INDEX_FILE):
            with open(RAG_INDEX_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_rag_index(index_data):
    """Save RAG index to file"""
    try:
        with open(RAG_INDEX_FILE, 'w') as f:
            json.dump(index_data, f)
    except Exception:
        pass

# Load existing conversations
user_conversations = load_conversations()

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    developer_message: str  # Message from the developer/system
    user_message: str      # Message from the user
    model: Optional[str] = "gpt-4.1-mini"  # Optional model selection with default
    api_key: str          # OpenAI API key for authentication
    user_id: str          # User identifier for tracking

class RAGChatRequest(BaseModel):
    user_message: str      # Message from the user
    model: Optional[str] = "gpt-4.1-mini"  # Optional model selection with default
    api_key: str          # OpenAI API key for authentication
    user_id: str          # User identifier for tracking

class SearchRequest(BaseModel):
    query: str
    top_k: int = 4
    api_key: str

class EvaluateRequest(BaseModel):
    question: str
    answer: str
    context: Optional[str] = ""
    api_key: str

# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Initialize OpenAI client with the provided API key
        client = OpenAI(api_key=request.api_key)
        
        # Load fresh conversations (in case another function instance updated them)
        user_conversations = load_conversations()
        
        # Get or create conversation history for this user
        if request.user_id not in user_conversations:
            user_conversations[request.user_id] = []
        
        # Add the new user message to conversation history
        user_conversations[request.user_id].append({
            "role": "user", 
            "content": request.user_message,
            "timestamp": str(time.time())
        })
        
        # Save conversations immediately
        save_conversations(user_conversations)
        
        # Prepare messages for OpenAI (system + conversation history)
        messages = [{"role": "system", "content": "You are a helpful AI assistant. Always provide clear, accurate, and well-structured responses. When explaining concepts, use simple language and relatable examples. When summarizing, capture all key points concisely. When writing creatively, be imaginative and engaging. When solving problems, show your reasoning step-by-step. When rewriting text, maintain professional tone and correct all errors."}]
        messages.extend(user_conversations[request.user_id][-10:])  # Keep last 10 messages
        
        # Create an async generator function for streaming responses
        async def generate():
            # Create a streaming chat completion request
            stream = client.chat.completions.create(
                model=request.model,
                messages=messages,
                stream=True  # Enable streaming response
            )
            
            # Collect the full response for storage
            full_response = ""
            
            # Yield each chunk of the response as it becomes available
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # Store the AI response in conversation history
            user_conversations[request.user_id].append({
                "role": "assistant", 
                "content": full_response,
                "timestamp": str(time.time())
            })
            
            # Save conversations after AI response
            save_conversations(user_conversations)

        # Return a streaming response to the client
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Get user conversation history
@app.get("/api/conversations/{user_id}")
async def get_conversations(user_id: str):
    # Load fresh conversations
    conversations = load_conversations()
    
    if user_id not in conversations:
        return {"conversations": [], "message": "No conversations found for this user"}
    
    return {
        "user_id": user_id,
        "conversations": conversations[user_id],
        "total_messages": len(conversations[user_id])
    }

# Search endpoint for diagnostician (AIE8 Sessions 6-10 compliant)
@app.post("/api/search")
async def search_query(request: SearchRequest):
    """Query Qdrant vector database with Session 9 retriever pattern"""
    try:
        if not request.api_key:
            raise HTTPException(status_code=400, detail="Missing api_key")
        
        # Import and use Session 9 retriever
        from backend.search_client import search_top_k
        
        # Call Session 9 retriever (uses Cohere reranking)
        results = search_top_k(query=request.query, k=request.top_k, api_key=request.api_key)
        
        # Convert List[Document] to response format
        return [{
            "text": doc.page_content,
            "score": getattr(doc, "metadata", {}).get("score", 1.0),
            "metadata": getattr(doc, "metadata", {})
        } for doc in results]
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/evaluate")
async def evaluate_answer(request: EvaluateRequest):
    """Evaluate student answer using always-on Agentic Diagnostician Agent"""
    try:
        if not request.api_key:
            raise HTTPException(status_code=400, detail="Missing api_key")

        agent_graph = build_graph_with_api_key(request.api_key)

        state = {
            "question": request.question,
            "answer": request.answer,
            "context": request.context or "",
            "api_key": request.api_key,
        }

        result = agent_graph.invoke(state, config={"configurable": {"thread_id": str(uuid.uuid4())}})
        agent_output = result.get("agent_response", {})

        if not isinstance(agent_output, dict):
            try:
                agent_output = json.loads(agent_output)
            except Exception:
                agent_output = {
                    "score": 0.0,
                    "evaluation": "Malformed output from LLM.",
                    "next_step": "Retry with more context.",
                    "feedback": "Output could not be parsed to JSON."
                }

        return {
            "success": True,
            "data": agent_output,
            "meta": {
                "model": "gpt-4o-mini",
                "agent": "diagnostician",
                "version": "v2"
            }
        }

    except Exception as e:
        print(f"Evaluation error: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

# RAG Chat endpoint
@app.post("/api/rag-chat")
async def rag_chat(request: RAGChatRequest):
    """Chat with the uploaded PDF using RAG"""
    try:
        # Initialize RAG system
        rag = await initialize_rag_system(request.api_key)
        
        # Load fresh conversations
        user_conversations = load_conversations()
        
        # Get or create conversation history for this user
        if request.user_id not in user_conversations:
            user_conversations[request.user_id] = []
        
        # Add the new user message to conversation history
        user_conversations[request.user_id].append({
            "role": "user", 
            "content": request.user_message,
            "timestamp": str(time.time())
        })
        
        # Save conversations immediately
        save_conversations(user_conversations)
        
        # Use RAG to get context-aware response
        response = rag.query(request.user_message)
        
        # Store the AI response in conversation history
        user_conversations[request.user_id].append({
            "role": "assistant", 
            "content": response,
            "timestamp": str(time.time())
        })
        
        # Save conversations after AI response
        save_conversations(user_conversations)
        
        # Return JSON response
        return {
            "message": response,
            "documentsCount": len(rag.documents) if rag else 0,
            "status": "ok"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get RAG index status
@app.get("/api/rag-status")
async def get_rag_status():
    """Get the general status of RAG system"""
    try:
        # Get the global RAG system using environment variable
        rag = await initialize_rag_system()
        
        # Check if rag is a RAG object or a dictionary
        if hasattr(rag, 'documents'):
            documents_count = len(rag.documents)
        elif isinstance(rag, dict) and 'documents' in rag:
            documents_count = len(rag['documents'])
        else:
            documents_count = 0
        
        return {
            "has_index": documents_count > 0,
            "documentsCount": documents_count,
            "status": "ready" if documents_count > 0 else "empty",
            "message": f"RAG system ready with {documents_count} document chunks" if documents_count > 0 else "No documents indexed yet. Upload PDFs to get started."
        }
    except Exception as e:
        return {
            "has_index": False,
            "documentsCount": 0,
            "status": "error",
            "message": f"Error checking RAG status: {str(e)}"
        }

@app.get("/api/rag-status/{user_id}")
async def get_rag_status_by_user(user_id: str):
    """Get the status of RAG index for a specific user"""
    index_data = load_rag_index()
    
    if user_id not in index_data:
        return {
            "user_id": user_id,
            "has_index": False,
            "message": "No PDF uploaded for this user"
        }
    
    return {
        "user_id": user_id,
        "has_index": True,
        "index_info": index_data[user_id]
    }

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
