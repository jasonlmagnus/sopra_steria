import { render, screen } from '@testing-library/react'
import { ColumnDef } from '@tanstack/react-table'
import { DataTable } from './DataTable'

interface Row {
  id: number
  name: string
}

describe('DataTable', () => {
  const columns: ColumnDef<Row>[] = [
    { accessorKey: 'id', header: 'ID' },
    { accessorKey: 'name', header: 'Name' }
  ]

  const data: Row[] = [
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' }
  ]

  it('renders table rows', () => {
    render(<DataTable data={data} columns={columns} />)
    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.getByText('Bob')).toBeInTheDocument()
  })
})
