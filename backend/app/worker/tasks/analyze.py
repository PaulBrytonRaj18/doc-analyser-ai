"""Auto-Analysis Background Task - Celery"""

from celery import Task
from celery.result import AsyncResult

from app.worker import celery_app


@celery_app.task(bind=True, name="app.worker.tasks.analyze.run_analysis")
def run_analysis(self: Task, document_id: str, file_path: str) -> AsyncResult:
    """Run auto-analysis on a document."""
    from app.services.processing.file_processor import FileProcessor
    from app.services.analysis.classifier import ClassificationService
    from app.services.analysis.summarizer import SummarizationService
    from app.services.analysis.ner import NERService
    from app.services.analysis.sentiment import SentimentService
    from app.services.analysis.insights import InsightsService
    from app.services.analysis.table import TableExtractor
    from app.services.analysis.pii_detector import PIIDetector
    from app.services.rag.ingest import RAGIngestService

    try:
        processor = FileProcessor()
        classifier = ClassificationService()
        summarizer = SummarizationService()
        ner = NERService()
        sentiment = SentimentService()
        insights = InsightsService()
        table_extractor = TableExtractor()
        pii_detector = PIIDetector()
        rag_ingest = RAGIngestService()

        result = processor.process_file(file_path)

        if result.status == "failed":
            raise Exception(result.error)

        text_content = result.text

        update_state = self.update_state
        update_state(
            state="PROCESSING",
            meta={"step": "Classifying document", "progress": 10},
        )

        classification = classifier.classify(text_content)

        update_state(
            state="PROCESSING",
            meta={"step": "Summarizing", "progress": 30},
        )

        summary = summarizer.summarize(text_content)

        update_state(
            state="PROCESSING",
            meta={"step": "Extracting entities", "progress": 50},
        )

        entities = ner.extract_entities(text_content)

        update_state(
            state="PROCESSING",
            meta={"step": "Analyzing sentiment", "progress": 60},
        )

        sentiment_result = sentiment.analyze(text_content)

        update_state(
            state="PROCESSING",
            meta={"step": "Extracting insights", "progress": 70},
        )

        key_insights = insights.extract(text_content)

        update_state(
            state="PROCESSING",
            meta={"step": "Extracting tables", "progress": 80},
        )

        tables = table_extractor.extract(text_content)

        update_state(
            state="PROCESSING",
            meta={"step": "Detecting PII", "progress": 90},
        )

        pii_result = pii_detector.detect(text_content)

        update_state(
            state="PROCESSING",
            meta={"step": "Ingesting to RAG", "progress": 95},
        )

        rag_result = rag_ingest.ingest(document_id, text_content)

        return {
            "document_id": document_id,
            "status": "success",
            "classification": classification,
            "summary": summary,
            "entities": entities,
            "sentiment": sentiment_result,
            "key_insights": key_insights,
            "tables": tables,
            "pii_detected": pii_result,
            "rag_ingested": rag_result.status == "success",
        }

    except Exception as e:
        return {
            "document_id": document_id,
            "status": "failed",
            "error": str(e),
        }