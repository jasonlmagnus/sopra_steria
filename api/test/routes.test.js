import request from 'supertest';
import { describe, it, expect, vi } from 'vitest';
import app from '../src/index.js';
import axios from 'axios';

describe('GET /api/datasets', () => {
  it('proxies dataset list from FastAPI', async () => {
    vi.spyOn(axios, 'get').mockResolvedValue({ data: { datasets: ['pages'] } });
    const res = await request(app).get('/api/datasets');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ datasets: ['pages'] });
    vi.restoreAllMocks();
  });
});

describe('GET /api/pages', () => {
  it('proxies pages from FastAPI', async () => {
    vi.spyOn(axios, 'get').mockResolvedValue({ data: [{ id: 1 }] });
    const res = await request(app).get('/api/pages');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ pages: [{ id: 1 }] });
    vi.restoreAllMocks();
  });
});

describe('GET /api/recommendations', () => {
  it('proxies recommendations from FastAPI', async () => {
    vi.spyOn(axios, 'get').mockResolvedValue({ data: [{ id: 1 }] });
    const res = await request(app).get('/api/recommendations');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ recommendations: [{ id: 1 }] });
    vi.restoreAllMocks();
  });
});

describe('GET /api/docs', () => {
  it('serves Swagger UI', async () => {
    const res = await request(app).get('/api/docs/');
    expect(res.status).toBe(200);
    expect(res.text).toContain('Swagger UI');
  });
});
