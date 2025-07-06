import request from 'supertest';
import { describe, it, expect } from 'vitest';
import app from '../src/index.js';

describe('GET /api/hello', () => {
  it('responds with hello message', async () => {
    const res = await request(app).get('/api/hello');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ message: 'Hello from API' });
  });
});
