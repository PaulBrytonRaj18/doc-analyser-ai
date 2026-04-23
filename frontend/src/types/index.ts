export interface Document {
  document_id: string
  filename: string
  file_type: string
  file_size?: number
  total_chunks?: number
  uploaded_at?: string
  document_type?: string
  sub_type?: string
  classification_confidence?: number
  summary?: string
  rag_ingested?: boolean
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

export interface UploadResponse {
  status: string
  document_id: string
  filename: string
  processing_status: string
  message?: string
}

export interface UploadStreamResponse {
  type: string
  document_id: string
  step: string
  progress: number
  data?: any
}

export interface ClassificationResult {
  type: string
  sub_type?: string
  confidence: number
}

export interface SummaryResult {
  summary: string
  word_count: number
}

export interface EntityResult {
  persons: string[]
  organizations: string[]
  dates: string[]
  locations: string[]
  monetary_values: string[]
  invoice_numbers: string[]
  email_addresses: string[]
  phone_numbers: string[]
}

export interface SentimentResult {
  label: string
  score: number
}

export interface InsightResult {
  insights: string[]
}

export interface TableData {
  table_id: number
  headers: string[]
  rows: string[][]
  caption?: string
}

export interface TableExtractionResult {
  tables: TableData[]
}

export interface PIIResult {
  pii_detected: boolean
  pii_types: string[]
  locations: any[]
}

export interface AnalysisResult {
  document_id: string
  status: string
  classification: ClassificationResult
  summary: string
  entities: EntityResult
  sentiment: SentimentResult
  key_insights: string[]
  tables: TableData[]
  pii_detected: boolean
  pii_types: string[]
  processing_time_ms: number
}

export interface BatchJobStatus {
  batch_id: string
  status: string
  total_files: number
  processed_files: number
  failed_files: number
  results?: Array<{
    filename: string
    status: string
    error?: string
  }>
  created_at: string
  completed_at?: string
}

export interface RAGQueryRequest {
  query: string
  document_id?: string
  document_ids?: string[]
  top_k?: number
  filter_dict?: Record<string, unknown>
  streaming?: boolean
}

export interface SourceReference {
  id: string
  document_id: string
  chunk_id: string
  filename: string
  score: number
  page?: number
  region?: any
  preview: string
}

export interface Citation {
  document_id: string
  chunk_id: string
  page?: number
  region?: any
  excerpt: string
  relevance_score: number
}

export interface RAGQueryResponse {
  answer: string
  confidence: number
  sources: Citation[]
  follow_up_suggestions: string[]
  processing_time_ms: number
}

export interface QAHistoryItem {
  id: string
  query: string
  response: string
  sources?: Citation[]
  created_at: string
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
  similar_sections: Array<{
    section1: string
    section2: string
    similarity: number
  }>
  key_differences: string[]
  processing_time_ms: number
}

export interface RedactionRequest {
  document_id: string
  pii_types: string[]
  replacement?: string
  overwrite?: boolean
}

export interface RedactionResponse {
  document_id: string
  status: string
  redacted_text: string
  redactions_applied: number
  processing_time_ms: number
}

export interface OCRResult {
  document_id: string
  ocr_result: {
    full_text: string
    language_detected: string
    overall_confidence: number
    regions: Array<{
      region_id: number
      text: string
      confidence: number
      bounding_box: any
      engine_used: string
    }>
    low_confidence_regions: number[]
    preprocessing_applied: string[]
  }
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

export interface WebhookConfig {
  id: string
  url: string
  events: string[]
  active: boolean
  created_at: string
}

export interface AuditLogEntry {
  id: string
  timestamp: string
  request_id: string
  user_id?: string
  action: string
  resource_type?: string
  resource_id?: string
  request_path: string
  request_method: string
  response_status: number
  ip_address?: string
}

export interface HealthStatus {
  status: string
  service: string
  version: string
  features: {
    rag: boolean
    cache: boolean
    streaming: boolean
    ocr: boolean
    batch: boolean
  }
}

export interface OCRRegion {
  region_id: number
  text: string
  confidence: number
  bounding_box: Record<string, number>
  engine_used: string
}

export interface OCRResult {
  full_text: string
  language_detected: string
  overall_confidence: number
  regions: OCRRegion[]
  low_confidence_regions: number[]
  preprocessing_applied: string[]
}

export interface OCRScanResponse {
  document_id: string
  ocr_result: OCRResult
  processing_time_ms: number
}