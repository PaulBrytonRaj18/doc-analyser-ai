"""
Pydantic Models for API Request/Response Validation.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentIngestRequest(BaseModel):
    text: str = Field(..., description="Document text content")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(default="text/plain", description="MIME type")
    document_type: Optional[str] = Field(None, description="Document classification")
    summary: Optional[str] = Field(None, description="Document summary")
    tags: Optional[List[str]] = Field(default_factory=list, description="Document tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    chunking_strategy: str = Field(default="recursive", description="Chunking strategy")


# EntityExtraction and AnalysisMetadata are defined later but used in DocumentAnalysisResponse, so we define them here first to avoid circular references.

class EntityExtraction(BaseModel):
    persons: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    monetary_values: List[str] = Field(default_factory=list)


class AnalysisMetadata(BaseModel):
    file_type: str
    processing_time: str
    num_pages: Optional[str] = None


class DocumentAnalyzeRequest(BaseModel):
    query: Optional[str] = Field(None, description="Optional RAG query")


class DocumentIngestResponse(BaseModel):
    status: str
    document_id: str
    filename: str
    file_type: str
    total_chunks: int
    processing_time_ms: float
    metadata: Dict[str, Any]


class DocumentBatchItem(BaseModel):
    text: str
    filename: str
    file_type: str = "text/plain"
    document_type: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentBatchRequest(BaseModel):
    documents: List[DocumentBatchItem]
    chunking_strategy: str = "recursive"


class BatchResultItem(BaseModel):
    document_id: str
    filename: str
    status: str
    chunks_created: int
    error: Optional[str] = None


class DocumentBatchResponse(BaseModel):
    total: int
    successful: int
    failed: int
    results: List[BatchResultItem]


class DocumentDeleteResponse(BaseModel):
    status: str
    document_id: str
    message: str


class DocumentAnalysisRequest(BaseModel):
    text: str = Field(..., description="Document text")
    document_id: Optional[str] = Field(None, description="Document ID")


class DocumentAnalysisResponse(BaseModel):
    status: str = Field(default="success")
    document_id: str
    summary: str
    entities: EntityExtraction
    sentiment: str
    metadata: AnalysisMetadata


class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="User question")
    top_k: Optional[int] = Field(None, description="Number of results")
    max_context_chunks: Optional[int] = Field(
        None, description="Max chunks for context"
    )
    filter_dict: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    streaming: bool = Field(default=False, description="Enable streaming")


class SourceReference(BaseModel):
    id: str
    document_id: str
    filename: str
    score: float
    page: Optional[int] = None
    preview: str


class Citation(BaseModel):
    chunk_id: str
    text: str
    score: float
    document_id: str


class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[SourceReference]
    citations: List[Citation]
    confidence: float
    processing_time_ms: float
    query: Optional[str] = None


class RAGSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: Optional[int] = Field(None, description="Number of results")
    filter_dict: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class SearchResultItem(BaseModel):
    result_id: str
    score: float
    content: str
    document_id: Optional[str] = None
    filename: Optional[str] = None
    page: Optional[int] = None
    chunk_index: Optional[int] = None


class RAGSearchResponse(BaseModel):
    total: int
    results: List[SearchResultItem]


class SynthesisSection(BaseModel):
    title: str
    content: str
    confidence: float = 0.0


class SynthesisRequest(BaseModel):
    query: str = Field(..., description="Synthesis topic or question")
    max_documents: int = Field(default=10, description="Max documents to analyze")


class SynthesisResponse(BaseModel):
    query: str
    title: str
    executive_summary: str
    sections: List[SynthesisSection]
    source_documents: List[Dict[str, Any]]
    key_findings: List[str]
    contradictions: List[Dict[str, Any]] = []
    confidence_score: float
    processing_time_ms: float
    metadata: Dict[str, Any] = {}


class ComparisonRequest(BaseModel):
    document1_id: str
    document2_id: str


class ComparisonResponse(BaseModel):
    document1: Dict[str, Any]
    document2: Dict[str, Any]
    overall_similarity: float
    content_overlap: float
    semantic_similarity: float
    structure_similarity: float = 0.0
    common_topics: List[str]
    unique_to_doc1: List[str] = []
    unique_to_doc2: List[str] = []
    key_differences: List[str]
    conflict_areas: List[Dict[str, Any]]
    recommendations: List[str]
    processing_time_ms: float = 0


class InsightExtractionRequest(BaseModel):
    text: Optional[str] = Field(None, description="Document text")
    document_id: Optional[str] = Field(None, description="Document ID")
    filename: Optional[str] = Field(None, description="Filename")


class InsightItem(BaseModel):
    type: str
    title: str
    description: str
    confidence: float
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"


class InsightExtractionResponse(BaseModel):
    document_id: str
    filename: str
    action_items: List[InsightItem]
    decisions: List[InsightItem]
    deadlines: List[InsightItem]
    risks: List[InsightItem]
    opportunities: List[InsightItem]
    key_metrics: List[InsightItem]
    summary: str
    confidence_score: float
    processing_time_ms: float = 0


class InsightReportResponse(BaseModel):
    title: str
    executive_summary: str
    critical_findings: List[str]
    recommendations: List[str]
    risk_assessment: Dict[str, int]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    features: Dict[str, bool]


# OCR Schemas

class OCRScanRequest(BaseModel):
    language: Optional[str] = Field(None, description="Language code")
    auto_preprocess: bool = Field(True, description="Enable preprocessing")


class OCRRegion(BaseModel):
    region_id: int
    text: str
    confidence: float
    bounding_box: Dict[str, int] = Field(default_factory=dict)
    engine_used: str = "tesseract"


class OCRResult(BaseModel):
    full_text: str
    language_detected: str
    overall_confidence: float
    regions: List[OCRRegion] = Field(default_factory=list)
    low_confidence_regions: List[int] = Field(default_factory=list)
    preprocessing_applied: List[str] = Field(default_factory=list)


class OCRScanResponse(BaseModel):
    document_id: str
    ocr_result: OCRResult
    processing_time_ms: int


class OCRPreviewResponse(BaseModel):
    original_size: List[int]
    processed_size: List[int]
    ocr_overlay: str


class OCRLanguagesResponse(BaseModel):
    languages: List[Dict[str, Any]]


# Analysis Schemas

class CompareRequest(BaseModel):
    document_id_a: str
    document_id_b: str
    focus: Optional[str] = None


class CompareResponse(BaseModel):
    document1: Dict[str, Any]
    document2: Dict[str, Any]
    overall_similarity: float
    content_overlap: float
    semantic_similarity: float
    similar_sections: List[Dict[str, Any]]
    key_differences: List[str]
    processing_time_ms: int


class RedactRequest(BaseModel):
    document_id: str
    pii_types: List[str] = Field(default_factory=lambda: ["person_name", "email_address"])
    replacement: str = "[REDACTED]"
    overwrite: bool = False


class RedactResponse(BaseModel):
    document_id: str
    status: str
    redacted_text: str
    redactions_applied: int
    processing_time_ms: int


class BatchUploadRequest(BaseModel):
    files: List[str]


class BatchStatusResponse(BaseModel):
    batch_id: str
    status: str
    total_files: int
    processed_files: int
    failed_files: int


class ExportRequest(BaseModel):
    document_id: str
    format: str = "json"


# Upload Schemas

class UploadRequest(BaseModel):
    auto_analyze: bool = True


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    status: str
    processing_status: str
    analysis: Optional[Dict[str, Any]] = None
    processing_time_ms: int


class UploadStreamEvent(BaseModel):
    step: str
    progress: int
    message: Optional[str] = None
    document_id: Optional[str] = None


class UploadStreamResponse(BaseModel):
    event: str
    data: UploadStreamEvent


class WebhookRegisterRequest(BaseModel):
    url: str = Field(..., description="Webhook URL")
    events: List[str] = Field(..., description="List of events to subscribe to")
    secret: Optional[str] = Field(None, description="Webhook secret for signing")
    enabled: bool = Field(default=True, description="Enable/disable webhook")


class WebhookItem(BaseModel):
    id: str
    url: str
    events: List[str]
    enabled: bool
    created_at: datetime
    updated_at: datetime


class WebhookRegisterResponse(BaseModel):
    id: str
    url: str
    events: List[str]
    enabled: bool
    created_at: datetime


class WebhookListResponse(BaseModel):
    total: int
    webhooks: List[WebhookItem]


