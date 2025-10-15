import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

export async function POST(req: NextRequest) {
  try {
    const { question, answer, apiKey: keyFromBody } = await req.json()
    const apiKey = keyFromBody || process.env.OPENAI_API_KEY
    if (!apiKey) return NextResponse.json({ error: 'Missing OPENAI_API_KEY' }, { status: 400 })

    // Call FastAPI search endpoint to get grounded context
    const searchResp = await fetch('http://localhost:8000/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: question, top_k: 4, api_key: apiKey })
    })

    if (!searchResp.ok) {
      const errTxt = await searchResp.text()
      return NextResponse.json({ error: 'Search failed', details: errTxt }, { status: 500 })
    }

    const sources = await searchResp.json()
    const context = sources.map((s: any) => s.text).join('\n\n')

    // Evaluate with grounded context
    const prompt = `Use the provided context to evaluate if the student's answer is correct.

Context:
${context}

Question: ${question}
Student Answer: ${answer}

Return JSON with this exact structure: {"score": 0.0-1.0, "feedback": "brief explanation"}`

    const resp = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: prompt }]
      })
    })

    if (!resp.ok) {
      const errTxt = await resp.text()
      return NextResponse.json({ error: 'OpenAI error', details: errTxt }, { status: 500 })
    }

    const data = await resp.json()
    const content = data.choices?.[0]?.message?.content ?? ''
    
    // Parse JSON evaluation
    try {
      const evaluation = JSON.parse(content)
      return NextResponse.json({ evaluation, sources })
    } catch {
      // Fallback if JSON parse fails
      return NextResponse.json({ evaluation: { score: 0, feedback: content }, sources })
    }
  } catch (e: any) {
    return NextResponse.json({ error: 'diagnostician failed', details: e?.message || String(e) }, { status: 500 })
  }
}


