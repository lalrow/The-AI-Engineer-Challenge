'use client'

import React from 'react'

const QUESTIONS = [
  { id: 1, text: 'What is pollination?' },
  { id: 2, text: 'What do bees collect from flowers?' },
  { id: 3, text: 'Why are roots important to plants?' },
  { id: 4, text: 'What is photosynthesis?' },
  { id: 5, text: 'How do plants make their own food?' }
]

export default function QuizPage() {
  const [apiKey, setApiKey] = React.useState<string>('')
  const [selectedQuestion, setSelectedQuestion] = React.useState(QUESTIONS[0].text)
  const [answer, setAnswer] = React.useState('')
  const [feedback, setFeedback] = React.useState<string>('')
  const [submitting, setSubmitting] = React.useState(false)

  React.useEffect(() => {
    try {
      const saved = localStorage.getItem('openai_api_key') || ''
      if (saved) setApiKey(saved)
    } catch {}
  }, [])

  const handleSubmit = async () => {
    if (!apiKey || !answer.trim()) {
      setFeedback('Error: Please provide API key and answer')
      return
    }

    setSubmitting(true)
    setFeedback('')
    try {
      localStorage.setItem('openai_api_key', apiKey)
      
      const res = await fetch('/api/diagnostician', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: selectedQuestion, answer, apiKey })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data?.error || 'Failed')
      
      const score = data.evaluation?.score ?? 'N/A'
      const text = data.evaluation?.feedback ?? 'No feedback'
      setFeedback(`Score: ${score}\n\n${text}`)
    } catch (e: any) {
      setFeedback(`Error: ${e?.message || String(e)}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', padding: '1rem', fontFamily: 'sans-serif' }}>
      <h1 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Foundational Skill Diagnostician</h1>
      
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.25rem' }}>OpenAI API Key</label>
        <input
          type="password"
          placeholder="sk-..."
          value={apiKey}
          onChange={e => setApiKey(e.target.value)}
          style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc' }}
        />
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.25rem' }}>Select Question</label>
        <select 
          value={selectedQuestion}
          onChange={e => setSelectedQuestion(e.target.value)}
          style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc' }}
        >
          {QUESTIONS.map(q => (
            <option key={q.id} value={q.text}>{q.text}</option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ display: 'block', marginBottom: '0.25rem' }}>Your Answer</label>
        <textarea
          value={answer}
          onChange={e => setAnswer(e.target.value)}
          rows={4}
          style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc' }}
          placeholder="Type your answer here..."
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={submitting}
        style={{ 
          padding: '0.5rem 1.5rem', 
          border: '1px solid #333', 
          background: '#fff', 
          cursor: submitting ? 'not-allowed' : 'pointer' 
        }}
      >
        {submitting ? 'Evaluating...' : 'Submit'}
      </button>

      {feedback && (
        <div style={{ marginTop: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.25rem' }}>Feedback</label>
          <textarea
            readOnly
            value={feedback}
            rows={8}
            style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', background: '#f9f9f9' }}
          />
        </div>
      )}
    </div>
  )
}


