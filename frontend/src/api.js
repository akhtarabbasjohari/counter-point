// CounterPoint API Client with resilient host fallback

function getInitialBase() {
  try {
    if (typeof localStorage !== 'undefined' && localStorage && typeof localStorage.getItem === 'function') {
      return localStorage.getItem('CP_API_BASE') || '/api';
    }
  } catch (e) {
    // Fallback if localStorage unavailable
  }
  return '/api';
}

let detectedBase = getInitialBase();

function getApiBases() {
  let currentHost = 'localhost';
  try {
    if (typeof window !== 'undefined' && window.location) {
      currentHost = window.location.hostname || 'localhost';
    }
  } catch (e) {}

  const candidateBases = [
    '/api',
    `http://${currentHost}:8000/api`,
    'http://127.0.0.1:8000/api',
    'http://localhost:8000/api'
  ];
  return Array.from(new Set(candidateBases));
}

async function request(endpoint, options = {}) {
  const basesToTry = Array.from(new Set([detectedBase, ...getApiBases()]));
  let lastError = null;

  for (const base of basesToTry) {
    const cleanBase = base.replace(/\/$/, '');
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${cleanBase}${cleanEndpoint}`;

    try {
      const response = await fetch(url, {
        headers: {
          ...(options.body && !(options.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}),
          ...options.headers,
        },
        ...options,
      });

      if (response.ok) {
        detectedBase = base;
        try {
          if (typeof localStorage !== 'undefined' && localStorage && typeof localStorage.setItem === 'function') {
            localStorage.setItem('CP_API_BASE', base);
          }
        } catch (e) {
          // Ignore storage restriction
        }
        return await response.json();
      }

      // If relative /api returned 404 (e.g. dev server without proxy), try explicit backend host
      if (response.status === 404 && base === '/api' && basesToTry.length > 1) {
        continue;
      }

      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || errorData.detail || `API request failed with status ${response.status}`);
    } catch (err) {
      lastError = err;
      if (err.name === 'TypeError' || err.message.includes('Failed to fetch')) {
        continue;
      }
      throw err;
    }
  }

  throw lastError || new Error(`API request failed on all endpoint candidates.`);
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

  querySynthesis(query, executeWebSearch = true) {
    return request('/synthesis/', {
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
