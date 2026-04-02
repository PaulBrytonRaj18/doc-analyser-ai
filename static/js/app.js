/**
 * app.js — Main application orchestrator
 * Initializes modules, coordinates upload → analyze → render flow.
 */

(function () {
  'use strict';

  const analyzeBtn = document.getElementById('analyzeBtn');
  const timeline = document.getElementById('timeline');
  const timelineSteps = document.getElementById('timelineSteps');

  // Initialize upload module
  Upload.init((files) => {
    analyzeBtn.disabled = files.length === 0;
    if (files.length === 0) {
      Results.hide();
    }
  });

  // Wire up analyze button
  analyzeBtn.addEventListener('click', handleAnalyze);

  // Wire up export buttons
  document.getElementById('exportJsonBtn').addEventListener('click', () => Export.downloadJSON());
  document.getElementById('exportSummaryBtn').addEventListener('click', () => Export.downloadSummary());

  async function handleAnalyze() {
    const files = Upload.getFiles();
    if (files.length === 0) return;

    setLoading(true);
    showTimeline(['Uploading...']);

    try {
      let result;

      if (files.length === 1) {
        updateTimeline(['Uploading...', 'Extracting text...']);
        result = await API.analyzeFile(files[0]);
        updateTimeline(['Uploaded ✓', 'Text extracted ✓', 'AI analysis complete ✓']);
      } else {
        updateTimeline(['Uploading batch...', 'Processing files...']);
        const batch = await API.analyzeBatch(files);

        if (batch.errors && batch.errors.length > 0) {
          const errorMsgs = batch.errors.map(e => `${e.filename}: ${e.error}`).join('\n');
          Upload.showError(`Some files failed:\n${errorMsgs}`);
        }

        if (batch.results && batch.results.length > 0) {
          result = batch.results[0]; // Show first result
          updateTimeline(['Batch uploaded ✓', `${batch.results.length}/${batch.total} processed ✓`]);
        } else {
          throw new Error('No files were successfully processed.');
        }
      }

      // Store result for export
      Export.setResult(result);

      // Render
      Results.render(result);

    } catch (err) {
      Upload.showError(err.message || 'Analysis failed. Please try again.');
      Results.hide();
    } finally {
      setLoading(false);
    }
  }

  function setLoading(isLoading) {
    analyzeBtn.disabled = isLoading;
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoading = analyzeBtn.querySelector('.btn-loading');

    if (isLoading) {
      btnText.style.display = 'none';
      btnLoading.style.display = 'flex';
    } else {
      btnText.style.display = 'flex';
      btnLoading.style.display = 'none';
    }
  }

  function showTimeline(steps) {
    timeline.style.display = 'block';
    updateTimeline(steps);
  }

  function updateTimeline(steps) {
    timelineSteps.innerHTML = '';
    steps.forEach((label, i) => {
      const isDone = label.includes('✓');
      const isLast = i === steps.length - 1;
      const step = document.createElement('div');
      step.className = 'timeline-step';
      step.innerHTML = `
        <span class="timeline-dot ${isDone ? 'active' : (isLast ? 'processing' : '')}"></span>
        <span class="timeline-label ${isDone ? 'active' : ''}">${label}</span>
      `;
      timelineSteps.appendChild(step);
    });
  }
})();
