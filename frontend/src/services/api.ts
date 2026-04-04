import axios from 'axios'
import type {
  DocumentIngestResponse,
  RAGQueryRequest,
  RAGQueryResponse,
  SearchResult,
  SynthesisResponse,
  ComparisonResponse,
  InsightExtractionResponse,
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

export const documentApi = {
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

  delete: async (documentId: string): Promise<void> => {
    await api.delete(`/v1/documents/${documentId}`)
  },

  analyze: async (data: { text: string; document_id?: string }): Promise<Record<string, unknown>> => {
    const response = await api.post('/v1/documents/analyze', data)
    return response.data
  },
}

export const analyzeApi = {
  analyzeFile: async (file: File): Promise<{
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
  }> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/v1/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  analyzeText: async (text: string): Promise<{
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
  }> => {
    const formData = new FormData()
    formData.append('text', text)
    const response = await api.post('/v1/analyze/text', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
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

  getStats: async (): Promise<Record<string, unknown>> => {
    const response = await api.get('/v1/rag/stats')
    return response.data
  },
}

export const analysisApi = {
  synthesize: async (data: { query: string; max_documents?: number }): Promise<SynthesisResponse> => {
    const response = await api.post('/v1/analysis/synthesize', data)
    return response.data
  },

  compare: async (data: { document1_id: string; document2_id: string }): Promise<ComparisonResponse> => {
    const response = await api.post('/v1/analysis/compare', data)
    return response.data
  },

  extractInsights: async (data: { document_id?: string; text?: string; filename?: string }): Promise<InsightExtractionResponse> => {
    const response = await api.post('/v1/analysis/insights', data)
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