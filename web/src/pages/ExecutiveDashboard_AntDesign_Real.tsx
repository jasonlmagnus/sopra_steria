import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useFilters } from '../hooks/useFilters';
import { FilterSystem } from '../components/FilterSystem';
import PagesList from './PagesList';
import type { FilterConfig } from '../types/filters';
import { mapOpportunity, mapSuccessStory } from '../utils/mapApiData';

// Ant Design imports
import {
  Card,
  Row,
  Col,
  Statistic,
  Badge,
  Typography,
  Button,
  Alert,
  Spin,
  Collapse,
  List,
  Tag,
  Layout
} from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  EyeOutlined,
  UserOutlined,
  GlobalOutlined,
  BarChartOutlined,
  AimOutlined,
  TrophyOutlined,
  RocketOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  LinkOutlined
} from '@ant-design/icons';
import '../styles/ant.css';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;
const { Content } = Layout;

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const dashboardFilters: FilterConfig[] = [
  {
    name: 'tier',
    label: 'Focus on Content Tier:',
    type: 'select',
    defaultValue: 'All Tiers',
    options: [
      { value: 'All Tiers', label: 'All Tiers' },
      { value: 'Tier 1 (Strategic)', label: 'Tier 1 (Strategic)' },
      { value: 'Tier 2 (Tactical)', label: 'Tier 2 (Tactical)' },
      { value: 'Tier 3 (Operational)', label: 'Tier 3 (Operational)' },
    ],
  },
];

// Standard Card Component for Ant Design
const StandardCard = ({ 
  label, 
  value, 
  status, 
  children 
}: { 
  label: string; 
  value: string | number; 
  status?: string; 
  children?: React.ReactNode 
}) => {
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'excellent': return '#52c41a';
      case 'good': return '#1890ff';
      case 'warning': return '#faad14';
      case 'critical': return '#ff4d4f';
      default: return '#8c8c8c';
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'excellent': return <CheckCircleOutlined />;
      case 'good': return <ArrowUpOutlined />;
      case 'warning': return <WarningOutlined />;
      case 'critical': return <ArrowDownOutlined />;
      default: return <InfoCircleOutlined />;
    }
  };

  return (
    <Card hoverable>
      <Statistic
        title={label}
        value={value}
        valueStyle={{ color: getStatusColor(status) }}
        prefix={getStatusIcon(status)}
      />
      {children && <Text type="secondary" style={{ fontSize: '12px' }}>{children}</Text>}
    </Card>
  );
};

function ExecutiveDashboard_AntDesign_Real() {
  const { filters, setAllFilters } = useFilters();

  useEffect(() => {
    const defaultFilters = dashboardFilters.reduce((acc, f) => {
      acc[f.name] = f.defaultValue;
      return acc;
    }, {} as { [key: string]: any });
    setAllFilters(defaultFilters);
  }, [setAllFilters]);
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['summary'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/summary`)
      if (!res.ok) throw new Error('Failed to load summary')
      return res.json()
    }
  })

  const { data: oppData } = useQuery({
    queryKey: ['opportunities'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/opportunities?limit=3`)
      if (!res.ok) throw new Error('Failed to load opportunities')
      return res.json()
    }
  })

  const { data: strategicData } = useQuery({
    queryKey: ['strategic-assessment', filters.tier],
    queryFn: async () => {
      const tierParam = filters.tier && filters.tier !== 'All Tiers' ? `?tier=${encodeURIComponent(filters.tier)}` : '';
      const res = await fetch(`${apiBase}/api/strategic-assessment${tierParam}`);
      if (!res.ok) throw new Error('Failed to load strategic assessment');
      return res.json();
    },
    enabled: !!filters.tier,
  });

  const { data: successData } = useQuery({
    queryKey: ['success-stories'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/success-stories?limit=5&min_score=7.5`)
      if (!res.ok) throw new Error('Failed to load success stories')
      return res.json()
    }
  })

  if (isLoading) return (
    <div className="ant-design-root">
      <Layout className="dashboard-layout">
        <Content className="content-center">
          <Spin size="large" />
          <Title level={2} className="mt-24">Loading brand health metrics...</Title>
        </Content>
      </Layout>
    </div>
  )

  if (error) return (
    <div className="ant-design-root">
      <Layout className="dashboard-layout">
        <Content>
          <Alert
            message="Error"
            description="Error loading dashboard data"
            type="error"
            showIcon
            icon={<ExclamationCircleOutlined />}
          />
        </Content>
      </Layout>
    </div>
  )

  const brand = data?.brand_health || {}
  const metrics = data?.key_metrics || {}
  const sentiment = data?.sentiment || {}
  const conversion = data?.conversion || {}
  const recs = Array.isArray(data?.recommendations) ? data.recommendations : []
  const opps = Array.isArray(oppData?.opportunities)
    ? oppData.opportunities.map(mapOpportunity)
    : [];

  const successStories = Array.isArray(successData?.success_stories)
    ? successData.success_stories.map(mapSuccessStory)
    : [];

  // Use real strategic assessment data when available
  const getDistinctivenessScore = () => {
    if (strategicData?.distinctiveness?.score !== undefined) {
      return strategicData.distinctiveness.score
    }
    // Fallback calculation if API fails
    const baseScore = (brand.raw_score || 0) * 0.6 + (sentiment.net_sentiment || 0) * 0.4
    return Math.min(Math.max(baseScore, 0), 10)
  }

  const getResonanceScore = () => {
    if (strategicData?.resonance?.net_sentiment !== undefined) {
      return strategicData.resonance.net_sentiment / 10
    }
    // Fallback: use existing sentiment data converted to 0-10 scale
    return Math.max((sentiment.net_sentiment || 0) / 10, 0)
  }

  const getConversionScore = () => {
    if (strategicData?.conversion?.score !== undefined) {
      return strategicData.conversion.score
    }
    // Fallback: use existing conversion data
    return conversion.raw_score || 0
  }

  const getScoreStatus = (score: number) => {
    if (score >= 7.0) return "HIGH"
    if (score >= 4.0) return "MODERATE"
    return "LOW"
  }

  const getHealthStatus = (score: number) => {
    if (score >= 7.0) return 'excellent'
    if (score >= 4.0) return 'warning'
    return 'critical'
  }

  const getScoreColor = (score: number) => {
    if (score >= 7.0) return '#52c41a'
    if (score >= 4.0) return '#faad14'
    return '#ff4d4f'
  }

  return (
    <div className="ant-design-root">
      <Layout className="dashboard-layout">
        <Content>
          <div className="mb-24">
            <Row justify="space-between" align="middle">
              <Col>
                <Title level={1} style={{ margin: 0, color: '#1f2937' }}>
                  Brand Health Command Center
                </Title>
                <Text type="secondary" style={{ fontSize: '16px' }}>
                  30-second strategic marketing decision engine for executives
                </Text>
              </Col>
              <Col>
                <Badge.Ribbon text="Real Data - Ant Design" color="blue">
                  <div style={{ width: '120px', height: '40px' }} />
                </Badge.Ribbon>
              </Col>
            </Row>
          </div>

          {/* Brand Health Overview */}
          <Card 
            title={
              <Title level={2} style={{ margin: 0 }}>
                <BarChartOutlined style={{ marginRight: '8px' }} />
                Brand Health Overview
              </Title>
            }
            style={{ marginBottom: '24px' }}
          >
            <Row gutter={[24, 24]}>
              <Col xs={24} sm={12} md={6}>
                <StandardCard
                  label="Overall Brand Health"
                  value={`${brand.raw_score || 0}/10`}
                  status={getHealthStatus(brand.raw_score)}
                >
                  {brand.status || 'Unknown'}
                </StandardCard>
              </Col>
              <Col xs={24} sm={12} md={6}>
                <StandardCard
                  label="Critical Issues"
                  value={metrics.critical_issues || 0}
                  status={(metrics.critical_issues || 0) > 10 ? 'critical' : 'warning'}
                />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <StandardCard
                  label="Quick Wins"
                  value={metrics.quick_wins || 0}
                  status="good"
                />
              </Col>
              <Col xs={24} sm={12} md={6}>
                <StandardCard
                  label="Success Pages"
                  value={metrics.success_pages || 0}
                  status="excellent"
                />
              </Col>
            </Row>
          </Card>

          {/* Strategic Focus */}
          <Card 
            title={
              <Title level={3} style={{ margin: 0 }}>
                <AimOutlined style={{ marginRight: '8px' }} />
                Strategic Focus
              </Title>
            }
            style={{ marginBottom: '24px' }}
          >
            <FilterSystem config={dashboardFilters} data={{}} />
          </Card>

          {/* Strategic Brand Assessment */}
          <Card 
            title={
              <Title level={2} style={{ margin: 0 }}>
                <BarChartOutlined style={{ marginRight: '8px' }} />
                Strategic Brand Assessment
              </Title>
            }
            style={{ marginBottom: '24px' }}
          >
            <Row gutter={[24, 24]}>
              {/* Are we distinct? */}
              <Col xs={24} md={8}>
                <Card type="inner" title="Are we distinct?" hoverable>
                  {(() => {
                    const score = getDistinctivenessScore()
                    const status = getScoreStatus(score)
                    
                    return (
                      <div>
                        <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
                          <Col>
                            <Statistic
                              value={score.toFixed(1)}
                              suffix="/ 10"
                              valueStyle={{ color: getScoreColor(score), fontSize: '32px' }}
                            />
                          </Col>
                          <Col>
                            <Tag color={score >= 7 ? 'green' : score >= 4 ? 'orange' : 'red'}>
                              {status}
                            </Tag>
                          </Col>
                        </Row>
                        <Paragraph>
                          <Text strong>How we measure:</Text><br/>
                          First impression uniqueness (40%)<br/>
                          Brand visibility (30%)<br/>
                          Distinctive language tone (30%)
                        </Paragraph>
                      </div>
                    )
                  })()}
                </Card>
              </Col>

              {/* Are we resonating? */}
              <Col xs={24} md={8}>
                <Card type="inner" title="Are we resonating?" hoverable>
                  {(() => {
                    const score = getResonanceScore()
                    const status = getScoreStatus(score)
                    
                    return (
                      <div>
                        <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
                          <Col>
                            <Statistic
                              value={score.toFixed(1)}
                              suffix="/ 10"
                              valueStyle={{ color: getScoreColor(score), fontSize: '32px' }}
                            />
                          </Col>
                          <Col>
                            <Tag color={score >= 7 ? 'green' : score >= 4 ? 'orange' : 'red'}>
                              {status}
                            </Tag>
                          </Col>
                        </Row>
                        <Paragraph>
                          <Text strong>How we measure:</Text><br/>
                          User sentiment scores (50%)<br/>
                          Content engagement (30%)<br/>
                          Success rate (20%)
                        </Paragraph>
                      </div>
                    )
                  })()}
                </Card>
              </Col>

              {/* Are we converting? */}
              <Col xs={24} md={8}>
                <Card type="inner" title="Are we converting?" hoverable>
                  {(() => {
                    const score = getConversionScore()
                    const status = getScoreStatus(score)
                    
                    return (
                      <div>
                        <Row justify="space-between" align="middle" style={{ marginBottom: '16px' }}>
                          <Col>
                            <Statistic
                              value={score.toFixed(1)}
                              suffix="/ 10"
                              valueStyle={{ color: getScoreColor(score), fontSize: '32px' }}
                            />
                          </Col>
                          <Col>
                            <Tag color={score >= 7 ? 'green' : score >= 4 ? 'orange' : 'red'}>
                              {status}
                            </Tag>
                          </Col>
                        </Row>
                        <Paragraph>
                          <Text strong>How we measure:</Text><br/>
                          Conversion likelihood (50%)<br/>
                          Trust & credibility (30%)<br/>
                          Performance metrics (20%)
                        </Paragraph>
                      </div>
                    )
                  })()}
                </Card>
              </Col>
            </Row>
          </Card>

          {/* Top 3 Improvement Opportunities */}
          <Card 
            title={
              <Title level={2} style={{ margin: 0 }}>
                <AimOutlined style={{ marginRight: '8px' }} />
                Top 3 Improvement Opportunities
              </Title>
            }
            style={{ marginBottom: '24px' }}
          >
            <Alert
              message="For comprehensive analysis, visit the Opportunity & Impact tab"
              type="info"
              showIcon
              style={{ marginBottom: '16px' }}
            />

            {opps.length > 0 ? (
              <Collapse>
                {opps.map((opp: any) => (
                  <Panel 
                    key={opp.id} 
                    header={
                      <Row justify="space-between" align="middle">
                        <Col flex="auto">
                          <Text strong>{opp.title}</Text>
                        </Col>
                        <Col>
                          <Badge 
                            count={`${(opp.score || 0).toFixed(1)}/10`} 
                            style={{ backgroundColor: opp.score >= 8 ? '#52c41a' : '#1890ff' }}
                          />
                        </Col>
                      </Row>
                    }
                  >
                    <Paragraph>{opp.description}</Paragraph>
                    <List size="small">
                      <List.Item>
                        <Text strong>Page:</Text> {opp.id}
                      </List.Item>
                      <List.Item>
                        <Text strong>Persona:</Text> {opp.persona}
                      </List.Item>
                      <List.Item>
                        <Text strong>Evidence:</Text> <Text type="secondary" italic>{opp.evidence}</Text>
                      </List.Item>
                      {opp.url && (
                        <List.Item>
                          <Text strong>URL:</Text> <Button type="link" href={opp.url} target="_blank" style={{ wordBreak: 'break-all', whiteSpace: 'normal', textAlign: 'left', padding: 0 }}>{opp.url}</Button>
                        </List.Item>
                      )}
                    </List>
                  </Panel>
                ))}
              </Collapse>
            ) : (
              <Text type="secondary">No improvement opportunities found.</Text>
            )}
          </Card>

          {/* Top 5 Success Stories */}
          <Card 
            title={
              <Title level={2} style={{ margin: 0 }}>
                <TrophyOutlined style={{ marginRight: '8px' }} />
                Top 5 Success Stories
              </Title>
            }
            style={{ marginBottom: '24px' }}
          >
            <Alert
              message="For comprehensive analysis, visit the Success Library tab"
              type="info"
              showIcon
              style={{ marginBottom: '16px' }}
            />

            {successStories.length > 0 ? (
              <Collapse>
                {successStories.map((story: any) => (
                  <Panel 
                    key={story.id} 
                    header={
                      <Row justify="space-between" align="middle">
                        <Col flex="auto">
                          <Text strong>{story.title}</Text>
                        </Col>
                        <Col>
                          <Badge 
                            count={`${(story.score || 0).toFixed(1)}/10`} 
                            style={{ backgroundColor: '#52c41a' }}
                          />
                        </Col>
                      </Row>
                    }
                  >
                    <Paragraph>{story.description}</Paragraph>
                    <List size="small">
                      <List.Item>
                        <Text strong>Persona:</Text> {story.persona}
                      </List.Item>
                      {story.url && (
                        <List.Item>
                          <Text strong>URL:</Text>
                          <Button
                            type="link"
                            href={story.url}
                            target="_blank"
                            style={{ wordBreak: 'break-all', whiteSpace: 'normal', textAlign: 'left', padding: 0 }}
                            icon={<LinkOutlined />}
                          >
                            {story.url}
                          </Button>
                        </List.Item>
                      )}
                    </List>
                  </Panel>
                ))}
              </Collapse>
            ) : (
              <Text type="secondary">No success stories found.</Text>
            )}
          </Card>

          {/* Strategic Recommendations */}
          {recs.length > 0 && (
            <Card 
              title={
                <Title level={2} style={{ margin: 0 }}>
                  <RocketOutlined style={{ marginRight: '8px' }} />
                  Strategic Recommendations
                </Title>
              }
              style={{ marginBottom: '24px' }}
            >
              <Alert
                message="AI-generated action priorities based on current brand health"
                type="info"
                showIcon
                style={{ marginBottom: '16px' }}
              />

              <List
                dataSource={recs}
                renderItem={(rec: any, index: number) => (
                  <List.Item
                    actions={[
                      <Button 
                        type="primary" 
                        size="small"
                        icon={
                          rec.toLowerCase().includes('critical pages') || rec.toLowerCase().includes('scoring below') ? (
                            <EyeOutlined />
                          ) : rec.toLowerCase().includes('quick wins') || rec.toLowerCase().includes('immediate impact') ? (
                            <ArrowUpOutlined />
                          ) : rec.toLowerCase().includes('persona') ? (
                            <UserOutlined />
                          ) : rec.toLowerCase().includes('improvements') || rec.toLowerCase().includes('opportunities') ? (
                            <AimOutlined />
                          ) : (
                            <BarChartOutlined />
                          )
                        }
                      >
                        {rec.toLowerCase().includes('critical pages') || rec.toLowerCase().includes('scoring below') ? (
                          'View Critical Pages'
                        ) : rec.toLowerCase().includes('quick wins') || rec.toLowerCase().includes('immediate impact') ? (
                          'See Quick Wins'
                        ) : rec.toLowerCase().includes('persona') ? (
                          'Analyze Persona'
                        ) : rec.toLowerCase().includes('improvements') || rec.toLowerCase().includes('opportunities') ? (
                          'Get Action Plan'
                        ) : (
                          'Explore Analysis'
                        )}
                      </Button>
                    ]}
                  >
                    <List.Item.Meta
                      title={`${index + 1}. Recommendation`}
                      description={rec}
                    />
                  </List.Item>
                )}
              />
            </Card>
          )}

          {/* Page Performance Overview */}
          <Card 
            title={
              <Title level={2} style={{ margin: 0 }}>
                <EyeOutlined style={{ marginRight: '8px' }} />
                Page Performance Overview
              </Title>
            }
            style={{ marginBottom: '24px' }}
          >
            <Alert
              message="Quick visual overview of brand scores across all audited pages"
              type="info"
              showIcon
              style={{ marginBottom: '16px' }}
            />
            <PagesList />
          </Card>

          {/* Deep-Dive Analysis Navigation */}
          <Card 
            title={
              <Title level={2} style={{ margin: 0 }}>
                <GlobalOutlined style={{ marginRight: '8px' }} />
                Deep-Dive Analysis
              </Title>
            }
          >
            <Paragraph>
              <Text strong>Need more details?</Text> Visit these specialized tabs for comprehensive analysis:
            </Paragraph>

            <Row gutter={[24, 24]}>
              <Col xs={24} md={8}>
                <Card type="inner" title="📊 Analysis Tabs" size="small">
                  <List size="small">
                    <List.Item>
                      <Text strong>👥 Persona Insights</Text> - How different personas experience your brand
                    </List.Item>
                    <List.Item>
                      <Text strong>📊 Content Matrix</Text> - Detailed performance by content type and tier
                    </List.Item>
                  </List>
                </Card>
              </Col>

              <Col xs={24} md={8}>
                <Card type="inner" title="🎯 Action Tabs" size="small">
                  <List size="small">
                    <List.Item>
                      <Text strong>💡 Opportunity & Impact</Text> - Comprehensive improvement roadmap
                    </List.Item>
                    <List.Item>
                      <Text strong>🌟 Success Library</Text> - Pattern analysis and replication guides
                    </List.Item>
                  </List>
                </Card>
              </Col>

              <Col xs={24} md={8}>
                <Card type="inner" title="📋 Data & Tools" size="small">
                  <List size="small">
                    <List.Item>
                      <Text strong>📋 Reports & Export</Text> - Custom reports and data exports
                    </List.Item>
                    <List.Item>
                      <Text strong>🚀 Run Audit</Text> - Generate fresh audit data
                    </List.Item>
                  </List>
                </Card>
              </Col>
            </Row>
          </Card>
        </Content>
      </Layout>
    </div>
  );
}

export default ExecutiveDashboard_AntDesign_Real; 