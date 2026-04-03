import { FileText, Trash2, CheckCircle, Clock, AlertTriangle } from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'
import { useAppStore } from '@/store'
import { documentApi } from '@/services/api'
import toast from 'react-hot-toast'

export default function DocumentList() {
  const { documents, removeDocument } = useAppStore()

  const handleDelete = async (id: string) => {
    try {
      await documentApi.delete(id)
      removeDocument(id)
      toast.success('Document deleted')
    } catch (error) {
      toast.error('Failed to delete document')
    }
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg">
        <FileText className="h-12 w-12 text-muted-foreground/50" />
        <h3 className="mt-4 text-lg font-medium">No documents yet</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Upload documents to get started
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.document_id}
          className="flex items-center justify-between rounded-lg border bg-card p-4"
        >
          <div className="flex items-center gap-3">
            <FileText className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="font-medium">{doc.filename}</p>
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <CheckCircle className="h-3 w-3 text-green-500" />
                  Indexed
                </span>
                {doc.total_chunks && (
                  <span>{doc.total_chunks} chunks</span>
                )}
                {doc.uploaded_at && (
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatDate(doc.uploaded_at)}
                  </span>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={() => handleDelete(doc.document_id)}
            className="rounded-md p-2 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  )
}
