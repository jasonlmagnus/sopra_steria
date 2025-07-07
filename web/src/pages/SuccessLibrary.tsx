import React from 'react';
import {
  ColumnDef,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';

interface Success {
  title: string;
  url: string;
  score: number;
}

const data: Success[] = [
  { title: 'Case Study A', url: 'https://example.com/a', score: 8.5 },
  { title: 'Landing Page B', url: 'https://example.com/b', score: 7.9 },
  { title: 'Video Campaign C', url: 'https://example.com/c', score: 9.1 },
];

function SuccessLibrary() {
  const columns = React.useMemo<ColumnDef<Success, any>[]>(
    () => [
      { accessorKey: 'title', header: 'Title' },
      {
        accessorKey: 'url',
        header: 'URL',
        cell: (info) => <a href={info.getValue() as string}>Link</a>,
      },
      { accessorKey: 'score', header: 'Score' },
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
  );
}

export default SuccessLibrary;
