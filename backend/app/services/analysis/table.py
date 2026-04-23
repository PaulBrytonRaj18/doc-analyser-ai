"""
Table Extraction Service - DocuLens AI v4.0
"""

from dataclasses import dataclass, field
from typing import Optional
from app.services.llm.llm_service import LLMService


@dataclass
class TableData:
    table_id: int
    headers: list[str]
    rows: list[list[str]]
    caption: Optional[str] = None


@dataclass
class TableExtractionResult:
    tables: list[TableData] = field(default_factory=list)


class TableExtractor:
    """Extracts tables from document text."""

    def __init__(self):
        self.llm = LLMService()

    def extract(self, text: str) -> TableExtractionResult:
        """Extract tables from document text."""
        prompt = f"""Extract any tables from the following document.
Format each table as:
TABLE <id>
HEADERS: <comma-separated column headers>
ROW: <tab-separated values>
...

Document text:
{text[:3000]}"""

        response = self.llm.generate(prompt)

        tables = []
        current_table = None

        try:
            for line in response.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue

                if line.startswith("TABLE "):
                    if current_table:
                        tables.append(current_table)
                    table_id = int(line.split()[1])
                    current_table = TableData(table_id=table_id, headers=[], rows=[])
                elif line.startswith("HEADERS:") and current_table:
                    headers = line.split(":", 1)[1].strip().split(",")
                    current_table.headers = [h.strip() for h in headers]
                elif line.startswith("ROW:") and current_table:
                    values = line.split(":", 1)[1].strip().split("\t")
                    current_table.rows.append(values)

            if current_table:
                tables.append(current_table)

        except Exception:
            pass

        return TableExtractionResult(tables=tables)