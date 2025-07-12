import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import type { ColumnDef } from '@tanstack/react-table'
import React from 'react'
import { PageContainer, DataTable } from '../components'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function DatasetDetail() {
  const { name } = useParams()

  const { data, isLoading, error } = useQuery({
    queryKey: ['dataset', name],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/datasets/${name}`)
      if (!res.ok) throw new Error('Failed to load dataset')
      return res.json()
    },
    enabled: !!name,
  })

  const dataArray = Array.isArray(data) ? data : []

  // create columns dynamically from keys
  const columns = React.useMemo<ColumnDef<any, any>[]>(() => {
    if (dataArray.length === 0) return []
    return Object.keys(dataArray[0]).map(key => ({
      accessorKey: key,
      header: key,
    }))
  }, [dataArray])

  if (!name) return <p>No dataset specified</p>
  if (isLoading) return <p>Loading dataset...</p>
  if (error) return <p>Error loading dataset</p>

  return (
    <PageContainer title={`Dataset: ${name}`}>
      <DataTable data={dataArray} columns={columns} />
    </PageContainer>
  )
}

export default DatasetDetail
