'use client'

import React from 'react'

export default function QuizPage() {
  const [apiKey, setApiKey] = React.useState<string>('')
  const [question, setQuestion] = React.useState('What is pollination?')
  const [answer, setAnswer] = React.useState('')
  const [result, setResult] = React.useState<any>(null)
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
    setResult(null)
    try {
      const res = await fetch('/api/diagnostician', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, answer, apiKey })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.error || 'Failed')
      setResult(data)
    } catch (e: any) {
      setResult({ error: e?.message || String(e) })
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
      <button onClick={handleSubmit} disabled={submitting} style={{ marginTop: '1rem' }}>
        {submitting ? 'Evaluating…' : 'Evaluate'}
      </button>
      {result && (
        <div style={{ marginTop: '1rem' }}>
          {result.error ? (
            <pre style={{ background: '#fee', padding: '1rem', whiteSpace: 'pre-wrap' }}>Error: {result.error}</pre>
          ) : (
            <>
              <div style={{ background: '#f5f5f5', padding: '1rem', marginBottom: '1rem' }}>
                <strong>Score:</strong> {result.evaluation?.score ?? 'N/A'}<br />
                <strong>Feedback:</strong> {result.evaluation?.feedback ?? 'N/A'}
              </div>
              {result.sources && result.sources.length > 0 && (
                <div>
                  <h3>Sources</h3>
                  {result.sources.map((s: any, i: number) => (
                    <div key={i} style={{ background: '#fafafa', padding: '0.5rem', marginBottom: '0.5rem', fontSize: '0.9em' }}>
                      <strong>Score: {s.score.toFixed(2)}</strong> - {s.text.substring(0, 100)}...
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}


