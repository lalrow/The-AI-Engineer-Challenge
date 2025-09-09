'use client';

import { useState, useEffect } from 'react';

interface ChatRequest {
  developer_message: string;
  user_message: string;
  model: string;
  api_key: string;
}

interface HealthResponse {
  status: string;
}

export default function Home() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'healthy' | 'error'>('checking');
  const [healthResponse, setHealthResponse] = useState<string>('');
  const [userMessage, setUserMessage] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState('');

  const checkHealth = async () => {
    setApiStatus('checking');
    try {
      const response = await fetch('/api/health');
      const data: HealthResponse = await response.json();
      
      if (response.ok) {
        setApiStatus('healthy');
        setHealthResponse(JSON.stringify(data, null, 2));
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      setApiStatus('error');
      setHealthResponse(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const testChat = async () => {
    if (!userMessage.trim()) {
      alert('Please enter a message');
      return;
    }

    if (!apiKey.trim()) {
      alert('Please enter your OpenAI API key');
      return;
    }

    setIsLoading(true);
    setChatResponse('Sending request...');

    try {
      const requestBody: ChatRequest = {
        developer_message: "You are a helpful AI assistant.",
        user_message: userMessage,
        model: "gpt-4.1-mini",
        api_key: apiKey
      };

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000);

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const maybeText = await response.text().catch(() => '');
        if (response.status === 401) {
          setChatResponse('Error: 401 Unauthorized - Your OpenAI API key is invalid or missing.');
        } else {
          setChatResponse(`Error: HTTP ${response.status}${maybeText ? ` - ${maybeText}` : ''}`);
        }
        return;
      }

      // If there's no body (no stream), fall back to reading text
      if (!response.body) {
        const text = await response.text().catch(() => '');
        setChatResponse(text || 'No response body received from server.');
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let result = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        result += decoder.decode(value);
        setChatResponse(result);
      }

      if (!result) {
        setChatResponse('No content received from the stream.');
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        setChatResponse('Request timed out. Please try again or provide a valid API key.');
      } else {
        setChatResponse(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-800 text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-yellow-400 to-pink-400 bg-clip-text text-transparent">
              🤖 AI Engineer Challenge
            </h1>
            <p className="text-xl text-blue-100">
              Your First LLM-powered Application with Next.js & Vercel
            </p>
          </div>

          {/* API Status Section */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-8 shadow-xl">
            <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <span className="text-2xl">🔍</span>
              API Status
            </h2>
            
            <div className="flex items-center gap-4 mb-4">
              <div className={`px-4 py-2 rounded-full font-semibold ${
                apiStatus === 'checking' ? 'bg-yellow-500' :
                apiStatus === 'healthy' ? 'bg-green-500' : 'bg-red-500'
              }`}>
                {apiStatus === 'checking' && '🔄 Checking...'}
                {apiStatus === 'healthy' && '✅ API is healthy'}
                {apiStatus === 'error' && '❌ API is not responding'}
              </div>
              <button
                onClick={checkHealth}
                className="px-6 py-2 bg-blue-500 hover:bg-blue-600 rounded-full font-medium transition-colors"
              >
                Check API Health
              </button>
            </div>

            {healthResponse && (
              <div className="bg-black/20 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre>{healthResponse}</pre>
              </div>
            )}
          </div>

          {/* API Endpoints Section */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 mb-8 shadow-xl">
            <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <span className="text-2xl">📡</span>
              Available Endpoints
            </h2>
            
            <div className="space-y-4">
              <div className="bg-black/20 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-1 bg-green-500 text-white text-xs font-bold rounded">
                    GET
                  </span>
                  <code className="text-lg font-mono">/api/health</code>
                </div>
                <p className="text-blue-100">Health check endpoint to verify API status</p>
              </div>

              <div className="bg-black/20 p-4 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-1 bg-blue-500 text-white text-xs font-bold rounded">
                    POST
                  </span>
                  <code className="text-lg font-mono">/api/chat</code>
                </div>
                <p className="text-blue-100 mb-2">Chat endpoint for AI conversations</p>
                <p className="text-sm text-blue-200">
                  <strong>Body:</strong> JSON with developer_message, user_message, model, api_key
                </p>
              </div>
            </div>
          </div>

          {/* Chat Test Section */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-xl">
            <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <span className="text-2xl">💬</span>
              Test Chat API
            </h2>
            
            <div className="space-y-4">
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-blue-100 mb-2">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-..."
                    className="w-full px-4 py-3 rounded-full border-0 bg-white/20 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                  />
                  <p className="text-xs text-blue-200 mt-1">
                    Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-yellow-400 hover:text-yellow-300 underline">OpenAI Platform</a>
                  </p>
                </div>
                <div className="flex gap-4">
                  <input
                    type="text"
                    value={userMessage}
                    onChange={(e) => setUserMessage(e.target.value)}
                    placeholder="Enter your message..."
                    className="flex-1 px-4 py-3 rounded-full border-0 bg-white/20 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                    onKeyPress={(e) => e.key === 'Enter' && testChat()}
                  />
                  <button
                    onClick={testChat}
                    disabled={isLoading}
                    className="px-6 py-3 bg-green-500 hover:bg-green-600 disabled:bg-gray-500 rounded-full font-medium transition-colors"
                  >
                    {isLoading ? 'Sending...' : 'Send Message'}
                  </button>
                </div>
              </div>

              {chatResponse && (
                <div className="bg-black/20 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Response:</h3>
                  <pre className="whitespace-pre-wrap font-mono text-sm overflow-x-auto">
                    {chatResponse}
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-8 text-blue-200">
            <p>Built with Next.js, FastAPI, and deployed on Vercel</p>
            <p className="text-sm mt-2">
              🚀 Part of the AI Engineer Challenge by{' '}
              <a 
                href="https://github.com/AI-Maker-Space/The-AI-Engineer-Challenge" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-yellow-400 hover:text-yellow-300 underline"
              >
                AI Makerspace
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
