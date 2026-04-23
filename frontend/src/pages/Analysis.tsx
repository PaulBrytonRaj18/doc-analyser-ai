import { useState } from 'react'
import { Beaker, GitCompare, Lightbulb, Loader2 } from 'lucide-react'
import { analyzeApi, compareApi } from '@/services/api'
import { useAppStore } from '@/store'
import { cn } from '@/lib/utils'
import ReactMarkdown from 'react-markdown'
import toast from 'react-hot-toast'

type TabType = 'synthesis' | 'compare' | 'insights'

export default function Analysis() {
  const [activeTab, setActiveTab] = useState<TabType>('synthesis')
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<Record<string, unknown> | null>(null)
  const { selectedDocumentIds, documents } = useAppStore()

  const tabs = [
    { id: 'synthesis' as const, label: 'Synthesis', icon: Beaker },
    { id: 'compare' as const, label: 'Compare', icon: GitCompare },
    { id: 'insights' as const, label: 'Insights', icon: Lightbulb },
  ]

  const handleSynthesize = async () => {
    if (!query.trim()) return
    setIsLoading(true)
    try {
      const response = await analyzeApi.text(query)
      setResults(response)
      toast.success('Analysis complete')
    } catch (error) {
      toast.error('Analysis failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCompare = async () => {
    if (selectedDocumentIds.length !== 2) {
      toast.error('Select exactly 2 documents to compare')
      return
    }
    setIsLoading(true)
    try {
      const response = await compareApi.compare(
        selectedDocumentIds[0],
        selectedDocumentIds[1]
      )
      setResults(response as unknown as Record<string, unknown>)
      toast.success('Comparison complete')
    } catch (error) {
      toast.error('Comparison failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExtractInsights = async () => {
    if (selectedDocumentIds.length === 0) {
      toast.error('Select at least 1 document')
      return
    }
    setIsLoading(true)
    try {
      const response = await analyzeApi.get(selectedDocumentIds[0])
      setResults(response)
      toast.success('Insights extracted')
    } catch (error) {
      toast.error('Extraction failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = () => {
    if (activeTab === 'synthesis') handleSynthesize()
    else if (activeTab === 'compare') handleCompare()
    else handleExtractInsights()
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analysis</h1>
        <p className="mt-2 text-muted-foreground">
          Advanced document analysis with AI
        </p>
      </div>

      <div className="flex gap-2 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveTab(tab.id)
              setResults(null)
              setQuery('')
            }}
            className={cn(
              'flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            )}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          {activeTab === 'synthesis' && (
            <div className="space-y-4">
              <label className="text-sm font-medium">Synthesis Topic</label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="What would you like to synthesize across your documents?"
                className="w-full rounded-lg border bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary min-h-[100px]"
              />
            </div>
          )}

          {activeTab === 'compare' && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Select exactly 2 documents to compare
              </p>
              <div className="space-y-2">
                {documents.map((doc) => (
                  <label
                    key={doc.document_id}
                    className={cn(
                      'flex items-center gap-3 rounded-lg border p-3 cursor-pointer',
                      selectedDocumentIds.includes(doc.document_id)
                        ? 'border-primary bg-primary/5'
                        : 'hover:bg-accent'
                    )}
                  >
                    <input
                      type="checkbox"
                      checked={selectedDocumentIds.includes(doc.document_id)}
                      onChange={() => useAppStore.getState().toggleDocumentSelection(doc.document_id)}
                      className="h-4 w-4"
                    />
                    <span className="text-sm">{doc.filename}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'insights' && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Extract action items, decisions, deadlines, and risks
              </p>
              <div className="space-y-2">
                {documents.map((doc) => (
                  <label
                    key={doc.document_id}
                    className={cn(
                      'flex items-center gap-3 rounded-lg border p-3 cursor-pointer',
                      selectedDocumentIds.includes(doc.document_id)
                        ? 'border-primary bg-primary/5'
                        : 'hover:bg-accent'
                    )}
                  >
                    <input
                      type="checkbox"
                      checked={selectedDocumentIds.includes(doc.document_id)}
                      onChange={() => useAppStore.getState().toggleDocumentSelection(doc.document_id)}
                      className="h-4 w-4"
                    />
                    <span className="text-sm">{doc.filename}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="w-full rounded-lg bg-primary px-4 py-3 font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Processing...
              </span>
            ) : (
              `Analyze with ${activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}`
            )}
          </button>

          {results && (
            <div className="rounded-lg border bg-card p-6">
              <h3 className="text-lg font-semibold mb-4">
                {activeTab === 'synthesis' && (results as { title?: string }).title}
                {activeTab === 'compare' && 'Comparison Results'}
                {activeTab === 'insights' && 'Extracted Insights'}
              </h3>
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <ReactMarkdown>
                  {JSON.stringify(results, null, 2)}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>

        <div className="rounded-lg border bg-card p-4">
          <h3 className="font-medium mb-4">Quick Info</h3>
          <div className="space-y-4 text-sm">
            {activeTab === 'synthesis' && (
              <p className="text-muted-foreground">
                Synthesis combines information from multiple documents to create
                a coherent summary. The AI identifies themes, contradictions,
                and key findings across your documents.
              </p>
            )}
            {activeTab === 'compare' && (
              <p className="text-muted-foreground">
                Compare two documents to identify similarities, differences,
                and conflicts. Great for comparing contract versions or proposals.
              </p>
            )}
            {activeTab === 'insights' && (
              <p className="text-muted-foreground">
                Extract structured insights including action items, decisions,
                deadlines, risks, and key metrics from your documents.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
