import { useQuery } from '@tanstack/react-query';

function DatasetList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['datasets'],
    queryFn: async () => {
      const res = await fetch('http://localhost:3000/api/datasets');
      if (!res.ok) throw new Error('Failed to load datasets');
      return res.json();
    },
  });

  if (isLoading) return <p>Loading datasets...</p>;
  if (error) return <p>Error loading datasets</p>;

  const datasets = data?.datasets || [];

  return (
    <div>
      <h2>Datasets</h2>
      <ul>
        {datasets.map((d: any, idx: number) => (
          <li key={idx}>{JSON.stringify(d)}</li>
        ))}
      </ul>
    </div>
  );
}

export default DatasetList;
