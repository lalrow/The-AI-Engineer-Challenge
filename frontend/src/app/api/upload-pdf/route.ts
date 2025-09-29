/**
 * PDF Upload API Route
 * Handles PDF uploads, text extraction, metadata storage, and embedding generation
 */

import { NextRequest, NextResponse } from 'next/server';

// Forward PDF processing to FastAPI backend with PyMuPDFLoader
async function processPDFWithBackend(file: File, apiKey: string, userId: string): Promise<{text: string, chunks: number}> {
  try {
    console.log('Forwarding PDF to FastAPI backend for processing with PyMuPDFLoader');
    
    // Create form data to send to FastAPI
    const formData = new FormData();
    formData.append('file', file);
    formData.append('api_key', apiKey);
    formData.append('user_id', userId);
    
    // Send to FastAPI backend
    const response = await fetch('http://localhost:8000/api/upload-pdf', {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`FastAPI backend error: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('FastAPI processing result:', result);
    
    // Return the processed text and chunk count
    return {
      text: result.text || 'PDF processed successfully',
      chunks: result.chunks || 1
    };
    
  } catch (error) {
    console.error('FastAPI backend processing error:', error);
    throw error;
  }
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    const apiKey = formData.get('api_key') as string;
    const userType = formData.get('user_type') as string || 'parent'; // parent or system

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    if (!apiKey) {
      return NextResponse.json(
        { error: 'No API key provided' },
        { status: 400 }
      );
    }

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return NextResponse.json(
        { error: 'File must be a PDF' },
        { status: 400 }
      );
    }

    // Generate unique user ID
    const timestamp = Date.now();
    const userId = `user_${timestamp}_${Math.random().toString(36).substr(2, 9)}`;

    // Process PDF using FastAPI backend with PyMuPDFLoader
    console.log('Forwarding PDF to FastAPI backend for processing');
    const { text: content, chunks } = await processPDFWithBackend(file, apiKey, userId);
    
    if (!content || content.length < 50) {
      return NextResponse.json(
        { error: 'Could not extract readable text from PDF' },
        { status: 400 }
      );
    }

    return NextResponse.json({
      success: true,
      message: 'PDF uploaded and embedded successfully',
      filename: file.name,
      content_length: content.length,
      chunks_created: chunks,
      user_id: userId
    });

  } catch (error) {
    console.error('PDF upload error:', error);
    return NextResponse.json(
      { 
        error: 'Upload failed', 
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}