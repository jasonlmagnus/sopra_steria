import express from 'express';
import cors from 'cors';
import swaggerUi from 'swagger-ui-express';
import swaggerJsdoc from 'swagger-jsdoc';

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
app.get('/api/datasets', (_req, res) => {
  res.json({ datasets: [] });
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
app.get('/api/pages', (_req, res) => {
  res.json({ pages: [] });
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
app.get('/api/recommendations', (_req, res) => {
  res.json({ recommendations: [] });
});

const port = process.env.PORT || 3000;

if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`API server listening on port ${port}`);
  });
}

export default app;
