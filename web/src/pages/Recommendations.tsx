import { useQuery } from '@tanstack/react-query'
import { ColumnDef, getCoreRowModel, useReactTable } from '@tanstack/react-table'
import React from 'react'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function Recommendations() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['recommendations'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/recommendations`)
      if (!res.ok) throw new Error('Failed to load recommendations')
      return res.json()
    },
  })

  if (isLoading) return <p>Loading recommendations...</p>
  if (error) return <p>Error loading recommendations</p>

  const recs = Array.isArray(data?.recommendations) ? data.recommendations : []

  const columns = React.useMemo<ColumnDef<any, any>[]>(() => {
    if (recs.length === 0) return []
    return Object.keys(recs[0]).map(key => ({ accessorKey: key, header: key }))
  }, [recs])

  const table = useReactTable({ data: recs, columns, getCoreRowModel: getCoreRowModel() })

  return (
    <div>
      <h2>Recommendations</h2>
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

export default Recommendations
