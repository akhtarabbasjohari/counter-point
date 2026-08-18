// CounterPoint API Client

const API_BASE = '/api';

async function request(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        ...(options.body && !(options.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || errorData.detail || `API request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const ApiClient = {
  checkHealth() {
    return request('/health/');
  },

  uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    return request('/upload/', {
      method: 'POST',
      body: formData,
    });
  },

  getActiveDocument() {
    return request('/documents/');
  },

  clearActiveDocument() {
    return request('/documents/', {
      method: 'DELETE',
    });
  },

  searchCompetitor(query, maxResults = 5) {
    return request('/search/', {
      method: 'POST',
      body: JSON.stringify({ query, max_results: maxResults }),
    });
  },

  queryMultiHop(query, executeWebSearch = true) {
    return request('/query/', {
      method: 'POST',
      body: JSON.stringify({ query, execute_web_search: executeWebSearch }),
    });
  },

  getAuditLogs() {
    return request('/logs/');
  },

  resetSession() {
    return request('/session/reset/', {
      method: 'POST',
    });
  },
};
