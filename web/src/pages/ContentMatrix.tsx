import React from 'react'
import {
  ColumnDef,
  getCoreRowModel,
  useReactTable
} from '@tanstack/react-table'
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'
import { groupBy } from 'lodash-es'
import { useDataset } from '../hooks/useDataset'
import { FilterControls, FilterBar, ExpandableSection } from '../components'
import { useFilters } from '../context/FilterContext'

interface ContentItem {
  type: string
  count: number
  avgScore: number
}

function ContentMatrix() {
  const { data: dataset, isLoading } = useDataset('master')
  const { persona, tier } = useFilters()
  const options: { personas: string[]; tiers: string[] } = { personas: [], tiers: [] }

  const personaOptions = React.useMemo(
    () => (dataset ? Array.from(new Set(dataset.map(d => d.persona_id).filter(Boolean))) : []),
    [dataset]
  )
  const tierOptions = React.useMemo(
    () => (dataset ? Array.from(new Set(dataset.map(d => d.tier_name || d.tier).filter(Boolean))) : []),
    [dataset]
  )

  const tableData = React.useMemo<ContentItem[]>(() => {
    if (!dataset) return []
    options.personas = personaOptions
    options.tiers = tierOptions
    const filtered = dataset.filter(d =>
      (!persona || d.persona_id === persona) &&
      (!tier || d.tier_name === tier || d.tier === tier)
    )
    const groups = groupBy(filtered, (d) => d.tier_name || 'Unknown') as Record<
      string,
      any[]
    >
    return Object.entries(groups).map(([type, rows]) => {
      const count = rows.length
      const avgScore =
        rows.reduce((sum, r) => sum + parseFloat(r.avg_score || 0), 0) / count
      return { type, count, avgScore: Number(avgScore.toFixed(2)) }
    })
  }, [dataset, persona, tier, personaOptions, tierOptions])

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
      <FilterBar>
        <FilterControls personas={options.personas} tiers={options.tiers} />
      </FilterBar>
      <ExpandableSection title="Tier Scores" defaultExpanded>
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
      </ExpandableSection>
      <ExpandableSection title="Matrix Table" defaultExpanded>
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
      </ExpandableSection>
    </div>
  )
}

export default ContentMatrix;
