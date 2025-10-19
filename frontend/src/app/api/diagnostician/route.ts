import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

export async function POST(req: NextRequest) {
  try {
    const { question, answer, apiKey } = await req.json()
    
    if (!apiKey) {
      return NextResponse.json({ error: 'Missing API key' }, { status: 400 })
    }

    // Step 1: Retrieve context using Session 9 retriever
    const searchResponse = await fetch('http://localhost:8000/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: question, top_k: 3, api_key: apiKey })
    })

    if (!searchResponse.ok) {
      return NextResponse.json(
        { error: 'Failed to retrieve context' }, 
        { status: 500 }
      )
    }

    const searchResults = await searchResponse.json()
    const context = searchResults.map((r: any) => r.text).join('\n\n')

    // Step 2: Evaluate answer with retrieved context
    const evalResponse = await fetch('http://localhost:8000/api/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, answer, context, api_key: apiKey })
    })

    if (!evalResponse.ok) {
      const error = await evalResponse.json()
      return NextResponse.json(
        { error: error.detail || 'Evaluation failed' }, 
        { status: evalResponse.status }
      )
    }

    const result = await evalResponse.json()
    return NextResponse.json(result)
    
  } catch (e: any) {
    return NextResponse.json(
      { error: 'Request failed', details: e?.message || String(e) }, 
      { status: 500 }
    )
  }
}


