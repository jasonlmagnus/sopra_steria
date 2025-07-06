import request from 'supertest';
import { describe, it, expect } from 'vitest';
import app from '../src/index.js';

describe('GET /api/datasets', () => {
  it('returns empty datasets array', async () => {
    const res = await request(app).get('/api/datasets');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ datasets: [] });
  });
});

describe('GET /api/pages', () => {
  it('returns empty pages array', async () => {
    const res = await request(app).get('/api/pages');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ pages: [] });
  });
});

describe('GET /api/recommendations', () => {
  it('returns empty recommendations array', async () => {
    const res = await request(app).get('/api/recommendations');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ recommendations: [] });
  });
});

describe('GET /api/docs', () => {
  it('serves Swagger UI', async () => {
    const res = await request(app).get('/api/docs/');
    expect(res.status).toBe(200);
    expect(res.text).toContain('Swagger UI');
  });
});
