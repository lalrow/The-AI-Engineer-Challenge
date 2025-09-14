# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
import time
import json
from typing import Optional
from fastapi.responses import StreamingResponse

# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API")

# File-based storage for user conversations (persists across serverless function calls)
CONVERSATIONS_FILE = "/tmp/conversations.json"

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

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
