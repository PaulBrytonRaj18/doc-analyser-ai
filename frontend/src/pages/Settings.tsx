import { useState } from 'react'

export default function Settings() {
  const [apiKey, setApiKey] = useState('')
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle')
  
  const [ocrEngine, setOcrEngine] = useState('tesseract')
  const [confidenceThreshold, setConfidenceThreshold] = useState(75)
  
  const [chunkSize, setChunkSize] = useState(512)
  const [topK, setTopK] = useState(5)
  const [relevanceThreshold, setRelevanceThreshold] = useState(0.7)
  
  const [webhooks, setWebhooks] = useState<string[]>([])
  const [newWebhook, setNewWebhook] = useState('')

  const testConnection = async () => {
    setConnectionStatus('testing')
    setTimeout(() => {
      setConnectionStatus(apiKey.length > 10 ? 'success' : 'error')
    }, 1500)
  }

  const addWebhook = () => {
    if (newWebhook && newWebhook.startsWith('http')) {
      setWebhooks([...webhooks, newWebhook])
      setNewWebhook('')
    }
  }

  const removeWebhook = (url: string) => {
    setWebhooks(webhooks.filter(w => w !== url))
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Configure your document analyzer preferences
        </p>
      </div>

      <div className="grid gap-6">
        {/* API Configuration */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">API Configuration</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your API key"
                className="input w-full px-4 py-2 rounded-lg"
              />
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={testConnection}
                disabled={!apiKey || connectionStatus === 'testing'}
                className="btn-primary px-4 py-2 rounded-lg font-medium disabled:opacity-50"
              >
                {connectionStatus === 'testing' ? 'Testing...' : 'Test Connection'}
              </button>
              {connectionStatus === 'success' && (
                <span className="text-[var(--success)]">Connected successfully</span>
              )}
              {connectionStatus === 'error' && (
                <span className="text-[var(--error)]">Connection failed</span>
              )}
            </div>
          </div>
        </div>

        {/* OCR Settings */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">OCR Settings</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-sm font-medium mb-2">OCR Engine</label>
              <select
                value={ocrEngine}
                onChange={(e) => setOcrEngine(e.target.value)}
                className="input w-full px-4 py-2 rounded-lg"
              >
                <option value="tesseract">Tesseract</option>
                <option value="cloud-vision">Cloud Vision API</option>
                <option value="aws-textract">AWS Textract</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Confidence Threshold: {confidenceThreshold}%</label>
              <input
                type="range"
                min="0"
                max="100"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                className="w-full accent-[var(--primary)]"
              />
            </div>
          </div>
        </div>

        {/* RAG Settings */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">RAG Settings</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <label className="block text-sm font-medium mb-2">Chunk Size</label>
              <input
                type="number"
                value={chunkSize}
                onChange={(e) => setChunkSize(Number(e.target.value))}
                className="input w-full px-4 py-2 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Top K</label>
              <input
                type="number"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="input w-full px-4 py-2 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Relevance Threshold</label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={relevanceThreshold}
                onChange={(e) => setRelevanceThreshold(Number(e.target.value))}
                className="input w-full px-4 py-2 rounded-lg"
              />
            </div>
          </div>
        </div>

        {/* Webhook Management */}
        <div className="card p-6">
          <h2 className="text-xl font-semibold mb-4">Webhook Management</h2>
          <div className="space-y-4">
            <div className="flex gap-4">
              <input
                type="url"
                value={newWebhook}
                onChange={(e) => setNewWebhook(e.target.value)}
                placeholder="https://your-webhook-url.com/hook"
                className="input flex-1 px-4 py-2 rounded-lg"
              />
              <button
                onClick={addWebhook}
                disabled={!newWebhook}
                className="btn-primary px-4 py-2 rounded-lg font-medium disabled:opacity-50"
              >
                Add Webhook
              </button>
            </div>
            {webhooks.length > 0 ? (
              <ul className="space-y-2">
                {webhooks.map((url) => (
                  <li key={url} className="flex items-center justify-between bg-[var(--bg-input)] px-4 py-2 rounded-lg">
                    <span className="text-sm truncate">{url}</span>
                    <button
                      onClick={() => removeWebhook(url)}
                      className="text-[var(--error)] text-sm hover:underline"
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-muted-foreground text-sm">No webhooks configured</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}