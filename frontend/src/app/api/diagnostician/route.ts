import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

export async function POST(req: NextRequest) {
  try {
    const { question, answer, context, apiKey: keyFromBody } = await req.json()
    const apiKey = keyFromBody || process.env.OPENAI_API_KEY
    if (!apiKey) return NextResponse.json({ error: 'Missing OPENAI_API_KEY' }, { status: 400 })

    const prompt = `
Question: ${question}
Answer: ${answer}
Context: ${context}
Rate 0–1 correctness and give short feedback:
`

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
    return NextResponse.json({ evaluation: content })
  } catch (e: any) {
    return NextResponse.json({ error: 'diagnostician failed', details: e?.message || String(e) }, { status: 500 })
  }
}


