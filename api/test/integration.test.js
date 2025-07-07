import request from 'supertest';
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import app from '../src/index.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

let fastapi;

beforeAll(async () => {
  fastapi = spawn('python3', ['-m', 'fastapi_service.server'], {
    cwd: path.join(__dirname, '..', '..'),
    stdio: 'ignore'
  });

  // wait briefly for the FastAPI server to start
  await new Promise((res) => setTimeout(res, 3000));
});

afterAll(() => {
  if (fastapi) {
    fastapi.kill();
  }
});

describe('Integration Express->FastAPI', () => {
  it('proxies dataset list', async () => {
    const res = await request(app).get('/api/datasets');
    expect(res.status).toBe(200);
    expect(res.body.datasets).toContain('master');
  });

  it('serves methodology data', async () => {
    const res = await request(app).get('/api/methodology');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('calculation');
  });

  it('returns opportunities data', async () => {
    const res = await request(app).get('/api/opportunities');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('opportunities');
  });

  it('returns executive summary', async () => {
    const res = await request(app).get('/api/summary');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('brand_health');
  });

  it('returns tier metrics', async () => {
    const res = await request(app).get('/api/tier-metrics');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('returns persona comparison data', async () => {
    const res = await request(app).get('/api/persona-comparison');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('returns full recommendations list', async () => {
    const res = await request(app).get('/api/full-recommendations');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('length');
  });

  it('lists reports', async () => {
    const res = await request(app).get('/api/reports');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('reports');
  });
});
