import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { PageContainer } from '../components'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000';

function DatasetList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['datasets'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/datasets`);
      if (!res.ok) throw new Error('Failed to load datasets');
      return res.json();
    },
  });

  if (isLoading) return <p>Loading datasets...</p>;
  if (error) return <p>Error loading datasets</p>;

  const datasets = data?.datasets || [];

  return (
    <PageContainer title="Datasets">
      <ul>
        {datasets.map((d: any, idx: number) => (
          <li key={idx}>
            <Link to={`/datasets/${d}`}>{d}</Link>
          </li>
        ))}
      </ul>
    </PageContainer>
  )
}

export default DatasetList;
