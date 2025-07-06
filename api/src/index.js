import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());

app.get('/api/hello', (_req, res) => {
  res.json({ message: 'Hello from API' });
});

const port = process.env.PORT || 3000;

if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`API server listening on port ${port}`);
  });
}

export default app;
