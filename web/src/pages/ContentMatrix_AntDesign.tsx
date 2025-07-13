import React, { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layout, Typography, Row, Col, Card, Statistic, Table, Spin, Alert } from 'antd';
import { mapApiData } from '../utils/mapApiData';
import { useFilters } from '../hooks/useFilters';
import { FilterSystem } from '../components/FilterSystem';
import type { FilterConfig } from '../types/filters';
import '../styles/ant.css';

const { Title } = Typography;
const { Content } = Layout;
const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const contentMatrixFilters: FilterConfig[] = [
  { name: 'persona', label: '👥 Persona', type: 'select', defaultValue: 'All' },
  { name: 'tier', label: '🏗️ Content Tier', type: 'select', defaultValue: 'All' },
  {
    name: 'minScore',
    label: '📊 Min Score',
    type: 'range',
    defaultValue: 0,
    min: 0,
    max: 10,
    step: 0.5
  },
  {
    name: 'performanceLevel',
    label: '⭐ Performance Level',
    type: 'select',
    defaultValue: 'All',
    options: [
      { value: 'All', label: 'All' },
      { value: 'Excellent', label: 'Excellent (≥8)' },
      { value: 'Good', label: 'Good (6-8)' },
      { value: 'Fair', label: 'Fair (4-6)' },
      { value: 'Poor', label: 'Poor (<4)' }
    ]
  }
];

function ContentMatrix_AntDesign() {
  const { filters, setAllFilters } = useFilters();

  useEffect(() => {
    const defaults = contentMatrixFilters.reduce((acc, f) => {
      acc[f.name] = f.defaultValue;
      return acc;
    }, {} as { [key: string]: any });
    setAllFilters(defaults);
  }, [setAllFilters]);

  const { data, isLoading, error } = useQuery({
    queryKey: ['content-matrix-ant', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters as any);
      const res = await fetch(`${apiBase}/api/content-matrix?${params}`);
      if (!res.ok) throw new Error('Failed to load content matrix');
      return res.json();
    }
  });

  const mapped = data ? mapApiData(data) as any : null;

  if (isLoading) {
    return (
      <div className="ant-design-root">
        <Layout className="dashboard-layout">
          <Content className="content-center">
            <Spin size="large" />
            <Title level={2} className="mt-24">Loading content matrix...</Title>
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
            <Alert message="Error loading content matrix" type="error" showIcon />
          </Content>
        </Layout>
      </div>
    );
  }

  const metrics = mapped.metrics || {};
  const pages = Array.isArray(mapped.pages) ? mapped.pages : [];
  const tierAnalysis = Array.isArray(mapped.tierAnalysis) ? mapped.tierAnalysis : [];

  const columns = [
    { title: 'Page', dataIndex: 'title', key: 'title' },
    { title: 'Tier', dataIndex: 'tier', key: 'tier' },
    { title: 'Score', dataIndex: 'avgScore', key: 'avgScore', render: (v: number) => v?.toFixed?.(1) },
    { title: 'Personas', dataIndex: 'personas', key: 'personas' }
  ];

  return (
    <div className="ant-design-root">
      <Layout className="dashboard-layout">
        <Content>
          <Title level={1}>📊 Content Matrix (Ant)</Title>

          <Card className="mb-24" bordered={false}>
            <FilterSystem config={contentMatrixFilters} data={mapped} />
          </Card>

          <Row gutter={[16, 16]} className="mb-24">
            <Col xs={12} sm={6}>
              <Card>
                <Statistic title="Average Score" value={metrics.avgScore || 0} precision={1} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic title="Total Pages" value={metrics.totalPages || 0} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic title="Excellent" value={metrics.excellent || 0} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card>
                <Statistic title="Poor" value={metrics.poor || 0} />
              </Card>
            </Col>
          </Row>

          {tierAnalysis.length > 0 && (
            <Card title="Tier Performance" className="mb-24">
              <Row gutter={[16, 16]}>
                {tierAnalysis.map((t: any) => (
                  <Col key={t.tier} xs={12} sm={6}>
                    <Statistic title={t.name} value={t.avgScore} precision={1} />
                  </Col>
                ))}
              </Row>
            </Card>
          )}

          <Card title="Page Drill-Down">
            <Table columns={columns} dataSource={pages} rowKey="id" pagination={{ pageSize: 10 }} />
          </Card>
        </Content>
      </Layout>
    </div>
  );
}

export default ContentMatrix_AntDesign;
