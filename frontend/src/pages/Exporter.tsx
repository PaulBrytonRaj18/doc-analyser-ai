import { useState } from 'react'
import { useAppStore } from '@/store'
import { exportApi } from '@/services/api'
import { FileText, Download, FileJson, FileSpreadsheet, File, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

type ExportFormat = 'json' | 'csv' | 'markdown' | 'pdf_report'

interface FormatOption {
  value: ExportFormat
  label: string
  icon: React.ElementType
  description: string
}

const formats: FormatOption[] = [
  { value: 'json', label: 'JSON', icon: FileJson, description: 'Full structured data with metadata' },
  { value: 'csv', label: 'CSV', icon: FileSpreadsheet, description: 'Tabular format for spreadsheets' },
  { value: 'markdown', label: 'Markdown', icon: File, description: 'Formatted text document' },
  { value: 'pdf_report', label: 'PDF Report', icon: FileText, description: 'Print-ready PDF document' },
]

export default function Exporter() {
  const { documents } = useAppStore()
  const [selectedDocId, setSelectedDocId] = useState<string>('')
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('json')
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async () => {
    if (!selectedDocId) {
      toast.error('Please select a document')
      return
    }

    setIsExporting(true)

    try {
      const blob = await exportApi.document(selectedDocId, selectedFormat)

      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      const ext = selectedFormat === 'pdf_report' ? 'pdf' : selectedFormat
      const filename = `export_${selectedDocId.slice(0, 8)}_${Date.now()}.${ext}`
      link.download = filename

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.success(`Exported as ${selectedFormat.toUpperCase()}`)
    } catch (error) {
      toast.error('Export failed')
    } finally {
      setIsExporting(false)
    }
  }

  const selectedDocument = documents.find((d) => d.document_id === selectedDocId)

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-slate-100 mb-6">
        Export Documents
      </h1>

      <div className="bg-slate-800 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">
          Select Document
        </h2>

        {documents.length === 0 ? (
          <p className="text-slate-400">No documents available. Upload documents first.</p>
        ) : (
          <div className="space-y-2 mb-6">
            {documents.map((doc) => (
              <button
                key={doc.document_id}
                onClick={() => setSelectedDocId(doc.document_id)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg border text-left transition-colors ${
                  selectedDocId === doc.document_id
                    ? 'border-cyan-500 bg-cyan-500/10'
                    : 'border-slate-700 bg-slate-900 hover:border-slate-600'
                }`}
              >
                <FileText className="h-5 w-5 text-slate-400" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-200">
                    {doc.filename || doc.document_id}
                  </p>
                  <p className="text-xs text-slate-500">
                    {doc.document_type} • {doc.metadata?.page_count || 1} pages
                  </p>
                </div>
              </button>
            ))}
          </div>
        )}

        <h2 className="text-lg font-semibold text-slate-100 mb-4">
          Export Format
        </h2>

        <div className="grid grid-cols-2 gap-3 mb-6">
          {formats.map((format) => (
            <button
              key={format.value}
              onClick={() => setSelectedFormat(format.value)}
              className={`flex items-start gap-3 p-4 rounded-lg border text-left transition-colors ${
                selectedFormat === format.value
                  ? 'border-cyan-500 bg-cyan-500/10'
                  : 'border-slate-700 bg-slate-900 hover:border-slate-600'
              }`}
            >
              <format.icon className="h-5 w-5 text-cyan-400 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-slate-200">{format.label}</p>
                <p className="text-xs text-slate-500">{format.description}</p>
              </div>
            </button>
          ))}
        </div>

        {selectedDocument && (
          <div className="bg-slate-900 rounded-lg p-4 mb-6">
            <h3 className="text-sm font-medium text-slate-400 mb-2">Export Preview</h3>
            <p className="text-slate-200">
              {selectedDocument.filename || selectedDocument.document_id}
            </p>
            <p className="text-sm text-slate-500">
              Format: {selectedFormat.toUpperCase()}
            </p>
          </div>
        )}

        <button
          onClick={handleExport}
          disabled={!selectedDocId || isExporting}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-cyan-600 px-4 py-3 font-medium text-white hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isExporting ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Exporting...
            </>
          ) : (
            <>
              <Download className="h-5 w-5" />
              Export Document
            </>
          )}
        </button>
      </div>
    </div>
  )
}