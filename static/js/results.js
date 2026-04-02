/**
 * results.js — Render all analysis result cards
 */

const Results = (() => {
  function render(data) {
    renderMeta(data);
    renderDocType(data.document_type);
    renderSummary(data.summary);
    renderSentiment(data.sentiment);
    renderEntities(data.entities);
    renderPipeline(data.processing_steps);

    // Show results, hide empty state
    document.getElementById('emptyState').style.display = 'none';
    const container = document.getElementById('resultsContainer');
    container.style.display = 'block';
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function renderMeta(data) {
    const typeMap = { pdf: '📕 PDF', docx: '📘 DOCX', image: '🖼️ Image' };
    const pills = document.getElementById('metaPills');
    pills.innerHTML = `
      <span class="meta-pill highlight">${typeMap[data.file_type] || data.file_type}</span>
      <span class="meta-pill">${(data.word_count || 0).toLocaleString()} words</span>
      <span class="meta-pill">${(data.processing_time_ms || 0).toFixed(0)}ms</span>
    `;
  }

  function renderDocType(docType) {
    const icons = {
      'Invoice': '🧾', 'Resume': '👤', 'Legal': '⚖️',
      'Research Paper': '📚', 'Complaint': '📢', 'Report': '📊',
      'Letter': '✉️', 'Contract': '📝', 'Other': '📄',
    };
    const badge = document.getElementById('doctypeBadge');
    badge.textContent = `${icons[docType] || '📄'} ${docType}`;
  }

  function renderSummary(summary) {
    // TL;DR
    const tldr = document.getElementById('tldrBox');
    tldr.textContent = summary?.tldr || 'No summary available.';

    // Bullet points
    const list = document.getElementById('bulletList');
    list.innerHTML = '';
    const bullets = summary?.bullets || [];
    bullets.forEach(b => {
      const li = document.createElement('li');
      li.textContent = b;
      list.appendChild(li);
    });
  }

  function renderSentiment(sentiment) {
    const container = document.getElementById('sentimentDisplay');
    const label = sentiment?.label || 'neutral';
    const confidence = sentiment?.confidence ?? 50;
    const reason = sentiment?.reason || '';

    const emojiMap = { positive: '😊', negative: '😟', neutral: '😐' };

    container.innerHTML = `
      <div class="sentiment-emoji">${emojiMap[label] || '😐'}</div>
      <div class="sentiment-label ${label}">${label.charAt(0).toUpperCase() + label.slice(1)}</div>
      <div class="confidence-wrap">
        <div class="confidence-track">
          <div class="confidence-fill ${label}" id="confidenceFill" style="width:0%"></div>
        </div>
        <div class="confidence-text">Confidence: ${confidence}%</div>
      </div>
      <div class="sentiment-reason">${escHtml(reason)}</div>
    `;

    // Animate the bar
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        document.getElementById('confidenceFill').style.width = confidence + '%';
      });
    });
  }

  function renderEntities(entities) {
    const groups = [
      { key: 'people', label: 'People', cls: 'people' },
      { key: 'organizations', label: 'Organizations', cls: 'organizations' },
      { key: 'dates', label: 'Dates', cls: 'dates' },
      { key: 'amounts', label: 'Amounts', cls: 'amounts' },
    ];

    const container = document.getElementById('entityGroups');
    container.innerHTML = '';
    let hasAny = false;

    groups.forEach(g => {
      const items = entities?.[g.key] || [];
      if (items.length === 0) return;
      hasAny = true;

      const div = document.createElement('div');
      div.innerHTML = `
        <div class="entity-group-label">${g.label}</div>
        <div class="entity-tags">
          ${items.map(t => `<span class="entity-tag ${g.cls}">${escHtml(t)}</span>`).join('')}
        </div>
      `;
      container.appendChild(div);
    });

    if (!hasAny) {
      container.innerHTML = '<div class="empty-entity">No entities detected in this document.</div>';
    }
  }

  function renderPipeline(steps) {
    const container = document.getElementById('pipelineSteps');
    const labelMap = {
      'uploaded': '📤 Uploaded',
      'ocr_complete': '🔍 OCR Complete',
      'text_extracted': '📝 Text Extracted',
      'analysis_complete': '✅ Analysis Complete',
    };

    container.innerHTML = '';
    (steps || []).forEach((step, i) => {
      if (i > 0) {
        const arrow = document.createElement('span');
        arrow.className = 'pipeline-arrow';
        arrow.textContent = '→';
        container.appendChild(arrow);
      }
      const el = document.createElement('span');
      el.className = 'pipeline-step done';
      el.innerHTML = `<span class="pipeline-step-dot"></span>${labelMap[step] || step}`;
      container.appendChild(el);
    });
  }

  function hide() {
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('emptyState').style.display = 'flex';
  }

  function escHtml(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  return { render, hide };
})();
