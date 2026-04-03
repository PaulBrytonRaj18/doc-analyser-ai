export interface Document {
  document_id: string
  filename: string
  file_type: string
  file_size?: number
  total_chunks?: number
  uploaded_at?: string
  document_type?: string
  summary?: string
  tags?: string[]
  metadata?: Record<string, unknown>
}

export interface DocumentIngestResponse {
  status: string
  document_id: string
  filename: string
  file_type: string
  total_chunks: number
  processing_time_ms: number
  metadata: Document
}

export interface RAGQueryRequest {
  query: string
  top_k?: number
  max_context_chunks?: number
  filter_dict?: Record<string, unknown>
  streaming?: boolean
}

export interface SourceReference {
  id: string
  document_id: string
  filename: string
  score: number
  page?: number
  preview: string
}

export interface RAGQueryResponse {
  answer: string
  sources: SourceReference[]
  citations: Citation[]
  confidence: number
  processing_time_ms: number
}

export interface Citation {
  chunk_id: string
  text: string
  score: number
  document_id: string
}

export interface SearchResult {
  result_id: string
  score: number
  content: string
  document_id?: string
  filename?: string
  page?: number
  chunk_index?: number
}

export interface SynthesisSection {
  title: string
  content: string
  confidence: number
}

export interface SynthesisResponse {
  query: string
  title: string
  executive_summary: string
  sections: SynthesisSection[]
  source_documents: Array<{
    document_id: string
    filename: string
    score: number
  }>
  key_findings: string[]
  contradictions: Array<Record<string, unknown>>
  confidence_score: number
  processing_time_ms: number
}

export interface ComparisonResponse {
  document1: {
    id: string
    filename: string
    content_length: number
  }
  document2: {
    id: string
    filename: string
    content_length: number
  }
  overall_similarity: number
  content_overlap: number
  semantic_similarity: number
  structure_similarity: number
  common_topics: string[]
  unique_to_doc1: string[]
  unique_to_doc2: string[]
  key_differences: string[]
  conflict_areas: Array<Record<string, unknown>>
  recommendations: string[]
  processing_time_ms: number
}

export interface InsightItem {
  type: string
  title: string
  description: string
  confidence: number
  assigned_to?: string
  due_date?: string
  priority: string
}

export interface InsightExtractionResponse {
  document_id: string
  filename: string
  action_items: InsightItem[]
  decisions: InsightItem[]
  deadlines: InsightItem[]
  risks: InsightItem[]
  opportunities: InsightItem[]
  key_metrics: InsightItem[]
  summary: string
  confidence_score: number
  processing_time_ms: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: SourceReference[]
  timestamp: Date
  isLoading?: boolean
}

export interface HealthStatus {
  status: string
  service: string
  version: string
  features: {
    rag: boolean
    cache: boolean
    streaming: boolean
  }
}
