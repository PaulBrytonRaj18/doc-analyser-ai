"""
PDF Report Generator - DocuLens AI v4.0
"""

import io
from datetime import datetime
from typing import Dict, Any, List, Optional


class PDFExporter:
    """Export analysis results to PDF report."""

    def export(
        self,
        analysis_data: Dict[str, Any],
        document_metadata: Dict[str, Any],
        format_type: str = "report",
    ) -> bytes:
        """Export to PDF format."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
            )
            from reportlab.lib import colors

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)

            elements = []
            styles = getSampleStyleSheet()

            title_style = styles['Title']
            title_style.textColor = colors.HexColor('#1E293B')
            
            elements.append(Paragraph("Document Analysis Report", title_style))
            elements.append(Spacer(1, 0.3*inch))

            elements.append(Paragraph(
                f"Document: {document_metadata.get('filename', 'Unknown')}",
                styles['Normal']
            ))
            elements.append(Paragraph(
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                styles['Normal']
            ))
            elements.append(Spacer(1, 0.2*inch))

            if analysis_data.get('classification'):
                elements.append(Paragraph("Classification", styles['Heading2']))
                class_data = analysis_data['classification']
                elements.append(Paragraph(
                    f"Type: {class_data.get('type', 'N/A')}", styles['Normal']
                ))
                elements.append(Paragraph(
                    f"Confidence: {class_data.get('confidence', 0):.1%}",
                    styles['Normal']
                ))
                elements.append(Spacer(1, 0.2*inch))

            if analysis_data.get('summary'):
                elements.append(Paragraph("Summary", styles['Heading2']))
                elements.append(Paragraph(
                    analysis_data['summary'][:500], styles['Normal']
                ))
                elements.append(Spacer(1, 0.2*inch))

            doc.build(elements)
            return buffer.getvalue()

        except ImportError:
            return self._simple_export(analysis_data, document_metadata)

    def _simple_export(
        self,
        analysis_data: Dict[str, Any],
        document_metadata: Dict[str, Any],
    ) -> bytes:
        """Simple text export as fallback."""
        content = f"Document Analysis Report\n"
        content += f"=" * 50 + "\n\n"
        content += f"Document: {document_metadata.get('filename', 'Unknown')}\n"
        content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

        if analysis_data.get('classification'):
            content += f"Classification: {analysis_data['classification'].get('type')}\n"
        if analysis_data.get('summary'):
            content += f"\nSummary:\n{analysis_data['summary']}\n"

        return content.encode('utf-8')


pdf_exporter = PDFExporter()