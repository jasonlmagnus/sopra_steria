import React from 'react'
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  useReactTable,
  type ColumnDef,
  type RowData,
  type SortingState
} from '@tanstack/react-table'

export interface DataTableProps<T extends RowData> {
  data: T[]
  columns: ColumnDef<T, any>[]
}

export function DataTable<T extends RowData>({ data, columns }: DataTableProps<T>) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [filter, setFilter] = React.useState('')

  const table = useReactTable({
    data,
    columns,
    state: { sorting, globalFilter: filter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    globalFilterFn: (row, _columnId, filterValue: string) => {
      const val = String(filterValue || '').toLowerCase()
      return row
        .getAllCells()
        .some(cell => String(cell.getValue()).toLowerCase().includes(val))
    }
  })

  return (
    <div>
      <input
        placeholder="Filter..."
        value={filter}
        onChange={e => setFilter(e.target.value)}
        style={{ marginBottom: '0.5rem' }}
      />
      <table>
      <thead>
        {table.getHeaderGroups().map(headerGroup => (
          <tr key={headerGroup.id}>
            {headerGroup.headers.map(header => (
              <th key={header.id} onClick={header.column.getToggleSortingHandler()} style={{cursor: 'pointer'}}>
                {header.isPlaceholder ? null :
                  flexRender(header.column.columnDef.header, header.getContext())}
                {{ asc: ' \u25B2', desc: ' \u25BC' }[header.column.getIsSorted() as string] ?? null}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map(row => (
          <tr key={row.id}>
            {row.getVisibleCells().map(cell => (
              <td key={cell.id}>
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
    </div>
  )
}

export default DataTable
