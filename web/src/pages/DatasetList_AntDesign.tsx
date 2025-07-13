import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import {
  List,
  Typography,
  Alert,
  Spin,
  Layout
} from 'antd';
import { mapApiData } from '../utils/mapApiData';
import '../styles/ant.css';

const { Title } = Typography;
const { Content } = Layout;
const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000';

function DatasetList_AntDesign() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['datasets'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/datasets`);
      if (!res.ok) throw new Error('Failed to load datasets');
      return res.json();
    },
  });

  const mappedData = data ? mapApiData(data) : null;

  if (isLoading) {
    return (
      <div className="ant-design-root">
        <Layout className="dashboard-layout">
          <Content className="content-center">
            <Spin size="large" />
            <Title level={2} className="mt-24">Loading datasets...</Title>
          </Content>
        </Layout>
      </div>
    );
  }

  if (error || !mappedData) {
    return (
      <div className="ant-design-root">
        <Layout className="dashboard-layout">
          <Content>
            <Alert message="Error loading datasets" type="error" showIcon />
          </Content>
        </Layout>
      </div>
    );
  }

  const datasets: string[] = mappedData.datasets || [];

  return (
    <div className="ant-design-root">
      <Layout className="dashboard-layout">
        <Content>
          <Title level={1}>Datasets</Title>
          <List
            bordered
            dataSource={datasets}
            renderItem={(d) => (
              <List.Item>
                <Link to={`/datasets/${d}`}>{d}</Link>
              </List.Item>
            )}
          />
        </Content>
      </Layout>
    </div>
  );
}

export default DatasetList_AntDesign;
