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
 * /api/html-reports/{path}:
 *   get:
 *     summary: Get HTML report content
 *     parameters:
 *       - in: path
 *         name: path
 *         required: true
 *         schema:
 *           type: string
 *         description: Relative path to HTML report
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
app.get('/api/html-reports/:path(*)', async (req, res) => {
  try {
    const { path: reportPath } = req.params
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

const port = process.env.PORT || 3000;

if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`API server listening on port ${port}`);
  });
}

export default app;
