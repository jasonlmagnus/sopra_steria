import { useQuery } from '@tanstack/react-query'

export interface DatasetRecord {
  [key: string]: any
}

export function useDataset(name: string) {
  return useQuery<DatasetRecord[]>({
    queryKey: ['dataset', name],
    queryFn: async () => {
      const res = await fetch(`http://localhost:3000/api/datasets/${name}`)
      if (!res.ok) throw new Error('Failed to fetch dataset')
      return res.json()
    }
  })
}
