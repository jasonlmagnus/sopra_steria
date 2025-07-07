import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ColumnDef, getCoreRowModel, useReactTable } from '@tanstack/react-table'
import React from 'react'

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

  if (!name) return <p>No dataset specified</p>
  if (isLoading) return <p>Loading dataset...</p>
  if (error) return <p>Error loading dataset</p>

  const dataArray = Array.isArray(data) ? data : []

  // create columns dynamically from keys
  const columns = React.useMemo<ColumnDef<any, any>[]>(() => {
    if (dataArray.length === 0) return []
    return Object.keys(dataArray[0]).map(key => ({
      accessorKey: key,
      header: key,
    }))
  }, [dataArray])

  const table = useReactTable({ data: dataArray, columns, getCoreRowModel: getCoreRowModel() })

  return (
    <div>
      <h2>Dataset: {name}</h2>
      <table>
        <thead>
          {table.getHeaderGroups().map(headerGroup => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map(header => (
                <th key={header.id}>{header.isPlaceholder ? null : header.column.columnDef.header as string}</th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map(row => (
            <tr key={row.id}>
              {row.getVisibleCells().map(cell => (
                <td key={cell.id}>{cell.renderValue<string>()}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default DatasetDetail
