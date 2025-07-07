import express from 'express';
import cors from 'cors';
import swaggerUi from 'swagger-ui-express';
import swaggerJsdoc from 'swagger-jsdoc';
import axios from 'axios';
import { readFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import yaml from 'js-yaml';

const app = express();
app.use(cors());

const swaggerSpec = swaggerJsdoc({
  definition: {
    openapi: '3.0.0',
    info: { title: 'Sopra Steria Audit API', version: '0.1.0' }
  },
  apis: ['./src/**/*.js']
});

app.use('/api/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

/**
 * @openapi
 * /api/hello:
 *   get:
 *     summary: Returns a friendly greeting
 *     responses:
 *       200:
 *         description: Greeting message
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 message:
 *                   type: string
 */
app.get('/api/hello', (_req, res) => {
  res.json({ message: 'Hello from API' });
});

/**
 * @openapi
 * /api/datasets:
 *   get:
 *     summary: List available datasets
 *     responses:
 *       200:
 *         description: Array of datasets
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 datasets:
 *                   type: array
 *                   items:
 *                     type: object
 */
app.get('/api/datasets', async (_req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/datasets');
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch datasets' });
  }
});

app.get('/api/datasets/:name', async (req, res) => {
  try {
    const { name } = req.params;
    const response = await axios.get(`http://localhost:8000/datasets/${name}`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch dataset' });
  }
});

/**
 * @openapi
 * /api/pages:
 *   get:
 *     summary: List available pages
 *     responses:
 *       200:
 *         description: Array of pages
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 pages:
 *                   type: array
 *                   items:
 *                     type: object
 */
app.get('/api/pages', async (_req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/datasets/pages');
    res.json({ pages: response.data });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch pages' });
  }
});

/**
 * @openapi
 * /api/recommendations:
 *   get:
 *     summary: List content recommendations
 *     responses:
 *       200:
 *         description: Array of recommendations
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 recommendations:
 *                   type: array
 *                   items:
 *                     type: object
 */
app.get('/api/recommendations', async (_req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/datasets/recommendations');
    res.json({ recommendations: response.data });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch recommendations' });
  }
});

/**
 * @openapi
 * /api/opportunities:
 *   get:
 *     summary: List improvement opportunities
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *         description: Number of opportunities to return
 *     responses:
 *       200:
 *         description: Array of opportunities
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 opportunities:
 *                   type: array
 *                   items:
 *                     type: object
 */
app.get('/api/opportunities', async (req, res) => {
  const limit = req.query.limit || 20;
  try {
    const response = await axios.get(`http://localhost:8000/opportunities?limit=${limit}`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch opportunities' });
  }
});

app.get('/api/methodology', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url));
    const filePath = path.join(__dirname, '..', '..', 'audit_tool', 'config', 'methodology.yaml');
    const file = await readFile(filePath, 'utf8');
    const data = yaml.load(file);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to load methodology' });
  }
});

const port = process.env.PORT || 3000;

if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`API server listening on port ${port}`);
  });
}

export default app;
