import React from 'react'
import {
  ColumnDef,
  getCoreRowModel,
  useReactTable
} from '@tanstack/react-table'
import { useDataset } from '../hooks/useDataset'

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
      <h2>Success Library</h2>
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

export default SuccessLibrary;
