/*
  Simple eval harness: reads examples.json and calls the Next.js API route
  /api/diagnostician to get evaluations.

  Usage:
    cd frontend && npm run dev
    cd ..
    npx ts-node projects/diagnostician-agent/eval/run.ts
*/

import fs from 'node:fs'
import path from 'node:path'

const FRONTEND_BASE = process.env.FRONTEND_BASE_URL || 'http://localhost:3000'

type Example = { question: string; answer: string; context: string }

async function main() {
  const examplesPath = path.resolve('projects/diagnostician-agent/eval/examples.json')
  const raw = fs.readFileSync(examplesPath, 'utf-8')
  const examples: Example[] = JSON.parse(raw)

  for (const ex of examples) {
    const res = await fetch(`${FRONTEND_BASE}/api/diagnostician`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ex)
    })
    const data = await res.json()
    console.log('---')
    console.log('Q:', ex.question)
    console.log('A:', ex.answer)
    console.log('Eval:', data.evaluation)
  }
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})


