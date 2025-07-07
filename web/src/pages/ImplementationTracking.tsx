import React, { useEffect, useState } from 'react'
import { PageContainer, ScoreCard, DataTable, ChartCard, PlotlyChart } from '../components'
import { ColumnDef } from '@tanstack/react-table'

interface Item {
  status: string
  progress: number
  team: string
  name: string
}

function ImplementationTracking() {
  const [items, setItems] = useState<Item[]>([])

  useEffect(() => {
    fetch('http://localhost:3000/api/implementation-tracking')
      .then((res) => res.json())
      .then((data: Item[]) => setItems(data))
      .catch(() => setItems([]))
  }, [])

  const totalItems = items.length
  const completed = items.filter(i => i.status === 'completed').length
  const inProgress = items.filter(i => i.status === 'in_progress').length
  const avgProgress = items.reduce((sum, i) => sum + i.progress, 0) / (totalItems || 1)
  const completionRate = totalItems ? (completed / totalItems) * 100 : 0


  const columns = React.useMemo<ColumnDef<Item>[]>(
    () => [
      { accessorKey: 'name', header: 'Initiative' },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: info => (info.getValue() as string).replace('_', ' ')
      },
      { accessorKey: 'progress', header: 'Progress', cell: info => `${info.getValue()}%` },
      { accessorKey: 'team', header: 'Team' }
    ],
    []
  )

  return (
    <PageContainer title="Implementation Tracking">
      <div className="filter-bar">
        <ScoreCard label="Total Items" value={totalItems} />
        <ScoreCard label="Completion Rate" value={`${completionRate.toFixed(1)}%`} />
        <ScoreCard label="Avg Progress" value={`${avgProgress.toFixed(1)}%`} />
        <ScoreCard label="In Progress" value={inProgress} />
      </div>

      <ChartCard title="Progress by Initiative">
        <PlotlyChart
          data={[
            {
              x: items.map(i => i.name),
              y: items.map(i => i.progress),
              type: 'bar',
              marker: { color: '#3d4a6b' }
            }
          ]}
          layout={{ xaxis: { title: 'Initiative' }, yaxis: { title: 'Progress' }, height: 300 }}
        />
      </ChartCard>

      <DataTable data={items} columns={columns} />
    </PageContainer>
  )
}

export default ImplementationTracking
