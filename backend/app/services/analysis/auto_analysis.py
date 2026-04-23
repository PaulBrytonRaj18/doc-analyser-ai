"""
Auto-Analysis Service - DocuLens AI v4.0
Runs complete analysis pipeline on document upload
"""

import time
from dataclasses import dataclass

from app.core.config import settings
from app.services.analysis import (
    ClassificationService,
    SummarizationService,
    NERService,
    SentimentService,
    InsightsService,
    TableExtractor,
    PIIDetector,
)


@dataclass
class AutoAnalysisResult:
    document_id: str
    status: str
    classification: dict
    summary: str
    entities: dict
    sentiment: dict
    key_insights: list
    tables: list
    pii_result: dict
    processing_time_ms: int


class AutoAnalysisService:
    """Complete auto-analysis pipeline."""

    def __init__(self):
        self.classifier = ClassificationService()
        self.summarizer = SummarizationService()
        self.ner = NERService()
        self.sentiment = SentimentService()
        self.insights = InsightsService()
        self.tables = TableExtractor()
        self.pii = PIIDetector()

    def analyze(
        self,
        document_id: str,
        text: str,
        trigger_celery: bool = False,
    ) -> AutoAnalysisResult:
        """Run complete auto-analysis pipeline."""
        start_time = time.time()
        
        if trigger_celery and settings.celery_enabled:
            return self._analyze_async(document_id, text)
        
        return self._analyze_sync(document_id, text, start_time)

    def _analyze_sync(
        self,
        document_id: str,
        text: str,
        start_time: float,
    ) -> AutoAnalysisResult:
        """Synchronous analysis."""
        classification = self.classifier.classify(text)
        
        summary = self.summarizer.summarize(text)
        
        entities = self.ner.extract_entities(text)
        
        sentiment = self.sentiment.analyze(text)
        
        insights = self.insights.extract(text)
        
        table_result = self.tables.extract(text)
        
        pii_result = self.pii.detect(text)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return AutoAnalysisResult(
            document_id=document_id,
            status="success",
            classification={
                "type": classification.document_type,
                "sub_type": classification.sub_type,
                "confidence": classification.confidence,
            },
            summary=summary.summary,
            entities={
                "persons": entities.persons,
                "organizations": entities.organizations,
                "dates": entities.dates,
                "locations": entities.locations,
                "monetary_values": entities.monetary_values,
                "invoice_numbers": entities.invoice_numbers,
                "email_addresses": entities.email_addresses,
            },
            sentiment={
                "label": sentiment.label,
                "score": sentiment.score,
            },
            key_insights=insights.insights,
            tables=[t.__dict__ for t in table_result.tables],
            pii_result={
                "pii_detected": pii_result.pii_detected,
                "pii_types": pii_result.pii_types,
            },
            processing_time_ms=processing_time_ms,
        )

    def _analyze_async(self, document_id: str, text: str):
        """Queue analysis to Celery."""
        from app.worker.tasks.analyze import run_analysis
        
        run_analysis.apply_async(args=[document_id, text])
        
        return AutoAnalysisResult(
            document_id=document_id,
            status="queued",
            classification={},
            summary="",
            entities={},
            sentiment={},
            key_insights=[],
            tables=[],
            pii_result={},
            processing_time_ms=0,
        )


auto_analysis_service = AutoAnalysisService()