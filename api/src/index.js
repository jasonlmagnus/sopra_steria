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
  apis: []
});

app.use('/api/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

app.get('/api/hello', (_req, res) => {
  res.json({ message: 'Hello from API' });
});

app.get('/api/datasets', (_req, res) => {
  res.json({ datasets: [] });
});

app.get('/api/pages', (_req, res) => {
  res.json({ pages: [] });
});

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
