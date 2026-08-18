import { ApiClient } from './api.js';

// DOM Element References
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const btnResetSession = document.getElementById('btn-reset-session');

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const docStatusBadge = document.getElementById('doc-status-badge');
const docActiveView = document.getElementById('doc-active-view');
const docFileName = document.getElementById('doc-file-name');
const docFileStats = document.getElementById('doc-file-stats');
const docPreviewText = document.getElementById('doc-preview-text');
const docIcon = document.getElementById('doc-icon');
const btnClearDoc = document.getElementById('btn-clear-doc');

const presetChips = document.getElementById('preset-chips');
const queryForm = document.getElementById('query-form');
const queryInput = document.getElementById('query-input');
const chkWebSearch = document.getElementById('chk-web-search');
const btnSubmit = document.getElementById('btn-submit');
const activeModelTag = document.getElementById('active-model-tag');

const auditLogList = document.getElementById('audit-log-list');
const logCountBadge = document.getElementById('log-count-badge');

const researchTimeline = document.getElementById('research-timeline');
const emptyState = document.getElementById('empty-state');

const logModal = document.getElementById('log-modal');
const modalClose = document.getElementById('modal-close');
const modalTitle = document.getElementById('modal-title');
const modalContent = document.getElementById('modal-content');

// State
let currentSessionLogs = [];

// Initialize Application
async function init() {
  bindEvents();
  await verifyBackendHealth();
  await fetchActiveDocument();
  await fetchAuditLogs();
}

// Health Check
async function verifyBackendHealth() {
  try {
    const health = await ApiClient.checkHealth();
    if (health.status === 'ok') {
      statusIndicator.querySelector('.status-dot').style.backgroundColor = 'var(--status-success)';
      statusText.textContent = 'Backend Active';
    }
  } catch (err) {
    statusIndicator.querySelector('.status-dot').style.backgroundColor = 'var(--status-error)';
    statusText.textContent = 'Backend Offline';
  }
}

// Active Document Synchronization
async function fetchActiveDocument() {
  try {
    const res = await ApiClient.getActiveDocument();
    if (res.active_document) {
      renderActiveDocument(res.active_document);
    } else {
      renderNoDocument();
    }
  } catch (err) {
    console.error("Failed to fetch document status:", err);
  }
}

function renderActiveDocument(doc) {
  dropzone.classList.add('hidden');
  docActiveView.classList.remove('hidden');
  docStatusBadge.textContent = 'Active Doc';
  docStatusBadge.classList.add('active');
  
  docFileName.textContent = doc.file_name;
  docFileStats.textContent = `${doc.word_count.toLocaleString()} words • ${Math.round(doc.file_size_bytes / 1024 * 10) / 10} KB`;
  docPreviewText.textContent = doc.preview || "No preview text available.";
  docIcon.textContent = doc.file_type ? doc.file_type.toUpperCase() : 'DOC';
}

function renderNoDocument() {
  dropzone.classList.remove('hidden');
  docActiveView.classList.add('hidden');
  docStatusBadge.textContent = 'No File Uploaded';
  docStatusBadge.classList.remove('active');
}

// File Upload Handlers
function bindEvents() {
  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });

  btnClearDoc.addEventListener('click', async () => {
    try {
      await ApiClient.clearActiveDocument();
      renderNoDocument();
      await fetchAuditLogs();
    } catch (err) {
      alert("Failed to clear document: " + err.message);
    }
  });

  // Quick Chips
  presetChips.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (chip) {
      queryInput.value = chip.dataset.query;
      queryInput.focus();
    }
  });

  // Query Submit Form
  queryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    await executeSynthesisQuery(query, chkWebSearch.checked);
  });

  // Reset Session Button
  btnResetSession.addEventListener('click', async () => {
    if (confirm("Reset active document context, chat timeline, and audit logs?")) {
      try {
        await ApiClient.resetSession();
        renderNoDocument();
        researchTimeline.innerHTML = '';
        researchTimeline.appendChild(emptyState);
        emptyState.classList.remove('hidden');
        await fetchAuditLogs();
      } catch (err) {
        alert("Failed to reset session: " + err.message);
      }
    }
  });

  // Mobile Sidebar Toggle
  const btnToggleSidebar = document.getElementById('btn-toggle-sidebar');
  const sidebarPanel = document.querySelector('.sidebar-panel');
  if (btnToggleSidebar && sidebarPanel) {
    btnToggleSidebar.addEventListener('click', () => {
      sidebarPanel.classList.toggle('collapsed');
    });
  }

  // Modal Close
  modalClose.addEventListener('click', () => logModal.classList.add('hidden'));
  logModal.addEventListener('click', (e) => {
    if (e.target === logModal) logModal.classList.add('hidden');
  });
}

// Upload Handling
async function handleFileUpload(file) {
  const validExts = ['.pdf', '.txt', '.md'];
  const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
  if (!validExts.includes(ext)) {
    alert("Invalid file format. Please upload a PDF (.pdf) or Text (.txt, .md) positioning file.");
    return;
  }

  try {
    const response = await ApiClient.uploadDocument(file);
    renderActiveDocument(response.document);
    await fetchAuditLogs();
  } catch (err) {
    alert("Upload failed: " + err.message);
  }
}

// Multi-Hop Synthesis Execution
async function executeSynthesisQuery(query, executeWebSearch) {
  // Set UI Loading State
  btnSubmit.disabled = true;
  btnSubmit.querySelector('span').textContent = 'Synthesizing...';
  
  if (!emptyState.classList.contains('hidden')) {
    emptyState.classList.add('hidden');
  }

  // Add temporary loading placeholder card
  const tempCard = document.createElement('div');
  tempCard.className = 'report-card';
  tempCard.innerHTML = `
    <div class="report-header">
      <h3 class="report-query-title">${escapeHtml(query)}</h3>
      <div class="report-meta">Synthesizing live web data & positioning context...</div>
    </div>
    <div class="report-body" style="color: var(--text-muted); font-style: italic;">
      Executing multi-hop reasoning pipeline across internal strategy docs and live market signals...
    </div>
  `;
  researchTimeline.prepend(tempCard);

  try {
    const response = await ApiClient.queryMultiHop(query, executeWebSearch);
    
    // Update active model tag if returned
    if (response.model_used) {
      activeModelTag.textContent = `Model: ${response.model_used}`;
    }

    // Replace temp card with completed report
    const reportCard = document.createElement('div');
    reportCard.className = 'report-card';
    reportCard.innerHTML = renderReportHTML(response);
    
    researchTimeline.replaceChild(reportCard, tempCard);
    queryInput.value = '';

    // Refresh live audit log list
    await fetchAuditLogs();
  } catch (err) {
    tempCard.querySelector('.report-body').innerHTML = `<p style="color: var(--status-error);">Synthesis failed: ${escapeHtml(err.message)}</p>`;
  } finally {
    btnSubmit.disabled = false;
    btnSubmit.querySelector('span').textContent = 'Synthesize';
  }
}

// Render HTML for Report Card
function renderReportHTML(data) {
  const formattedSynthesis = parseMarkdownToHTML(data.synthesis);
  
  let sourcesHTML = '';
  if (data.web_sources && data.web_sources.length > 0) {
    sourcesHTML = `
      <div class="report-footer">
        <strong>Live Web Sources Consulted:</strong>
        <div class="source-list">
          ${data.web_sources.map(s => `
            <a href="${escapeHtml(s.url)}" target="_blank" rel="noopener" class="source-tag" title="${escapeHtml(s.snippet)}">
              ${escapeHtml(s.title || s.source)}
            </a>
          `).join('')}
        </div>
      </div>
    `;
  }

  const docTag = data.document_context_used && data.document_name
    ? `<span class="badge" style="background-color: var(--status-success-bg); color: var(--status-success);">Doc: ${escapeHtml(data.document_name)}</span>`
    : `<span class="badge">No Doc Context</span>`;

  return `
    <div class="report-header">
      <div>
        <h3 class="report-query-title">${escapeHtml(data.query)}</h3>
      </div>
      <div class="report-meta">
        ${docTag}
        <span>${data.execution_time_ms} ms</span>
      </div>
    </div>
    <div class="report-body">
      ${formattedSynthesis}
    </div>
    ${sourcesHTML}
  `;
}

// Markdown to HTML Formatter
function parseMarkdownToHTML(md) {
  if (!md) return '';
  let html = md;

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');

  // Bold & Italic
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // Bullet Lists
  html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
  html = html.replace(/<\/ul>\s*<ul>/g, '');

  // Paragraphs
  const paragraphs = html.split(/\n\n+/);
  return paragraphs.map(p => {
    if (p.startsWith('<h') || p.startsWith('<ul')) return p;
    return `<p>${p}</p>`;
  }).join('');
}

// Audit Log Fetching & UI Rendering
async function fetchAuditLogs() {
  try {
    const res = await ApiClient.getAuditLogs();
    currentSessionLogs = res.logs || [];
    renderAuditLogsList(currentSessionLogs);
  } catch (err) {
    console.error("Failed to fetch audit logs:", err);
  }
}

function renderAuditLogsList(logs) {
  logCountBadge.textContent = `${logs.length} calls`;

  if (!logs || logs.length === 0) {
    auditLogList.innerHTML = '<div class="empty-logs">No tool executions recorded yet.</div>';
    return;
  }

  auditLogList.innerHTML = logs.map((log, index) => {
    const timeFormatted = new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const statusColor = log.status === 'success' ? 'var(--status-success)' : 'var(--status-error)';
    
    return `
      <div class="log-item" data-index="${index}">
        <div>
          <div class="log-tool-name">${escapeHtml(log.tool_name)}</div>
          <div class="log-time">${timeFormatted} • <span style="color: ${statusColor}; font-weight:600;">${log.status}</span></div>
        </div>
        <div class="log-duration">${log.execution_time_ms} ms</div>
      </div>
    `;
  }).join('');

  // Bind click inspectors
  auditLogList.querySelectorAll('.log-item').forEach(item => {
    item.addEventListener('click', () => {
      const idx = item.dataset.index;
      showLogDetailModal(currentSessionLogs[idx]);
    });
  });
}

function showLogDetailModal(log) {
  if (!log) return;
  modalTitle.textContent = `Tool Audit: ${log.tool_name}`;
  modalContent.textContent = JSON.stringify(log, null, 2);
  logModal.classList.remove('hidden');
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Start application
document.addEventListener('DOMContentLoaded', init);
