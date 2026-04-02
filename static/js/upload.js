/**
 * upload.js — Drag & drop, multi-file management, validation
 */

const Upload = (() => {
  let selectedFiles = [];
  let onChangeCallback = null;

  const FILE_ICONS = {
    pdf: '📕', docx: '📘', doc: '📘',
    png: '🖼️', jpg: '🖼️', jpeg: '🖼️',
    tiff: '🖼️', tif: '🖼️', bmp: '🖼️', webp: '🖼️',
  };

  const ALLOWED_EXTENSIONS = new Set(Object.keys(FILE_ICONS));
  const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

  function init(onChange) {
    onChangeCallback = onChange;
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');

    // Click to browse
    dropZone.addEventListener('click', () => fileInput.click());

    // Drag & drop
    dropZone.addEventListener('dragover', e => {
      e.preventDefault();
      dropZone.classList.add('dragging');
    });
    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('dragging');
    });
    dropZone.addEventListener('drop', e => {
      e.preventDefault();
      dropZone.classList.remove('dragging');
      const files = Array.from(e.dataTransfer.files);
      addFiles(files);
    });

    // File input change
    fileInput.addEventListener('change', e => {
      const files = Array.from(e.target.files);
      addFiles(files);
      fileInput.value = '';
    });
  }

  function addFiles(files) {
    for (const file of files) {
      const ext = file.name.split('.').pop().toLowerCase();
      if (!ALLOWED_EXTENSIONS.has(ext)) {
        showError(`"${file.name}" is not a supported format.`);
        continue;
      }
      if (file.size > MAX_FILE_SIZE) {
        showError(`"${file.name}" exceeds the 50MB limit.`);
        continue;
      }
      // Avoid duplicates
      if (selectedFiles.some(f => f.name === file.name && f.size === file.size)) continue;
      selectedFiles.push(file);
    }
    renderFileList();
    if (onChangeCallback) onChangeCallback(selectedFiles);
  }

  function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderFileList();
    if (onChangeCallback) onChangeCallback(selectedFiles);
  }

  function clearAll() {
    selectedFiles = [];
    renderFileList();
    if (onChangeCallback) onChangeCallback(selectedFiles);
  }

  function getFiles() {
    return selectedFiles;
  }

  function renderFileList() {
    const container = document.getElementById('fileList');
    container.innerHTML = '';
    selectedFiles.forEach((file, i) => {
      const ext = file.name.split('.').pop().toLowerCase();
      const icon = FILE_ICONS[ext] || '📄';
      const item = document.createElement('div');
      item.className = 'file-item';
      item.innerHTML = `
        <span class="file-item-icon">${icon}</span>
        <div class="file-item-details">
          <div class="file-item-name">${escHtml(file.name)}</div>
          <div class="file-item-size">${formatBytes(file.size)}</div>
        </div>
        <button class="file-item-remove" data-index="${i}" title="Remove">✕</button>
      `;
      item.querySelector('.file-item-remove').addEventListener('click', (e) => {
        e.stopPropagation();
        removeFile(i);
      });
      container.appendChild(item);
    });
  }

  function showError(msg) {
    const box = document.getElementById('errorBox');
    box.textContent = msg;
    box.style.display = 'block';
    setTimeout(() => { box.style.display = 'none'; }, 5000);
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(2) + ' MB';
  }

  function escHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  return { init, getFiles, clearAll, showError };
})();
