import request from 'supertest';
import { describe, it, expect, vi } from 'vitest';
import app from '../src/index.js';
import axios from 'axios';
import * as fs from 'fs/promises';
vi.mock('fs/promises', () => ({
  readFile: vi.fn(() => Promise.resolve('calculation:\n  formula: TEST')),
  readdir: vi.fn(() => Promise.resolve(['report1.html']))
}));

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

describe('GET /api/opportunities', () => {
  it('proxies opportunities from FastAPI', async () => {
    vi.spyOn(axios, 'get').mockResolvedValue({ data: { opportunities: [{ id: 1 }] } });
    const res = await request(app).get('/api/opportunities');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ opportunities: [{ id: 1 }] });
    vi.restoreAllMocks();
  });
});

describe('GET /api/summary', () => {
  it('proxies summary from FastAPI', async () => {
    vi.spyOn(axios, 'get').mockResolvedValue({ data: { brand_health: { raw_score: 8.2 } } });
    const res = await request(app).get('/api/summary');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ brand_health: { raw_score: 8.2 } });
    vi.restoreAllMocks();
  });
});

describe('GET /api/methodology', () => {
  it('returns methodology yaml as json', async () => {
    const res = await request(app).get('/api/methodology');
    expect(res.status).toBe(200);
    expect(res.body.calculation.formula).toBe('TEST');
  });
});

describe('GET /api/reports', () => {
  it('lists report files', async () => {
    const res = await request(app).get('/api/reports');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ reports: ['report1.html'] });
  });
});

describe('GET /api/reports/:name', () => {
  it('returns report content', async () => {
    const res = await request(app).get('/api/reports/report1.html');
    expect(res.status).toBe(200);
    expect(res.text).toContain('formula: TEST');
  });
});

describe('GET /api/docs', () => {
  it('serves Swagger UI', async () => {
    const res = await request(app).get('/api/docs/');
    expect(res.status).toBe(200);
    expect(res.text).toContain('Swagger UI');
  });
});
