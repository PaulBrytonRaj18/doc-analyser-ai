/**
 * export.js — Download analysis results as JSON or markdown summary
 */

const Export = (() => {
  let lastResult = null;

  function setResult(data) {
    lastResult = data;
  }

  function getResult() {
    return lastResult;
  }

  function downloadJSON() {
    if (!lastResult) return;
    const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: 'application/json' });
    downloadBlob(blob, `${lastResult.filename || 'analysis'}_result.json`);
  }

  function downloadSummary() {
    if (!lastResult) return;
    const r = lastResult;
    const lines = [
      `# Document Analysis: ${r.filename}`,
      '',
      `**Document Type:** ${r.document_type}`,
      `**File Type:** ${(r.file_type || '').toUpperCase()} · **Words:** ${(r.word_count || 0).toLocaleString()}`,
      `**Processing Time:** ${(r.processing_time_ms || 0).toFixed(0)}ms`,
      '',
      '## Summary',
      '',
      `**TL;DR:** ${r.summary?.tldr || 'N/A'}`,
      '',
    ];

    (r.summary?.bullets || []).forEach(b => lines.push(`- ${b}`));

    lines.push('', '## Sentiment', '');
    lines.push(`**${(r.sentiment?.label || 'neutral').charAt(0).toUpperCase() + (r.sentiment?.label || 'neutral').slice(1)}** (confidence: ${r.sentiment?.confidence || 0}%)`);
    if (r.sentiment?.reason) lines.push(`_${r.sentiment.reason}_`);

    lines.push('', '## Entities', '');
    const entityLabels = { people: 'People', organizations: 'Organizations', dates: 'Dates', amounts: 'Amounts' };
    Object.entries(entityLabels).forEach(([key, label]) => {
      const items = r.entities?.[key] || [];
      if (items.length > 0) {
        lines.push(`**${label}:** ${items.join(', ')}`);
      }
    });

    const blob = new Blob([lines.join('\n')], { type: 'text/markdown' });
    downloadBlob(blob, `${r.filename || 'analysis'}_summary.md`);
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return { setResult, getResult, downloadJSON, downloadSummary };
})();
