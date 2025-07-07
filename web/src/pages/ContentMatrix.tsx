import React from 'react'
import {
  ColumnDef,
  getCoreRowModel,
  useReactTable
} from '@tanstack/react-table'
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'
import { groupBy } from 'lodash-es'
import { useDataset } from '../hooks/useDataset'

interface ContentItem {
  type: string
  count: number
  avgScore: number
}

function ContentMatrix() {
  const { data: dataset, isLoading } = useDataset('master')

  const tableData = React.useMemo<ContentItem[]>(() => {
    if (!dataset) return []
    const groups = groupBy(dataset, (d) => d.tier_name || 'Unknown') as Record<
      string,
      any[]
    >
    return Object.entries(groups).map(([type, rows]) => {
      const count = rows.length
      const avgScore =
        rows.reduce((sum, r) => sum + parseFloat(r.avg_score || 0), 0) / count
      return { type, count, avgScore: Number(avgScore.toFixed(2)) }
    })
  }, [dataset])

  const columns = React.useMemo<ColumnDef<ContentItem, any>[]>(
    () => [
      { accessorKey: 'type', header: 'Type' },
      { accessorKey: 'count', header: 'Count' },
      { accessorKey: 'avgScore', header: 'Avg Score' }
    ],
    []
  )

  const table = useReactTable({
    data: tableData,
    columns,
    getCoreRowModel: getCoreRowModel()
  })

  if (isLoading) {
    return <p>Loading...</p>
  }

  return (
    <div>
      <h2>Content Matrix</h2>
      <BarChart
        width={600}
        height={300}
        data={tableData}
        style={{ marginBottom: '1rem' }}
      >
        <XAxis dataKey="type" hide={true} />
        <YAxis />
        <Tooltip />
        <Bar dataKey="avgScore" fill="#3d4a6b" />
      </BarChart>
      <table>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id}>
                  {header.isPlaceholder
                    ? null
                    : (header.column.columnDef.header as string)}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>{cell.renderValue<string>()}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ContentMatrix;
