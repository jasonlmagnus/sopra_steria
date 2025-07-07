import React from 'react'
import type { ColumnDef } from '@tanstack/react-table'
import { useDataset } from '../hooks/useDataset'
import { PageContainer, DataTable, EvidenceBrowser } from '../components'

interface Success {
  title: string
  url: string
  score: number
}

function SuccessLibrary() {
  const { data: dataset, isLoading } = useDataset('master')

  const tableData = React.useMemo<Success[]>(() => {
    if (!dataset) return []
    return dataset
      .filter((d) => d.success_flag)
      .map((d) => ({
        title: d.url_slug,
        url: d.url,
        score: parseFloat(d.avg_score || 0)
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 10)
  }, [dataset])

  const columns = React.useMemo<ColumnDef<Success, any>[]>(
    () => [
      { accessorKey: 'title', header: 'Title' },
      {
        accessorKey: 'url',
        header: 'URL',
        cell: (info) => <a href={info.getValue() as string}>Link</a>
      },
      { accessorKey: 'score', header: 'Score' }
    ],
    []
  )


  if (isLoading) {
    return <p>Loading...</p>
  }

  return (
    <PageContainer title="Success Library">
      <EvidenceBrowser items={tableData} />
      <DataTable data={tableData} columns={columns} />
    </PageContainer>
  )
}

export default SuccessLibrary;
