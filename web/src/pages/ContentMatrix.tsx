import React from 'react';
import {
  ColumnDef,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

interface ContentItem {
  type: string;
  count: number;
  avgScore: number;
}

const data: ContentItem[] = [
  { type: 'Blog', count: 15, avgScore: 6.2 },
  { type: 'Landing Page', count: 8, avgScore: 7.1 },
  { type: 'Case Study', count: 5, avgScore: 8.4 },
  { type: 'Video', count: 4, avgScore: 7.8 },
];

function ContentMatrix() {
  const columns = React.useMemo<ColumnDef<ContentItem, any>[]>(
    () => [
      { accessorKey: 'type', header: 'Type' },
      { accessorKey: 'count', header: 'Count' },
      { accessorKey: 'avgScore', header: 'Avg Score' },
    ],
    [],
  );

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div>
      <h2>Content Matrix</h2>
      <BarChart
        width={600}
        height={300}
        data={data}
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
  );
}

export default ContentMatrix;
