import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

const data = [
  { month: 'Jan', mentions: 120 },
  { month: 'Feb', mentions: 90 },
  { month: 'Mar', mentions: 150 },
  { month: 'Apr', mentions: 130 },
];

function SocialMediaAnalysis() {
  return (
    <div>
      <h2>Social Media Analysis</h2>
      <LineChart width={600} height={300} data={data}>
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="mentions" stroke="#dc3545" />
      </LineChart>
    </div>
  );
}

export default SocialMediaAnalysis;
