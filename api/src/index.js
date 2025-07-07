import express from 'express';
import cors from 'cors';
import swaggerUi from 'swagger-ui-express';
import swaggerJsdoc from 'swagger-jsdoc';
import axios from 'axios';
import { readFile, readdir } from 'fs/promises';
import fs from 'fs';
import csv from 'csv-parser';
import { createMarkdownObjectTable } from 'parse-markdown-table';
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

/**
 * @openapi
 * /api/summary:
 *   get:
 *     summary: Executive summary metrics
 *     responses:
 *       200:
 *         description: Summary object
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 */
app.get('/api/summary', async (_req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/executive-summary');
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch executive summary' });
  }
});

/**
 * @openapi
 * /api/tier-metrics:
 *   get:
 *     summary: Tier performance metrics
 *     responses:
 *       200:
 *         description: Array of tier metrics
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 */
app.get('/api/tier-metrics', async (_req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/tier-metrics');
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch tier metrics' });
  }
});

/**
 * @openapi
 * /api/persona-comparison:
 *   get:
 *     summary: Persona comparison metrics
 *     responses:
 *       200:
 *         description: Array of persona metrics
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 */
app.get('/api/persona-comparison', async (_req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/persona-comparison');
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch persona comparison data' });
  }
});

/**
 * @openapi
 * /api/full-recommendations:
 *   get:
 *     summary: Full list of recommendations
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
app.get('/api/full-recommendations', async (_req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/full-recommendations');
    res.json({ recommendations: response.data });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch recommendations list' });
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

app.get('/api/reports', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const dir = path.join(__dirname, '..', '..', 'html_reports')
    const files = await readdir(dir)
    const reports = files.filter((f) => f.endsWith('.html'))
    res.json({ reports })
  } catch (err) {
    res.status(500).json({ error: 'Failed to list reports' })
  }
})

app.get('/api/reports/:name', async (req, res) => {
  try {
    const { name } = req.params
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.join(__dirname, '..', '..', 'html_reports', name)
    const file = await readFile(filePath, 'utf8')
    res.setHeader('Content-Type', 'text/html')
    res.send(file)
  } catch (err) {
    res.status(404).json({ error: 'Report not found' })
  }
})

app.get('/api/personas', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const dir = path.join(__dirname, '..', '..', 'audit_inputs', 'personas')
    const files = await readdir(dir)
    const personas = files.filter((f) => f.endsWith('.md')).map((f) => f.replace('.md', ''))
    res.json({ personas })
  } catch (err) {
    res.status(500).json({ error: 'Failed to list personas' })
  }
})

app.get('/api/personas/:name', async (req, res) => {
  try {
    const { name } = req.params
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.join(__dirname, '..', '..', 'audit_inputs', 'personas', `${name}.md`)
    const content = await readFile(filePath, 'utf8')
    res.json({ content })
  } catch (err) {
    res.status(404).json({ error: 'Persona not found' })
  }
})

app.get('/api/social-media', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.join(
      __dirname,
      '..',
      '..',
      'audit_inputs',
      'social_media',
      'archive',
      'sm_dashboard_data_enhanced.md'
    )
    const markdown = await readFile(filePath, 'utf8')
    const table = await createMarkdownObjectTable(markdown)
    const rows = []
    for await (const row of table) {
      rows.push(row)
    }
    res.json({ data: rows })
  } catch (err) {
    console.error(err)
    res.status(500).json({ error: 'Failed to load social media data' })
  }
})

app.get('/api/brand-hygiene', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.join(__dirname, '..', '..', 'audit_data', 'unified_audit_data.csv')
    const results = {}
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => {
        const desc = row.descriptor
        if (desc) {
          results[desc] = (results[desc] || 0) + 1
        }
      })
      .on('end', () => {
        res.json(results)
      })
      .on('error', () => {
        res.status(500).json({ error: 'Failed to parse CSV' })
      })
  } catch (err) {
    res.status(500).json({ error: 'Failed to load brand hygiene data' })
  }
})

app.post('/api/run-audit', express.json(), async (req, res) => {
  const { url } = req.body || {}
  if (!url) {
    return res.status(400).json({ error: 'URL required' })
  }
  // Placeholder implementation
  res.json({ message: `Audit queued for ${url}` })
})

app.get('/api/implementation-tracking', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.join(__dirname, '..', 'data', 'implementation_tracking.json')
    const file = await readFile(filePath, 'utf8')
    res.json(JSON.parse(file))
  } catch (err) {
    res.status(500).json({ error: 'Failed to load implementation data' })
  }
})

const port = process.env.PORT || 3000;

if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`API server listening on port ${port}`);
  });
}

export default app;
