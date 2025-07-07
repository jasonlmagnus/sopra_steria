import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { DataTable, PageContainer } from '../components'
import { type ColumnDef } from '@tanstack/react-table'

function AuditReports() {
  const { data, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: async () => {
      const res = await fetch('http://localhost:3000/api/reports')
      if (!res.ok) throw new Error('Failed to fetch reports')
      return res.json()
    }
  })

  if (isLoading) {
    return <p>Loading...</p>
  }

  const reports: { name: string }[] = (data?.reports || []).map((r: string) => ({ name: r }))

  const columns: ColumnDef<{ name: string }>[] = [
    {
      accessorKey: 'name',
      header: 'Report',
      cell: info => (
        <a href={`http://localhost:3000/api/reports/${info.getValue()}`}>{info.getValue()}</a>
      )
    }
  ]

  return (
    <PageContainer title="Audit Reports">
      <DataTable data={reports} columns={columns} />
    </PageContainer>
  )
}

export default AuditReports;
