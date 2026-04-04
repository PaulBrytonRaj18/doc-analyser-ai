import { useState, useRef } from 'react'
import { Upload, FileText, Image, FileType, Loader2, Sparkles, X, Send } from 'lucide-react'
import { analyzeApi } from '@/services/api'

interface AnalysisResult {
  summary: string
  entities: {
    persons: string[]
    organizations: string[]
    dates: string[]
    locations: string[]
    monetary_values: string[]
  }
  sentiment: string
  metadata: {
    file_type: string
    processing_time: string
    num_pages: string
  }
}

export default function Analyze() {
  const [file, setFile] = useState<File | null>(null)
  const [text, setText] = useState('')
  const [mode, setMode] = useState<'file' | 'text'>('file')
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0]
    if (selected) {
      setFile(selected)
      setError('')
    }
  }

  const handleAnalyze = async () => {
    if (mode === 'file' && !file) {
      setError('Please select a file')
      return
    }
    if (mode === 'text' && !text.trim()) {
      setError('Please enter some text')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      let response: AnalysisResult
      if (mode === 'file') {
        response = await analyzeApi.analyzeFile(file!)
      } else {
        response = await analyzeApi.analyzeText(text)
      }
      setResult(response)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-500 bg-green-500/10'
      case 'negative': return 'text-red-500 bg-red-500/10'
      default: return 'text-yellow-500 bg-yellow-500/10'
    }
  }

  const getFileIcon = (fileType: string) => {
    if (fileType === 'pdf') return <FileText className="h-5 w-5 text-red-500" />
    if (fileType === 'docx') return <FileType className="h-5 w-5 text-blue-500" />
    if (fileType === 'image') return <Image className="h-5 w-5 text-purple-500" />
    return <FileText className="h-5 w-5 text-muted-foreground" />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-primary/20 p-2">
          <Sparkles className="h-6 w-6 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Document Analyzer</h1>
          <p className="text-sm text-muted-foreground">AI-powered analysis for PDF, DOCX, and images</p>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setMode('file')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            mode === 'file' ? 'bg-primary text-white' : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
          }`}
        >
          <Upload className="mr-2 inline h-4 w-4" />
          Upload File
        </button>
        <button
          onClick={() => setMode('text')}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
            mode === 'text' ? 'bg-primary text-white' : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
          }`}
        >
          <FileText className="mr-2 inline h-4 w-4" />
          Paste Text
        </button>
      </div>

      <div className="rounded-xl border border-border/50 bg-card p-6">
        {mode === 'file' ? (
          <div
            onClick={() => fileInputRef.current?.click()}
            className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-border/50 p-12 transition-colors hover:border-primary/50 hover:bg-primary/5"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.png,.jpg,.jpeg,.tiff,.bmp"
              onChange={handleFileSelect}
              className="hidden"
            />
            {file ? (
              <div className="flex items-center gap-4">
                {getFileIcon(file.name.split('.').pop() || '')}
                <div>
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  className="rounded-full p-1 hover:bg-destructive/20"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <>
                <Upload className="h-12 w-12 text-muted-foreground" />
                <p className="mt-4 font-medium">Drop your document here</p>
                <p className="text-sm text-muted-foreground">PDF, DOCX, PNG, JPG, TIFF, BMP</p>
              </>
            )}
          </div>
        ) : (
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your document text here..."
            className="min-h-[200px] w-full resize-none rounded-lg border border-border bg-background p-4 text-sm placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
        )}

        {error && (
          <p className="mt-4 text-sm text-destructive">{error}</p>
        )}

        <button
          onClick={handleAnalyze}
          disabled={loading || (mode === 'file' ? !file : !text.trim())}
          className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-3 font-medium text-white transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
          {loading ? 'Analyzing...' : 'Analyze Document'}
        </button>
      </div>

      {result && (
        <div className="space-y-6">
          <div className="rounded-xl border border-primary/20 bg-card p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Summary</h2>
              <span className={`rounded-full px-3 py-1 text-xs font-medium ${getSentimentColor(result.sentiment)}`}>
                {result.sentiment}
              </span>
            </div>
            <p className="mt-4 text-muted-foreground">{result.summary}</p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-xl border border-border/50 bg-card p-6">
              <h3 className="mb-4 font-semibold">Entities</h3>
              <div className="space-y-4">
                {result.entities.persons.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground">Persons</p>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {result.entities.persons.map((person, i) => (
                        <span key={i} className="rounded-full bg-primary/10 px-3 py-1 text-xs text-primary">
                          {person}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {result.entities.organizations.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground">Organizations</p>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {result.entities.organizations.map((org, i) => (
                        <span key={i} className="rounded-full bg-blue-500/10 px-3 py-1 text-xs text-blue-500">
                          {org}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {result.entities.dates.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground">Dates</p>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {result.entities.dates.map((date, i) => (
                        <span key={i} className="rounded-full bg-purple-500/10 px-3 py-1 text-xs text-purple-500">
                          {date}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {result.entities.locations.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground">Locations</p>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {result.entities.locations.map((loc, i) => (
                        <span key={i} className="rounded-full bg-green-500/10 px-3 py-1 text-xs text-green-500">
                          {loc}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {result.entities.monetary_values.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground">Monetary Values</p>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {result.entities.monetary_values.map((money, i) => (
                        <span key={i} className="rounded-full bg-yellow-500/10 px-3 py-1 text-xs text-yellow-500">
                          {money}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {Object.values(result.entities).every(arr => arr.length === 0) && (
                  <p className="text-sm text-muted-foreground">No entities found</p>
                )}
              </div>
            </div>

            <div className="rounded-xl border border-border/50 bg-card p-6">
              <h3 className="mb-4 font-semibold">Metadata</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">File Type</span>
                  <span className="text-sm font-medium">{result.metadata.file_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Processing Time</span>
                  <span className="text-sm font-medium">{result.metadata.processing_time}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Pages</span>
                  <span className="text-sm font-medium">{result.metadata.num_pages}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}