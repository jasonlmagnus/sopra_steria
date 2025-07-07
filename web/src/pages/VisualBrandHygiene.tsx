import React from 'react';
import { PieChart, Pie, Tooltip, Cell } from 'recharts';

const data = [
  { name: 'Compliant', value: 70 },
  { name: 'Needs Update', value: 20 },
  { name: 'Off Brand', value: 10 },
];

const colors = ['#3d4a6b', '#dc3545', '#8884d8'];

function VisualBrandHygiene() {
  return (
    <div>
      <h2>Visual Brand Hygiene</h2>
      <PieChart width={400} height={300}>
        <Pie dataKey="value" data={data} cx="50%" cy="50%" outerRadius={100}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </div>
  );
}

export default VisualBrandHygiene;
