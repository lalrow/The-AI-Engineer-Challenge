import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

export async function POST(req: NextRequest) {
  try {
    const { question, answer, apiKey } = await req.json()
    
    if (!apiKey) {
      return NextResponse.json({ error: 'Missing API key' }, { status: 400 })
    }

    // Proxy request to backend /api/evaluate endpoint
    const response = await fetch('http://localhost:8000/api/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        question, 
        answer, 
        context: "", 
        api_key: apiKey 
      })
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(
        { error: error.detail || 'Evaluation failed' }, 
        { status: response.status }
      )
    }

    const result = await response.json()
    return NextResponse.json(result)
    
  } catch (e: any) {
    return NextResponse.json(
      { error: 'Request failed', details: e?.message || String(e) }, 
      { status: 500 }
    )
  }
}


