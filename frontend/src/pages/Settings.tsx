import { useState } from 'react'
import { Key, Globe, Database, Cpu, Check, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Settings() {
  const [apiKey, setApiKey] = useState(localStorage.getItem('api_key') || '')
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_API_URL || '/api')
  const [saved, setSaved] = useState(false)

  const handleSaveApiKey = () => {
    localStorage.setItem('api_key', apiKey)
    toast.success('API key saved')
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleSaveApiUrl = () => {
    localStorage.setItem('api_url', apiUrl)
    toast.success('API URL saved')
    window.location.reload()
  }

  return (
    <div className="max-w-2xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Configure your DocuLens AI experience
        </p>
      </div>

      <div className="space-y-6">
        <section className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Key className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">API Configuration</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your API key"
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <button
              onClick={handleSaveApiKey}
              className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              {saved ? <Check className="h-4 w-4" /> : null}
              Save API Key
            </button>
          </div>
        </section>

        <section className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Globe className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Server Configuration</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">API URL</label>
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://localhost:8000/api"
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <button
              onClick={handleSaveApiUrl}
              className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Save API URL
            </button>
          </div>
        </section>

        <section className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Database className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Vector Store</h2>
          </div>
          <p className="text-sm text-muted-foreground">
            Vector storage is powered by Pinecone. Configure your Pinecone
            credentials in the backend .env file.
          </p>
        </section>

        <section className="rounded-lg border bg-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <Cpu className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">AI Models</h2>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Embeddings</span>
              <span className="font-medium">Gemini Embeddings</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">LLM</span>
              <span className="font-medium">Gemini 2.0 Flash</span>
            </div>
          </div>
        </section>

        <section className="rounded-lg border border-yellow-500/20 bg-yellow-500/5 p-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-yellow-500 mt-0.5" />
            <div>
              <h3 className="font-medium text-yellow-500">Environment Variables</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                For production, set these environment variables in your backend:
              </p>
              <ul className="mt-2 space-y-1 text-sm text-muted-foreground font-mono">
                <li>GEMINI_API_KEY</li>
                <li>PINECONE_API_KEY</li>
                <li>REDIS_URL (optional)</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
