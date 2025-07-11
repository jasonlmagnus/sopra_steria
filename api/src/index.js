import express from 'express';
import cors from 'cors';
import swaggerUi from 'swagger-ui-express';
import swaggerJsdoc from 'swagger-jsdoc';
import axios from 'axios';
import { readFile, readdir, stat } from 'fs/promises';
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

/**
 * @openapi
 * /api/datasets/master:
 *   get:
 *     summary: Get master dataset
 *     responses:
 *       200:
 *         description: Master dataset records
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 */
app.get('/api/datasets/master', async (_req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/datasets/master');
    res.json(response.data);
  } catch (err) {
    console.error('FastAPI master dataset error:', err.message);
    res.status(500).json({ error: 'Failed to fetch master dataset', details: err.message });
  }
});

/**
 * @openapi
 * /api/datasets/metadata:
 *   get:
 *     summary: Get datasets metadata
 *     responses:
 *       200:
 *         description: Datasets metadata with records, columns, memory info
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 datasets:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       name:
 *                         type: string
 *                       records:
 *                         type: integer
 *                       columns:
 *                         type: integer
 *                       memoryMB:
 *                         type: string
 */
app.get('/api/datasets/metadata', async (_req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/datasets/metadata');
    res.json(response.data);
  } catch (err) {
    console.error('FastAPI datasets metadata error:', err.message);
    res.status(500).json({ error: 'Failed to fetch datasets metadata', details: err.message });
  }
});

/**
 * @openapi
 * /api/datasets/{name}:
 *   get:
 *     summary: Get specific dataset
 *     parameters:
 *       - in: path
 *         name: name
 *         required: true
 *         schema:
 *           type: string
 *         description: Dataset name
 *     responses:
 *       200:
 *         description: Dataset records
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 type: object
 */
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

/**
 * @openapi
 * /api/strategic-assessment:
 *   get:
 *     summary: Strategic brand assessment metrics
 *     parameters:
 *       - in: query
 *         name: tier
 *         schema:
 *           type: string
 *         description: Filter by tier (e.g., "Tier 1 (Strategic)")
 *     responses:
 *       200:
 *         description: Strategic assessment object
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 distinctiveness:
 *                   type: object
 *                 resonance:
 *                   type: object
 *                 conversion:
 *                   type: object
 */
app.get('/api/strategic-assessment', async (req, res) => {
  try {
    const tier = req.query.tier;
    const url = tier ? `http://localhost:8000/strategic-assessment?tier=${encodeURIComponent(tier)}` : 'http://localhost:8000/strategic-assessment';
    const response = await axios.get(url);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch strategic assessment' });
  }
});

/**
 * @openapi
 * /api/success-stories:
 *   get:
 *     summary: Top performing success stories
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 5
 *         description: Number of success stories to return
 *       - in: query
 *         name: min_score
 *         schema:
 *           type: number
 *           default: 7.5
 *         description: Minimum score for success stories
 *     responses:
 *       200:
 *         description: Success stories object
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success_stories:
 *                   type: array
 *                   items:
 *                     type: object
 */
app.get('/api/success-stories', async (req, res) => {
  try {
    const limit = req.query.limit || 5;
    const min_score = req.query.min_score || 7.5;
    const response = await axios.get(`http://localhost:8000/success-stories?limit=${limit}&min_score=${min_score}`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch success stories' });
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

app.get('/api/persona-journeys', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const dir = path.join(__dirname, '..', '..', 'audit_inputs', 'persona_journeys')
    const files = await readdir(dir)
    const personas = files.filter((f) => f.endsWith('.md')).map((f) => f.replace('.md', ''))
    res.json({ personas })
  } catch (err) {
    res.status(500).json({ error: 'Failed to list persona journeys' })
  }
})

app.get('/api/persona-journeys/:name', async (req, res) => {
  try {
    const { name } = req.params
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.join(__dirname, '..', '..', 'audit_inputs', 'persona_journeys', `${name}.md`)
    const markdown = await readFile(filePath, 'utf8')
    const lines = markdown.split('\n').filter((l) => l.trim().startsWith('| **'))
    const steps = lines.map((l) => {
      const cells = l.split('|').slice(1, -1).map((c) => c.trim())
      return {
        step: cells[0],
        evaluation: cells[1],
        severity: cells[2],
        quickFix: cells[3]
      }
    })
    res.json({ steps })
  } catch (err) {
    res.status(404).json({ error: 'Persona journey not found' })
  }
})

app.get('/api/download/:name', async (req, res) => {
  try {
    const { name } = req.params
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.join(__dirname, '..', '..', 'audit_data', name)
    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'File not found' })
    }
    res.sendFile(filePath)
  } catch (err) {
    res.status(500).json({ error: 'Failed to download file' })
  }
})

app.get('/api/social-media', async (req, res) => {
  try {
    const queryParams = new URLSearchParams(req.query).toString()
    const url = `http://localhost:8000/api/social-media${queryParams ? '?' + queryParams : ''}`
    const response = await axios.get(url)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI social-media error:', err.message)
    res.status(500).json({ error: 'Failed to fetch social media data', details: err.message })
  }
})

app.get('/api/brand-hygiene', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.join(__dirname, '..', '..', 'audit_inputs', 'visual_brand', 'brand_audit_scores.csv')
    const results = []
    
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => {
        // Convert CSV row to structured data
        results.push({
          url: row.URL,
          page_type: row['Page Type'],
          logo_compliance: parseFloat(row['Logo Compliance']) || 0,
          color_palette: parseFloat(row['Color Palette']) || 0,
          typography: parseFloat(row['Typography']) || 0,
          layout_structure: parseFloat(row['Layout Structure']) || 0,
          image_quality: parseFloat(row['Image Quality']) || 0,
          brand_messaging: parseFloat(row['Brand Messaging']) || 0,
          gating_penalties: parseFloat(row['Gating Penalties']) || 0,
          final_score: parseFloat(row['Final Score']) || 0,
          key_violations: row['Key Violations'] || '',
          // Derived fields for analysis
          domain: row.URL ? row.URL.split('/')[2] : '',
          page_name: row.URL ? row.URL.split('/').pop() || 'Homepage' : '',
          tier_number: row['Page Type']?.includes('Tier 1') ? '1' : 
                      row['Page Type']?.includes('Tier 2') ? '2' : 
                      row['Page Type']?.includes('Tier 3') ? '3' : '0',
          tier_name: row['Page Type']?.includes(' - ') ? row['Page Type'].split(' - ')[1] : row['Page Type'] || 'Unknown',
          region: row.URL?.includes('.nl') ? 'Netherlands' : 
                 row.URL?.includes('.be') ? 'Belgium' : 
                 row.URL?.includes('.com') ? 'Global' : 'Other'
        })
      })
      .on('end', () => {
        res.json(results)
      })
      .on('error', (err) => {
        console.error('Error reading brand audit CSV:', err)
        res.status(500).json({ error: 'Failed to parse brand audit data' })
      })
  } catch (err) {
    console.error('Error loading brand audit data:', err)
    res.status(500).json({ error: 'Failed to load brand audit data' })
  }
})

/**
 * @openapi
 * /api/persona-insights:
 *   get:
 *     summary: Get persona-specific insights from audit data
 *     responses:
 *       200:
 *         description: Persona insights data
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 personas:
 *                   type: array
 *                   items:
 *                     type: object
 */
app.get('/api/persona-insights', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.join(__dirname, '..', '..', 'audit_data', 'unified_audit_data.csv')
    
    const personaData = {}
    
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => {
        const personaId = row.persona_id
        if (!personaId || personaId === 'persona_id') return // Skip header row
        
        if (!personaData[personaId]) {
          personaData[personaId] = {
            persona_id: personaId,
            pages: [],
            metrics: {
              total_pages: 0,
              avg_score: 0,
              critical_issues: 0,
              quick_wins: 0,
              success_stories: 0
            }
          }
        }
        
        // Add page data
        const pageId = row.page_id
        const existingPage = personaData[personaId].pages.find(p => p.page_id === pageId)
        
        if (!existingPage) {
          personaData[personaId].pages.push({
            page_id: pageId,
            url: row.url,
            url_slug: row.url_slug,
            tier: row.tier,
            tier_name: row.tier_name,
            criteria: [],
            avg_score: parseFloat(row.avg_score) || 0,
            sentiment: row.overall_sentiment,
            engagement: row.engagement_level,
            conversion: row.conversion_likelihood
          })
          personaData[personaId].metrics.total_pages++
        }
        
        // Add criterion data
        const page = personaData[personaId].pages.find(p => p.page_id === pageId)
        if (page) {
          page.criteria.push({
            criterion_id: row.criterion_id,
            criterion_code: row.criterion_code,
            raw_score: parseFloat(row.raw_score) || 0,
            final_score: parseFloat(row.final_score) || 0,
            descriptor: row.descriptor,
            evidence: row.evidence,
            effective_copy_examples: row.effective_copy_examples,
            ineffective_copy_examples: row.ineffective_copy_examples,
            quick_win_flag: row.quick_win_flag === 'True',
            critical_issue_flag: row.critical_issue_flag === 'True',
            success_flag: row.success_flag === 'True'
          })
        }
        
        // Update metrics
        if (row.critical_issue_flag === 'True') {
          personaData[personaId].metrics.critical_issues++
        }
        if (row.quick_win_flag === 'True') {
          personaData[personaId].metrics.quick_wins++
        }
        if (row.success_flag === 'True') {
          personaData[personaId].metrics.success_stories++
        }
      })
      .on('end', () => {
        // Calculate average scores
        Object.values(personaData).forEach(persona => {
          const totalScores = persona.pages.reduce((sum, page) => sum + page.avg_score, 0)
          persona.metrics.avg_score = persona.metrics.total_pages > 0 
            ? (totalScores / persona.metrics.total_pages).toFixed(1)
            : 0
        })
        
        res.json({ personas: Object.values(personaData) })
      })
      .on('error', (err) => {
        console.error('Error reading CSV:', err)
        res.status(500).json({ error: 'Failed to parse persona insights data' })
      })
  } catch (err) {
    console.error('Error loading persona insights:', err)
    res.status(500).json({ error: 'Failed to load persona insights data' })
  }
})

/**
 * @openapi
 * /api/gap-analysis:
 *   get:
 *     summary: List gap analysis findings
 *     responses:
 *       200:
 *         description: Array of gaps
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 items:
 *                   type: array
 *                   items:
 *                     type: string
 */
app.get('/api/gap-analysis', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const filePath = path.join(__dirname, '..', 'data', 'gap_analysis.json')
    const file = await readFile(filePath, 'utf8')
    res.json({ items: JSON.parse(file) })
  } catch (err) {
    res.status(500).json({ error: 'Failed to load gap analysis' })
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

/**
 * @openapi
 * /api/personas:
 *   get:
 *     summary: List available personas
 *     responses:
 *       200:
 *         description: Array of persona IDs
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 personas:
 *                   type: array
 *                   items:
 *                     type: string
 */
app.get('/api/personas', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const personasDir = path.join(__dirname, '..', '..', 'audit_inputs', 'personas')
    
    const files = await readdir(personasDir)
    const personaIds = files
      .filter(file => file.endsWith('.md'))
      .map(file => file.replace('.md', ''))
      .sort()
    
    res.json({ personas: personaIds })
  } catch (err) {
    console.error('Error loading personas:', err)
    res.status(500).json({ error: 'Failed to load personas' })
  }
})

/**
 * @openapi
 * /api/persona/{id}:
 *   get:
 *     summary: Get specific persona details
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Persona ID (e.g., P1, P2, etc.)
 *     responses:
 *       200:
 *         description: Persona details
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 id:
 *                   type: string
 *                 name:
 *                   type: string
 *                 content:
 *                   type: string
 *       404:
 *         description: Persona not found
 */
app.get('/api/persona/:id', async (req, res) => {
  try {
    const { id } = req.params
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const personaPath = path.join(__dirname, '..', '..', 'audit_inputs', 'personas', `${id}.md`)
    
    const content = await readFile(personaPath, 'utf8')
    
    // Extract persona name from content
    const lines = content.trim().split('\n')
    let name = id
    if (lines.length > 0) {
      const firstLine = lines[0].trim()
      if (firstLine.startsWith('Persona Brief:')) {
        name = firstLine.replace('Persona Brief:', '').trim()
      }
    }
    
    res.json({
      id,
      name,
      content
    })
  } catch (err) {
    if (err.code === 'ENOENT') {
      res.status(404).json({ error: 'Persona not found' })
    } else {
      console.error('Error loading persona:', err)
      res.status(500).json({ error: 'Failed to load persona' })
    }
  }
})

/**
 * @openapi
 * /api/html-reports:
 *   get:
 *     summary: List available HTML reports
 *     responses:
 *       200:
 *         description: Array of HTML reports
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 reports:
 *                   type: array
 *                   items:
 *                     type: object
 */
app.get('/api/html-reports', async (_req, res) => {
  try {
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const htmlReportsDir = path.join(__dirname, '..', '..', 'html_reports')
    
    const reports = await scanHtmlReports(htmlReportsDir)
    res.json({ reports })
  } catch (err) {
    console.error('Error scanning HTML reports:', err)
    res.status(500).json({ error: 'Failed to scan HTML reports' })
  }
})

/**
 * @openapi
 * /api/html-reports/{folder}/{file}:
 *   get:
 *     summary: Get HTML report content from folder
 *     parameters:
 *       - in: path
 *         name: folder
 *         required: true
 *         schema:
 *           type: string
 *         description: Report folder name
 *       - in: path
 *         name: file
 *         required: true
 *         schema:
 *           type: string
 *         description: Report file name
 *     responses:
 *       200:
 *         description: HTML report content
 *         content:
 *           text/html:
 *             schema:
 *               type: string
 *       404:
 *         description: Report not found
 * 
 * /api/html-reports/{file}:
 *   get:
 *     summary: Get HTML report content from root
 *     parameters:
 *       - in: path
 *         name: file
 *         required: true
 *         schema:
 *           type: string
 *         description: Report file name
 *     responses:
 *       200:
 *         description: HTML report content
 *         content:
 *           text/html:
 *             schema:
 *               type: string
 *       404:
 *         description: Report not found
 */
// Fixed route to handle nested paths properly
app.get('/api/html-reports/:folder/:file', async (req, res) => {
  try {
    const { folder, file } = req.params
    const reportPath = `${folder}/${file}`
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const fullPath = path.join(__dirname, '..', '..', 'html_reports', reportPath)
    
    // Security check - ensure path is within html_reports directory
    const resolvedPath = path.resolve(fullPath)
    const htmlReportsDir = path.resolve(path.join(__dirname, '..', '..', 'html_reports'))
    
    if (!resolvedPath.startsWith(htmlReportsDir)) {
      return res.status(403).json({ error: 'Access denied' })
    }
    
    const content = await readFile(fullPath, 'utf8')
    res.setHeader('Content-Type', 'text/html')
    res.send(content)
  } catch (err) {
    if (err.code === 'ENOENT') {
      res.status(404).json({ error: 'Report not found' })
    } else {
      console.error('Error loading HTML report:', err)
      res.status(500).json({ error: 'Failed to load HTML report' })
    }
  }
})

// Handle root level HTML files
app.get('/api/html-reports/:file', async (req, res) => {
  try {
    const { file } = req.params
    const __dirname = path.dirname(fileURLToPath(import.meta.url))
    const fullPath = path.join(__dirname, '..', '..', 'html_reports', file)
    
    // Security check - ensure path is within html_reports directory
    const resolvedPath = path.resolve(fullPath)
    const htmlReportsDir = path.resolve(path.join(__dirname, '..', '..', 'html_reports'))
    
    if (!resolvedPath.startsWith(htmlReportsDir)) {
      return res.status(403).json({ error: 'Access denied' })
    }
    
    const content = await readFile(fullPath, 'utf8')
    res.setHeader('Content-Type', 'text/html')
    res.send(content)
  } catch (err) {
    if (err.code === 'ENOENT') {
      res.status(404).json({ error: 'Report not found' })
    } else {
      console.error('Error loading HTML report:', err)
      res.status(500).json({ error: 'Failed to load HTML report' })
    }
  }
})

async function scanHtmlReports(htmlReportsDir) {
  const reports = []
  
  try {
    const items = await readdir(htmlReportsDir)
    
    for (const item of items) {
      const itemPath = path.join(htmlReportsDir, item)
      const stats = await stat(itemPath)
      
      if (stats.isFile() && item.endsWith('.html')) {
        // Root level HTML files
        const report = await createReportInfo(itemPath, item, htmlReportsDir)
        if (report) reports.push(report)
      } else if (stats.isDirectory()) {
        // Subdirectories with HTML files
        try {
          const subItems = await readdir(itemPath)
          for (const subItem of subItems) {
            if (subItem.endsWith('.html')) {
              const subItemPath = path.join(itemPath, subItem)
              const relativePath = path.join(item, subItem)
              const report = await createReportInfo(subItemPath, relativePath, htmlReportsDir)
              if (report) reports.push(report)
            }
          }
        } catch (err) {
          console.error(`Error reading subdirectory ${item}:`, err)
        }
      }
    }
  } catch (err) {
    console.error('Error scanning HTML reports directory:', err)
  }
  
  return reports
}

async function createReportInfo(filePath, relativePath, baseDir) {
  try {
    const stats = await stat(filePath)
    const fileName = path.basename(relativePath)
    
    // Determine persona name and report type
    let personaName = 'Unknown'
    let reportType = 'Report'
    let category = 'Other'
    
    if (relativePath.includes('Consolidated')) {
      personaName = 'Consolidated Brand Report'
      reportType = 'Consolidated Report'
      category = 'Executive'
    } else if (fileName === 'index.html') {
      personaName = 'Index/Root'
      reportType = 'Strategic Analysis'
      category = 'Executive'
    } else if (fileName.includes('brand_audit')) {
      personaName = 'Index/Root'
      reportType = 'Strategic Analysis'
      category = 'Executive'
    } else if (relativePath.includes('Technical_Influencer')) {
      personaName = 'The Technical Influencer'
      reportType = 'Persona Report'
      category = 'Persona'
    } else if (relativePath.includes('Cybersecurity_Decision_Maker')) {
      personaName = 'The Benelux Cybersecurity Decision Maker'
      reportType = 'Persona Report'
      category = 'Persona'
    } else if (relativePath.includes('Strategic_Business_Leader')) {
      personaName = 'The Benelux Strategic Business Leader (C-Suite Executive)'
      reportType = 'Persona Report'
      category = 'Persona'
    } else if (relativePath.includes('Transformation_Programme_Leader')) {
      personaName = 'The Benelux Transformation Programme Leader'
      reportType = 'Persona Report'
      category = 'Persona'
    } else if (relativePath.includes('Technology_Innovation_Leader')) {
      personaName = 'The BENELUX Technology Innovation Leader'
      reportType = 'Persona Report'
      category = 'Persona'
    }
    
    return {
      file_path: filePath,
      file_name: fileName,
      persona_name: personaName,
      report_type: reportType,
      category: category,
      size: `${(stats.size / 1024).toFixed(1)} KB`,
      modified: stats.mtime.toISOString().split('T')[0] + ' ' + stats.mtime.toTimeString().split(' ')[0],
      relative_path: relativePath.replace(/\\/g, '/')
    }
  } catch (err) {
    console.error(`Error creating report info for ${filePath}:`, err)
    return null
  }
}

/**
 * @openapi
 * /api/content-matrix:
 *   get:
 *     summary: Content matrix analysis with filtering
 *     parameters:
 *       - in: query
 *         name: persona
 *         schema:
 *           type: string
 *         description: Filter by persona
 *       - in: query
 *         name: tier
 *         schema:
 *           type: string
 *         description: Filter by content tier
 *       - in: query
 *         name: minScore
 *         schema:
 *           type: number
 *         description: Minimum score filter
 *       - in: query
 *         name: performanceLevel
 *         schema:
 *           type: string
 *         description: Filter by performance level
 *     responses:
 *       200:
 *         description: Content matrix data
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 */
app.get('/api/content-matrix', async (req, res) => {
  try {
    const queryParams = new URLSearchParams(req.query).toString()
    const url = `http://localhost:8000/content-matrix${queryParams ? '?' + queryParams : ''}`
    const response = await axios.get(url)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI content-matrix error:', err.message)
    res.status(500).json({ error: 'Failed to fetch content matrix', details: err.message })
  }
})

/**
 * @openapi
 * /api/opportunity-impact:
 *   get:
 *     summary: Opportunity impact analysis with filtering
 *     parameters:
 *       - in: query
 *         name: impactThreshold
 *         schema:
 *           type: number
 *         description: Impact threshold filter
 *       - in: query
 *         name: effortLevel
 *         schema:
 *           type: string
 *         description: Filter by effort level
 *       - in: query
 *         name: priorityLevel
 *         schema:
 *           type: string
 *         description: Filter by priority level
 *       - in: query
 *         name: contentTier
 *         schema:
 *           type: string
 *         description: Filter by content tier
 *       - in: query
 *         name: maxOpportunities
 *         schema:
 *           type: integer
 *         description: Maximum number of opportunities to return
 *     responses:
 *       200:
 *         description: Opportunity impact data
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 */
app.get('/api/opportunity-impact', async (req, res) => {
  try {
    const queryParams = new URLSearchParams(req.query).toString()
    const url = `http://localhost:8000/opportunity-impact${queryParams ? '?' + queryParams : ''}`
    const response = await axios.get(url)
    res.json(response.data)
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch opportunity impact' })
  }
})

/**
 * @openapi
 * /api/strategic-intelligence:
 *   get:
 *     summary: Business-focused strategic recommendations with ROI impact
 *     parameters:
 *       - in: query
 *         name: tier
 *         schema:
 *           type: string
 *         description: Filter by content tier (Tier 1, Tier 2, Tier 3)
 *       - in: query
 *         name: business_impact
 *         schema:
 *           type: string
 *         description: Filter by business impact level (High, Medium, Low)
 *       - in: query
 *         name: timeline
 *         schema:
 *           type: string
 *         description: Filter by implementation timeline (0-30, 30-90, 90+ days)
 *     responses:
 *       200:
 *         description: Strategic intelligence with business context
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 executiveSummary:
 *                   type: object
 *                 strategicThemes:
 *                   type: array
 *                 businessImpact:
 *                   type: object
 *                 recommendations:
 *                   type: array
 */
app.get('/api/strategic-intelligence', async (req, res) => {
  try {
    const queryParams = new URLSearchParams(req.query).toString()
    const url = `http://localhost:8000/strategic-intelligence${queryParams ? '?' + queryParams : ''}`
    const response = await axios.get(url)
    res.json(response.data)
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch strategic intelligence' })
  }
})

/**
 * @openapi
 * /api/success-library:
 *   get:
 *     summary: Success library with filtering and analysis
 *     parameters:
 *       - in: query
 *         name: persona
 *         schema:
 *           type: string
 *         description: Filter by persona
 *       - in: query
 *         name: tier
 *         schema:
 *           type: string
 *         description: Filter by content tier
 *       - in: query
 *         name: successThreshold
 *         schema:
 *           type: number
 *         description: Minimum success score threshold
 *       - in: query
 *         name: maxStories
 *         schema:
 *           type: integer
 *         description: Maximum number of success stories to return
 *       - in: query
 *         name: evidenceType
 *         schema:
 *           type: string
 *         description: Filter by evidence type
 *       - in: query
 *         name: searchTerm
 *         schema:
 *           type: string
 *         description: Search term for filtering success stories
 *     responses:
 *       200:
 *         description: Success library data
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 */
app.get('/api/success-library', async (req, res) => {
  try {
    const queryParams = new URLSearchParams(req.query).toString()
    const url = `http://localhost:8000/success-library${queryParams ? '?' + queryParams : ''}`
    const response = await axios.get(url)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI success-library error:', err.message)
    res.status(500).json({ error: 'Failed to fetch success library', details: err.message })
  }
})

// Additional proxy endpoints for FastAPI (only non-duplicates)
app.get('/api/persona-pages', async (req, res) => {
  try {
    const queryParams = new URLSearchParams(req.query).toString()
    const url = `http://localhost:8000/persona-pages${queryParams ? '?' + queryParams : ''}`
    const response = await axios.get(url)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI persona-pages error:', err.message)
    res.status(500).json({ error: 'Failed to fetch persona pages', details: err.message })
  }
})

app.get('/api/audit/status/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params
    const response = await axios.get(`http://localhost:8000/api/audit/status/${sessionId}`)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI audit status error:', err.message)
    res.status(500).json({ error: 'Failed to fetch audit status', details: err.message })
  }
})

app.get('/api/audit/processing-status/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params
    const response = await axios.get(`http://localhost:8000/api/audit/processing-status/${sessionId}`)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI audit processing status error:', err.message)
    res.status(500).json({ error: 'Failed to fetch audit processing status', details: err.message })
  }
})

app.get('/api/persona/:personaId/voice-analysis', async (req, res) => {
  try {
    const { personaId } = req.params
    const queryParams = new URLSearchParams(req.query).toString()
    const url = `http://localhost:8000/api/persona/${personaId}/voice-analysis${queryParams ? '?' + queryParams : ''}`
    const response = await axios.get(url)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI persona voice-analysis error:', err.message)
    res.status(500).json({ error: 'Failed to fetch persona voice analysis', details: err.message })
  }
})

// Missing POST endpoints for audit functionality
app.post('/api/audit/run', express.json(), async (req, res) => {
  try {
    const response = await axios.post('http://localhost:8000/api/audit/run', req.body)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI audit run error:', err.message)
    res.status(500).json({ error: 'Failed to run audit', details: err.message })
  }
})

app.post('/api/audit/stop/:sessionId', express.json(), async (req, res) => {
  try {
    const { sessionId } = req.params
    const response = await axios.post(`http://localhost:8000/api/audit/stop/${sessionId}`, req.body)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI audit stop error:', err.message)
    res.status(500).json({ error: 'Failed to stop audit', details: err.message })
  }
})

app.post('/api/audit/process', express.json(), async (req, res) => {
  try {
    const response = await axios.post('http://localhost:8000/api/audit/process', req.body)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI audit process error:', err.message)
    res.status(500).json({ error: 'Failed to process audit', details: err.message })
  }
})

app.post('/api/regenerate-reports', express.json(), async (req, res) => {
  try {
    const response = await axios.post('http://localhost:8000/api/regenerate-reports', req.body)
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI regenerate reports error:', err.message)
    res.status(500).json({ error: 'Failed to regenerate reports', details: err.message })
  }
})

app.get('/api/download-all-reports', async (req, res) => {
  try {
    const response = await axios.get('http://localhost:8000/api/download-all-reports')
    res.json(response.data)
  } catch (err) {
    console.error('FastAPI download all reports error:', err.message)
    res.status(500).json({ error: 'Failed to download all reports', details: err.message })
  }
})

/**
 * @openapi
 * /api/reports/custom:
 *   post:
 *     summary: Generate custom report
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               reportType:
 *                 type: string
 *               personas:
 *                 type: array
 *                 items:
 *                   type: string
 *               format:
 *                 type: string
 *     responses:
 *       200:
 *         description: Custom report generated successfully
 */
app.post('/api/reports/custom', async (req, res) => {
  try {
    const response = await axios.post('http://localhost:8000/reports/custom', req.body);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to generate custom report' });
  }
});

/**
 * @openapi
 * /api/reports/html:
 *   post:
 *     summary: Generate HTML reports
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               generationMode:
 *                 type: string
 *               personas:
 *                 type: array
 *                 items:
 *                   type: string
 *     responses:
 *       200:
 *         description: HTML reports generated successfully
 */
app.post('/api/reports/html', async (req, res) => {
  try {
    const response = await axios.post('http://localhost:8000/reports/html', req.body);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to generate HTML reports' });
  }
});

/**
 * @openapi
 * /api/export/{format}:
 *   post:
 *     summary: Export data in specified format
 *     parameters:
 *       - in: path
 *         name: format
 *         required: true
 *         schema:
 *           type: string
 *           enum: [csv, json, excel, parquet]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               filters:
 *                 type: object
 *               options:
 *                 type: object
 *     responses:
 *       200:
 *         description: Data exported successfully
 */
app.post('/api/export/:format', async (req, res) => {
  try {
    const response = await axios.post(`http://localhost:8000/export/${req.params.format}`, req.body);
    
    // Handle file downloads
    if (response.headers['content-disposition']) {
      res.set({
        'Content-Type': response.headers['content-type'],
        'Content-Disposition': response.headers['content-disposition']
      });
      res.send(response.data);
    } else {
      res.json(response.data);
    }
  } catch (err) {
    res.status(500).json({ error: 'Failed to export data' });
  }
});


const port = process.env.PORT || 3000;

if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`API server listening on port ${port}`);
  });
}

export default app;
