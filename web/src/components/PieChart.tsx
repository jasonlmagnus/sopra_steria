import { PlotlyChart } from './PlotlyChart';

export interface PieChartProps {
  labels: string[];
  values: number[];
  title?: string;
}

export function PieChart({ labels, values, title }: PieChartProps) {
  return (
    <PlotlyChart
      data={[{
        labels,
        values,
        type: 'pie',
        hole: 0.4,
      }]}
      layout={{
        title,
      }}
    />
  );
}

export default PieChart; 