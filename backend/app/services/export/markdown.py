"""
Markdown Exporter - DocuLens AI v4.0
"""

from datetime import datetime
from typing import Dict, Any


class MarkdownExporter:
    """Export analysis to Markdown format."""

    def export(
        self,
        analysis_data: Dict[str, Any],
        document_metadata: Dict[str, Any],
    ) -> str:
        """Export to Markdown."""
        md = "# Document Analysis Report\n\n"
        md += f"**Document:** {document_metadata.get('filename', 'Unknown')}\n"
        md += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        md += "---\n\n"

        if analysis_data.get('classification'):
            md += "## Classification\n\n"
            class_data = analysis_data['classification']
            md += f"- **Type:** {class_data.get('type', 'N/A')}\n"
            md += f"- **Confidence:** {class_data.get('confidence', 0):.1%}\n\n"

        if analysis_data.get('summary'):
            md += "## Summary\n\n"
            md += f"{analysis_data['summary']}\n\n"

        if analysis_data.get('entities'):
            md += "## Entities\n\n"
            for entity_type, values in analysis_data['entities'].items():
                if values:
                    md += f"### {entity_type.replace('_', ' ').title()}\n\n"
                    for value in values:
                        md += f"- {value}\n"
                    md += "\n"

        if analysis_data.get('key_insights'):
            md += "## Key Insights\n\n"
            for insight in analysis_data['key_insights']:
                md += f"- {insight}\n"
            md += "\n"

        return md


markdown_exporter = MarkdownExporter()