import { useQuery } from '@tanstack/react-query';
import { Layout, Typography, Spin, Alert } from 'antd';
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { mapApiData } from '../utils/mapApiData';
import '../styles/ant.css';

const { Title } = Typography;
const { Content } = Layout;
const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000';

function PagesList_AntDesign() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['pages-ant'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/pages`);
      if (!res.ok) throw new Error('Failed to load pages');
      return res.json();
    },
  });

  const mapped = data ? (mapApiData(data) as any) : null;
  const pages = mapped?.pages || [];

  if (isLoading) {
    return (
      <div className="ant-design-root">
        <Layout className="dashboard-layout">
          <Content className="content-center">
            <Spin size="large" />
            <Title level={2} className="mt-24">
              Loading pages...
            </Title>
          </Content>
        </Layout>
      </div>
    );
  }

  if (error || !mapped) {
    return (
      <div className="ant-design-root">
        <Layout className="dashboard-layout">
          <Content>
            <Alert message="Error loading pages" type="error" showIcon />
          </Content>
        </Layout>
      </div>
    );
  }

  return (
    <div className="ant-design-root">
      <Layout className="dashboard-layout">
        <Content>
          <Title level={1}>Pages Brand Score</Title>
          <BarChart width={600} height={300} data={pages.slice(0, 10)}>
            <XAxis dataKey="slug" hide={true} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="avg_score" fill="#3d4a6b" />
          </BarChart>
        </Content>
      </Layout>
    </div>
  );
}

export default PagesList_AntDesign;
