'use client'

import React from 'react'

export default function QuizPage() {
  const [apiKey, setApiKey] = React.useState<string>('')
  const [question, setQuestion] = React.useState('What is pollination?')
  const [answer, setAnswer] = React.useState('')
  const [context, setContext] = React.useState('Pollination transfers pollen enabling seed and fruit formation.')
  const [result, setResult] = React.useState<string>('')
  const [submitting, setSubmitting] = React.useState(false)

  React.useEffect(() => {
    try {
      const saved = localStorage.getItem('openai_api_key') || ''
      if (saved) setApiKey(saved)
    } catch {}
  }, [])

  const handleSaveKey = () => {
    try {
      localStorage.setItem('openai_api_key', apiKey)
      alert('API key saved locally for this browser.')
    } catch (e) {
      console.error(e)
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    setResult('')
    try {
      const res = await fetch('/api/diagnostician', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, answer, context, apiKey })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.error || 'Failed')
      setResult(data.evaluation || '')
    } catch (e: any) {
      setResult(`Error: ${e?.message || String(e)}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 720, margin: '2rem auto', padding: '1rem' }}>
      <h1>Foundational Skill Diagnostician</h1>
      <fieldset style={{ border: '1px solid #ddd', padding: '0.75rem', marginBottom: '1rem' }}>
        <legend>OpenAI API Key</legend>
        <input
          type="password"
          placeholder="sk-..."
          value={apiKey}
          onChange={e => setApiKey(e.target.value)}
          style={{ width: '100%' }}
        />
        <button onClick={handleSaveKey} style={{ marginTop: '0.5rem' }}>Save Key</button>
      </fieldset>
      <label>Question</label>
      <textarea value={question} onChange={e => setQuestion(e.target.value)} rows={3} style={{ width: '100%' }} />
      <label>Your Answer</label>
      <textarea value={answer} onChange={e => setAnswer(e.target.value)} rows={3} style={{ width: '100%' }} />
      <label>Context</label>
      <textarea value={context} onChange={e => setContext(e.target.value)} rows={3} style={{ width: '100%' }} />
      <button onClick={handleSubmit} disabled={submitting} style={{ marginTop: '1rem' }}>
        {submitting ? 'Evaluating…' : 'Evaluate'}
      </button>
      {result && (
        <pre style={{ background: '#f5f5f5', padding: '1rem', marginTop: '1rem', whiteSpace: 'pre-wrap' }}>
          {result}
        </pre>
      )}
    </div>
  )
}


