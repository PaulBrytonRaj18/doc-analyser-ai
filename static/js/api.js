/**
 * api.js — API communication layer
 * Handles all backend requests with error handling.
 */

const API = {
  BASE_URL: '/api/v1',

  /**
   * Analyze a single file.
   * @param {File} file
   * @returns {Promise<Object>} analysis result
   */
  async analyzeFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const resp = await fetch(`${this.BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });

    const data = await resp.json();

    if (!resp.ok) {
      throw new Error(data.detail || data.message || `Server error: ${resp.status}`);
    }

    return data;
  },

  /**
   * Analyze multiple files in batch.
   * @param {File[]} files
   * @returns {Promise<Object>} { results, errors, total }
   */
  async analyzeBatch(files) {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));

    const resp = await fetch(`${this.BASE_URL}/analyze/batch`, {
      method: 'POST',
      body: formData,
    });

    const data = await resp.json();

    if (!resp.ok) {
      throw new Error(data.detail || data.message || `Server error: ${resp.status}`);
    }

    return data;
  },

  /**
   * Check backend health.
   * @returns {Promise<Object>}
   */
  async healthCheck() {
    const resp = await fetch(`${this.BASE_URL}/health`);
    return resp.json();
  },
};
