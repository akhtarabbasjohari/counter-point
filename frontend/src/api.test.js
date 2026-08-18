import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ApiClient } from './api.js';

describe('CounterPoint ApiClient Test Suite (Vitest)', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('checkHealth calls GET /api/health/ correctly', async () => {
    const mockResponse = { status: 'ok', app: 'counterpoint' };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await ApiClient.checkHealth();

    expect(fetch).toHaveBeenCalledWith('/api/health/', expect.objectContaining({
      headers: expect.any(Object),
    }));
    expect(result).toEqual(mockResponse);
  });

  it('uploadDocument sends FormData via POST to /api/upload/', async () => {
    const mockFile = new File(['strategy content'], 'strategy.txt', { type: 'text/plain' });
    const mockResult = { message: 'Document uploaded', document: { file_name: 'strategy.txt' } };
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResult,
    });

    const result = await ApiClient.uploadDocument(mockFile);

    expect(fetch).toHaveBeenCalledWith('/api/upload/', expect.objectContaining({
      method: 'POST',
      body: expect.any(FormData),
    }));
    expect(result).toEqual(mockResult);
  });

  it('getActiveDocument calls GET /api/documents/', async () => {
    const mockDoc = { active_document: { file_name: 'positioning.pdf' } };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDoc,
    });

    const result = await ApiClient.getActiveDocument();

    expect(fetch).toHaveBeenCalledWith('/api/documents/', expect.anything());
    expect(result).toEqual(mockDoc);
  });

  it('clearActiveDocument calls DELETE /api/documents/', async () => {
    const mockResponse = { message: 'Document cleared' };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await ApiClient.clearActiveDocument();

    expect(fetch).toHaveBeenCalledWith('/api/documents/', expect.objectContaining({
      method: 'DELETE',
    }));
    expect(result).toEqual(mockResponse);
  });

  it('searchCompetitor formats query and max_results as JSON in POST /api/search/', async () => {
    const mockSearchResults = { query: 'Notion', results: [{ title: 'Notion Overview' }] };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSearchResults,
    });

    const result = await ApiClient.searchCompetitor('Notion', 5);

    expect(fetch).toHaveBeenCalledWith('/api/search/', expect.objectContaining({
      method: 'POST',
      headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ query: 'Notion', max_results: 5 }),
    }));
    expect(result).toEqual(mockSearchResults);
  });

  it('queryMultiHop sends query and execute_web_search to POST /api/query/', async () => {
    const mockSynthesis = { synthesis: 'Strategic report', model_used: 'Groq' };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSynthesis,
    });

    const result = await ApiClient.queryMultiHop('Compare Notion vs CounterPoint', true);

    expect(fetch).toHaveBeenCalledWith('/api/query/', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ query: 'Compare Notion vs CounterPoint', execute_web_search: true }),
    }));
    expect(result).toEqual(mockSynthesis);
  });

  it('getAuditLogs calls GET /api/logs/', async () => {
    const mockLogs = { log_count: 2, logs: [{ tool_name: 'web_search' }] };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockLogs,
    });

    const result = await ApiClient.getAuditLogs();

    expect(fetch).toHaveBeenCalledWith('/api/logs/', expect.anything());
    expect(result).toEqual(mockLogs);
  });

  it('resetSession calls POST /api/session/reset/', async () => {
    const mockRes = { message: 'Session reset successfully' };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockRes,
    });

    const result = await ApiClient.resetSession();

    expect(fetch).toHaveBeenCalledWith('/api/session/reset/', expect.objectContaining({
      method: 'POST',
    }));
    expect(result).toEqual(mockRes);
  });

  it('throws descriptive error on non-200 HTTP response', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ error: 'Invalid file format uploaded' }),
    });

    await expect(ApiClient.uploadDocument(new File([], 'bad.exe'))).rejects.toThrow('Invalid file format uploaded');
  });

  it('falls back to default HTTP status error message if no JSON error field is returned', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => { throw new Error('Invalid JSON'); },
    });

    await expect(ApiClient.checkHealth()).rejects.toThrow('API request failed with status 500');
  });
});
