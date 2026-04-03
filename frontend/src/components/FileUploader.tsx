import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, CheckCircle, Loader2 } from 'lucide-react'
import { cn, formatFileSize } from '@/lib/utils'
import { documentApi } from '@/services/api'
import { useAppStore } from '@/store'
import toast from 'react-hot-toast'

export default function FileUploader() {
  const [files, setFiles] = useState<Array<{ file: File; status: 'pending' | 'uploading' | 'success' | 'error'; docId?: string }>>([])
  const { addDocument } = useAppStore()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [
      ...prev,
      ...acceptedFiles.map((file) => ({ file, status: 'pending' as const })),
    ])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/*': ['.png', '.jpg', '.jpeg'],
    },
  })

  const uploadFile = async (file: File, index: number) => {
    setFiles((prev) =>
      prev.map((f, i) => (i === index ? { ...f, status: 'uploading' as const } : f))
    )

    try {
      const response = await documentApi.ingestFile(file)
      setFiles((prev) =>
        prev.map((f, i) =>
          i === index ? { ...f, status: 'success' as const, docId: response.document_id } : f
        )
      )
      addDocument(response.metadata)
      toast.success(`Uploaded: ${file.name}`)
    } catch (error) {
      setFiles((prev) =>
        prev.map((f, i) => (i === index ? { ...f, status: 'error' as const } : f))
      )
      toast.error(`Failed: ${file.name}`)
    }
  }

  const uploadAll = async () => {
    await Promise.all(
      files
        .filter((f) => f.status === 'pending')
        .map((f, i) => uploadFile(f.file, files.indexOf(f)))
    )
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragActive
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-primary/50'
        )}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
        <p className="mt-4 text-lg font-medium">
          {isDragActive ? 'Drop files here' : 'Drag & drop files or click to browse'}
        </p>
        <p className="mt-2 text-sm text-muted-foreground">
          PDF, DOCX, TXT, PNG, JPG supported
        </p>
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">{files.length} file(s)</span>
            {files.some((f) => f.status === 'pending') && (
              <button
                onClick={uploadAll}
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                Upload All
              </button>
            )}
          </div>

          <div className="space-y-2">
            {files.map((item, index) => (
              <div
                key={index}
                className="flex items-center justify-between rounded-lg border bg-card p-3"
              >
                <div className="flex items-center gap-3">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{item.file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(item.file.size)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {item.status === 'pending' && (
                    <button
                      onClick={() => uploadFile(item.file, index)}
                      className="rounded-md bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90"
                    >
                      Upload
                    </button>
                  )}
                  {item.status === 'uploading' && (
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                  )}
                  {item.status === 'success' && (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  )}
                  {item.status === 'error' && (
                    <span className="text-xs text-destructive">Failed</span>
                  )}
                  <button
                    onClick={() => removeFile(index)}
                    className="rounded-md p-1 hover:bg-accent"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
