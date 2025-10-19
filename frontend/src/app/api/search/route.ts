import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

export async function POST(req: NextRequest) {
  try {
    const { query, top_k = 4, apiKey } = await req.json()
    
    if (!apiKey) {
      return NextResponse.json({ error: 'Missing API key' }, { status: 400 })
    }

    // Proxy to backend Session 9 retriever
    const response = await fetch('http://localhost:8000/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k, api_key: apiKey })
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(
        { error: error.detail || 'Search failed' }, 
        { status: response.status }
      )
    }

    const results = await response.json()
    return NextResponse.json(results)
    
  } catch (e: any) {
    return NextResponse.json(
      { error: 'Search request failed', details: e?.message || String(e) }, 
      { status: 500 }
    )
  }
}

