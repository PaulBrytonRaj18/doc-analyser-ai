import axios from 'axios'
import type {
  Document,
  DocumentIngestResponse,
  UploadResponse,
  UploadStreamResponse,
  AnalysisResult,
  ClassificationResult,
  SummaryResult,
  EntityResult,
  SentimentResult,
  InsightResult,
  TableExtractionResult,
  PIIResult,
  RAGQueryRequest,
  RAGQueryResponse,
  SearchResult,
  ComparisonResponse,
  RedactionRequest,
  RedactionResponse,
  OCRResult,
  QAHistoryItem,
  BatchJobStatus,
  WebhookConfig,
  AuditLogEntry,
  HealthStatus,
} from '@/types'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('api_key')
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('api_key')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const uploadApi = {
  upload: async (file: File, onProgress?: (progress: number) => void): Promise<UploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/v1/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100)
          onProgress(progress)
        }
      },
    })
    return response.data
  },

  uploadStream: async (file: File): Promise<AsyncIterable<UploadStreamResponse>> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/v1/upload/stream', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      responseType: 'stream',
    })
    return response.data
  },

  batch: async (files: File[]): Promise<{ batch_id: string }> => {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    
    const response = await api.post('/v1/batch/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  batchStatus: async (batchId: string): Promise<BatchJobStatus> => {
    const response = await api.get(`/v1/batch/${batchId}/status`)
    return response.data
  },
}

export const documentApi = {
  list: async (): Promise<Document[]> => {
    const response = await api.get('/v1/documents')
    return response.data
  },

  get: async (documentId: string): Promise<Document> => {
    const response = await api.get(`/v1/documents/${documentId}`)
    return response.data
  },

  delete: async (documentId: string): Promise<void> => {
    await api.delete(`/v1/documents/${documentId}`)
  },

  ingest: async (data: { text: string; filename: string; document_type?: string }): Promise<DocumentIngestResponse> => {
    const response = await api.post('/v1/documents/ingest', data)
    return response.data
  },

  ingestFile: async (file: File, documentType?: string): Promise<DocumentIngestResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    if (documentType) {
      formData.append('document_type', documentType)
    }
    const response = await api.post('/v1/documents/ingest/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

export const ocrApi = {
  scan: async (file: File, language?: string): Promise<OCRResult> => {
    const formData = new FormData()
    formData.append('file', file)
    if (language) {
      formData.append('language', language)
    }
    
    const response = await api.post('/v1/ocr/scan', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  scanPreview: async (file: File): Promise<{ preview_url: string; ocr_overlay: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/v1/ocr/scan/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  detectLanguage: async (file: File): Promise<{ languages: Array<{ language: string; confidence: number }> }> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/v1/ocr/languages', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

export const analyzeApi = {
  get: async (documentId: string): Promise<AnalysisResult> => {
    const response = await api.get(`/v1/analyze/${documentId}`)
    return response.data
  },

  text: async (text: string): Promise<AnalysisResult> => {
    const response = await api.post('/v1/analyze/text', { text })
    return response.data
  },

  file: async (file: File): Promise<AnalysisResult> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/v1/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

export const compareApi = {
  compare: async (docIdA: string, docIdB: string, focus?: string): Promise<ComparisonResponse> => {
    const response = await api.post('/v1/compare', {
      document_id_a: docIdA,
      document_id_b: docIdB,
      focus,
    })
    return response.data
  },
}

export const redactApi = {
  redact: async (data: RedactionRequest): Promise<RedactionResponse> => {
    const response = await api.post('/v1/redact', data)
    return response.data
  },
}

export const ragApi = {
  query: async (data: RAGQueryRequest): Promise<RAGQueryResponse> => {
    const response = await api.post('/v1/rag/query', data)
    return response.data
  },

  search: async (data: { query: string; top_k?: number }): Promise<{ total: number; results: SearchResult[] }> => {
    const response = await api.post('/v1/rag/search', data)
    return response.data
  },

  history: async (documentId: string): Promise<QAHistoryItem[]> => {
    const response = await api.get(`/v1/rag/history/${documentId}`)
    return response.data
  },

  getStats: async (): Promise<Record<string, unknown>> => {
    const response = await api.get('/v1/rag/stats')
    return response.data
  },
}

export const exportApi = {
  document: async (documentId: string, format: 'json' | 'csv' | 'markdown' | 'pdf_report'): Promise<Blob> => {
    const response = await api.get(`/v1/documents/${documentId}/export`, {
      params: { format },
      responseType: 'blob',
    })
    return response.data
  },

  batch: async (batchId: string, format: 'json' | 'csv' | 'zip'): Promise<Blob> => {
    const response = await api.get(`/v1/batch/${batchId}/export`, {
      params: { format },
      responseType: 'blob',
    })
    return response.data
  },
}

export const webhookApi = {
  register: async (data: { url: string; events: string[] }): Promise<WebhookConfig> => {
    const response = await api.post('/v1/webhooks/register', data)
    return response.data
  },

  list: async (): Promise<WebhookConfig[]> => {
    const response = await api.get('/v1/webhooks')
    return response.data
  },

  delete: async (webhookId: string): Promise<void> => {
    await api.delete(`/v1/webhooks/${webhookId}`)
  },
}

export const auditApi = {
  getLogs: async (limit?: number, offset?: number): Promise<AuditLogEntry[]> => {
    const response = await api.get('/v1/audit/logs', {
      params: { limit, offset },
    })
    return response.data
  },

  verifyChain: async (): Promise<{ valid: boolean; errors: any[] }> => {
    const response = await api.post('/v1/audit/verify')
    return response.data
  },
}

export const systemApi = {
  health: async (): Promise<HealthStatus> => {
    const response = await api.get('/health')
    return response.data
  },
}

export default api