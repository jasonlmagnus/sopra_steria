import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Table, Typography, Layout, Spin, Alert } from 'antd';
import { mapApiData } from '../utils/mapApiData';
import '../styles/ant.css';

const { Title } = Typography;
const { Content } = Layout;
const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000';

function DatasetDetail_AntDesign() {
  const { name } = useParams<{ name: string }>();

  const { data, isLoading, error } = useQuery({
    queryKey: ['dataset-ant', name],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/datasets/${name}`);
      if (!res.ok) throw new Error('Failed to load dataset');
      return res.json();
    },
    enabled: !!name,
  });

  const mapped = data ? (mapApiData(data) as any[]) : null;

  const columns = React.useMemo(() => {
    if (!Array.isArray(mapped) || mapped.length === 0) return [];
    return Object.keys(mapped[0]).map((key) => ({
      title: key,
      dataIndex: key,
      key,
    }));
  }, [mapped]);

  if (!name) {
    return (
      <div className="ant-design-root">
        <Layout className="dashboard-layout">
          <Content>
            <Alert message="No dataset specified" type="warning" showIcon />
          </Content>
        </Layout>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="ant-design-root">
        <Layout className="dashboard-layout">
          <Content className="content-center">
            <Spin size="large" />
            <Title level={2} className="mt-24">
              Loading dataset...
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
            <Alert message="Error loading dataset" type="error" showIcon />
          </Content>
        </Layout>
      </div>
    );
  }

  return (
    <div className="ant-design-root">
      <Layout className="dashboard-layout">
        <Content>
          <Title level={1}>{`Dataset: ${name}`}</Title>
          <Table
            columns={columns}
            dataSource={mapped}
            rowKey={(r) => JSON.stringify(r)}
            scroll={{ x: true }}
          />
        </Content>
      </Layout>
    </div>
  );
}

export default DatasetDetail_AntDesign;
