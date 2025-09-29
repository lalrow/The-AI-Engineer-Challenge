import { NextRequest, NextResponse } from 'next/server';
import { storeEmbedding, getEmbeddingsCount } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    console.log('[test-embedding] Starting test');
    
    // Test storeEmbedding
    const testEmbedding = Array(1536).fill(0).map(() => Math.random() - 0.5);
    storeEmbedding(999, 0, 'Test content', testEmbedding);
    
    // Check count
    const count = getEmbeddingsCount();
    
    return NextResponse.json({
      success: true,
      message: 'Test completed',
      embeddingsCount: count
    });
    
  } catch (error) {
    console.error('Test error:', error);
    return NextResponse.json(
      { error: 'Test failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

