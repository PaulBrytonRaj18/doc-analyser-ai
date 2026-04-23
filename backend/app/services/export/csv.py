"""
CSV Exporter - DocuLens AI v4.0
"""

import csv
import io
from typing import Dict, Any, List


class CSVExporter:
    """Export data to CSV format."""

    def export_entities(
        self,
        entities: Dict[str, List[str]],
    ) -> bytes:
        """Export entities to CSV."""
        output = io.StringIO()
        
        writer = csv.writer(output)
        writer.writerow(['Type', 'Value'])
        
        for entity_type, values in entities.items():
            for value in values:
                writer.writerow([entity_type, value])

        return output.getvalue().encode('utf-8')

    def export_table(
        self,
        table_data: Dict[str, Any],
    ) -> bytes:
        """Export table to CSV."""
        output = io.StringIO()
        
        writer = csv.writer(output)
        
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)

        return output.getvalue().encode('utf-8')


csv_exporter = CSVExporter()