import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ userId: string }> }
) {
  try {
    const { userId } = await context.params;
    
    // Forward RAG status request to FastAPI backend
    console.log('[RAG Status] Forwarding to FastAPI backend for userId:', userId);
    
    const fastapiResponse = await fetch('http://localhost:8000/api/rag-status', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!fastapiResponse.ok) {
      throw new Error(`FastAPI error: ${fastapiResponse.status}`);
    }

    const fastapiResult = await fastapiResponse.json();
    console.log('[RAG Status] FastAPI response:', fastapiResult);
    
    return NextResponse.json({
      has_index: fastapiResult.has_index || false,
      documentsCount: fastapiResult.documentsCount || 0,
      status: fastapiResult.status || "empty",
      message: fastapiResult.message || "No documents indexed yet. Upload PDFs to get started."
    });
    
  } catch (error) {
    console.error('RAG Status API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
