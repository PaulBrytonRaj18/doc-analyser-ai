import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useAppStore } from '@/store'
import { uploadApi } from '@/services/api'
import { Upload, FileText, X, CheckCircle, Loader2, AlertCircle } from 'lucide-react'
import { formatFileSize } from '@/lib/utils'
import toast from 'react-hot-toast'

interface FileItem {
  file: File
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
}

export default function BatchProcessor() {
  const [files, setFiles] = useState<FileItem[]>([])
  const [batchId, setBatchId] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [overallProgress, setOverallProgress] = useState(0)
  const { addBatchJob } = useAppStore()

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

  const startBatchUpload = async () => {
    if (files.length === 0) return

    setIsProcessing(true)
    setOverallProgress(0)

    setFiles((prev) =>
      prev.map((f) => (f.status === 'pending' ? { ...f, status: 'uploading' as const } : f))
    )

    try {
      const pendingFiles = files.filter((f) => f.status === 'pending')
      const response = await uploadApi.batch(pendingFiles.map((f) => f.file))
      setBatchId(response.batch_id)

      addBatchJob({
        batch_id: response.batch_id,
        status: 'processing',
        total_files: pendingFiles.length,
        processed_files: 0,
        failed_files: 0,
        created_at: new Date().toISOString(),
      })

      toast.success(`Batch started with ${pendingFiles.length} files`)
    } catch (error) {
      setFiles((prev) =>
        prev.map((f) =>
          f.status === 'uploading'
            ? { ...f, status: 'error' as const, error: 'Failed to start batch' }
            : f
        )
      )
      toast.error('Failed to start batch upload')
    } finally {
      setIsProcessing(false)
    }
  }

  const checkBatchStatus = async () => {
    if (!batchId) return

    try {
      const status = await uploadApi.batchStatus(batchId)
      setOverallProgress(
        status.total_files > 0
          ? Math.round((status.processed_files / status.total_files) * 100)
          : 0
      )

      setFiles((prev) =>
        prev.map((f, i) => {
          const result = status.results?.[i]
          if (result) {
            return {
              ...f,
              status: result.status === 'completed' ? 'success' : 'error',
              error: result.error,
            }
          }
          return f
        })
      )

      if (status.status === 'completed') {
        toast.success('Batch processing completed')
        setIsProcessing(false)
      }
    } catch (error) {
      toast.error('Failed to check batch status')
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const clearCompleted = () => {
    setFiles((prev) => prev.filter((f) => f.status !== 'success'))
  }

  const pendingCount = files.filter((f) => f.status === 'pending').length
  const completedCount = files.filter((f) => f.status === 'success').length

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-slate-100 mb-6">
        Batch Processor
      </h1>

      <div className="bg-slate-800 rounded-lg p-6 mb-6">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-cyan-500 bg-cyan-500/5'
              : 'border-slate-600 hover:border-cyan-500/50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-slate-400" />
          <p className="mt-4 text-lg font-medium text-slate-200">
            {isDragActive ? 'Drop files here' : 'Drag & drop files or click to browse'}
          </p>
          <p className="mt-2 text-sm text-slate-400">
            PDF, DOCX, TXT, PNG, JPG supported
          </p>
        </div>

        {files.length > 0 && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-slate-300 font-medium">
                {files.length} file(s) • {completedCount} completed • {pendingCount} pending
              </span>
              <div className="flex gap-2">
                {completedCount > 0 && (
                  <button
                    onClick={clearCompleted}
                    className="rounded-md bg-slate-700 px-3 py-1.5 text-sm font-medium text-slate-200 hover:bg-slate-600"
                  >
                    Clear Completed
                  </button>
                )}
                {pendingCount > 0 && !isProcessing && (
                  <button
                    onClick={startBatchUpload}
                    className="rounded-md bg-cyan-600 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-500"
                  >
                    Start Batch Upload
                  </button>
                )}
              </div>
            </div>

            {isProcessing && (
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm text-slate-400 mb-2">
                  <span>Processing...</span>
                  <span>{overallProgress}%</span>
                </div>
                <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-500 transition-all duration-300"
                    style={{ width: `${overallProgress}%` }}
                  />
                </div>
                {batchId && (
                  <button
                    onClick={checkBatchStatus}
                    className="mt-2 text-sm text-cyan-400 hover:text-cyan-300"
                  >
                    Check Status
                  </button>
                )}
              </div>
            )}

            <div className="space-y-2">
              {files.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-900 p-3"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-slate-400" />
                    <div>
                      <p className="text-sm font-medium text-slate-200">{item.file.name}</p>
                      <p className="text-xs text-slate-500">{formatFileSize(item.file.size)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {item.status === 'pending' && (
                      <span className="text-xs text-slate-500">Pending</span>
                    )}
                    {item.status === 'uploading' && (
                      <Loader2 className="h-5 w-5 animate-spin text-cyan-500" />
                    )}
                    {item.status === 'success' && (
                      <CheckCircle className="h-5 w-5 text-emerald-500" />
                    )}
                    {item.status === 'error' && (
                      <div className="flex items-center gap-2">
                        <AlertCircle className="h-5 w-5 text-rose-500" />
                        <span className="text-xs text-rose-400">{item.error || 'Failed'}</span>
                      </div>
                    )}
                    <button
                      onClick={() => removeFile(index)}
                      className="rounded-md p-1 hover:bg-slate-800"
                    >
                      <X className="h-4 w-4 text-slate-400" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}