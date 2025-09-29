import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log('[RAG Chat] Received request body:', body);
    const { message, apiKey, userId } = body;

    if (!message) {
      console.log('[RAG Chat] Missing message in request');
      return NextResponse.json(
        { error: "Message is required" },
        { status: 400 }
      );
    }

    // Forward RAG request to FastAPI backend
    console.log('[RAG Chat] Forwarding to FastAPI backend');
    
    const fastapiResponse = await fetch('http://localhost:8000/api/rag-chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_message: message,
        api_key: apiKey || 'test-key',
        user_id: userId || 'test-user'
      }),
    });

    if (!fastapiResponse.ok) {
      throw new Error(`FastAPI error: ${fastapiResponse.status}`);
    }

    const fastapiResult = await fastapiResponse.json();
    console.log('[RAG Chat] FastAPI response:', fastapiResult);

    return NextResponse.json({
      status: "ok",
      message: fastapiResult.message || fastapiResult.response || "No response from FastAPI",
      documentsCount: fastapiResult.documentsCount || 0
    });

  } catch (error) {
    console.error('RAG chat error:', error);
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
