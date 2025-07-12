import { PlotlyChart } from './PlotlyChart';

export interface BarChartProps {
  x: (string | number)[];
  y: (string | number)[];
  title?: string;
  orientation?: 'v' | 'h';
}

export function BarChart({ x, y, title, orientation = 'v' }: BarChartProps) {
  return (
    <PlotlyChart
      data={[{
        x: orientation === 'v' ? x : y,
        y: orientation === 'v' ? y : x,
        type: 'bar',
        orientation,
      }]}
      layout={{
        title,
        xaxis: {
          title: orientation === 'v' ? 'Category' : 'Value',
        },
        yaxis: {
          title: orientation === 'v' ? 'Value' : 'Category',
        },
      }}
    />
  );
}

export default BarChart; 