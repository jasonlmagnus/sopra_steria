import { useQuery } from '@tanstack/react-query';
import '../styles/ant.css';
import { Layout, Typography, Tabs, Card, List, Alert, Spin } from 'antd';
import { mapApiData } from '../utils/mapApiData';

const { Content } = Layout;
const { Title, Paragraph, Text } = Typography;

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000';

function Methodology_AntDesign() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['methodology'],
    queryFn: async () => {
      const res = await fetch(`${apiBase}/api/methodology`);
      if (!res.ok) throw new Error('Failed to load methodology');
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
            <Title level={2} className="mt-24">
              Loading methodology...
            </Title>
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
            <Alert message="Error loading methodology data" type="error" showIcon />
          </Content>
        </Layout>
      </div>
    );
  }

  const renderOverview = () => {
    const metadata = (mappedData as any).metadata || {};
    const calc = (mappedData as any).calculation || {};
    const multipliers = calc.crisis_multipliers || {};
    return (
      <div>
        <Card className="mb-24" title={<Title level={4}>Brand Health Audit Methodology</Title>}>
          <Paragraph>
            <Text strong>Version:</Text> {metadata.version || 'N/A'}{' '}
            <Text strong>Updated:</Text> {metadata.updated || 'N/A'}
          </Paragraph>
          <Paragraph>
            <Text strong>Corporate Tagline:</Text> "{metadata.tagline || 'The world is how we shape it'}"
          </Paragraph>
          <Paragraph>{metadata.description}</Paragraph>
        </Card>

        <Card className="mb-24" title={<Title level={4}>Brand Score Calculation</Title>}>
          <Paragraph>
            <Text strong>Formula:</Text> <code>{calc.formula}</code>
          </Paragraph>
          <List
            dataSource={[
              `Onsite Weight: ${(calc.onsite_weight || 0.7) * 100}% (Your website and digital properties)`,
              `Offsite Weight: ${(calc.offsite_weight || 0.3) * 100}% (Third-party platforms and reviews)`,
              'Crisis Impact: Can reduce overall score by up to 70%',
            ]}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>

        <Card className="mb-24" title={<Title level={4}>Crisis Impact Multipliers</Title>}>
          <Paragraph>Reputation issues can significantly impact your overall brand health score:</Paragraph>
          <List
            dataSource={Object.entries(multipliers)}
            renderItem={([crisis, mult]) => (
              <List.Item>
                <Text strong>{crisis.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}:</Text>{' '}
                {mult} multiplier{' '}
                {Number(mult) < 1 && (
                  <Text type="secondary">({((1 - Number(mult)) * 100).toFixed(0)}% reduction)</Text>
                )}
              </List.Item>
            )}
          />
        </Card>

        <Card title={<Title level={4}>Audit Process</Title>}>
          <Paragraph>The brand health audit follows a structured 5-stage process:</Paragraph>
          <List
            dataSource={[
              'Page Classification: Categorize content into Tier 1 (Brand), Tier 2 (Value Prop), or Tier 3 (Functional)',
              'Criteria Assessment: Apply tier-specific scoring criteria with appropriate brand/performance weightings',
              'Evidence Collection: Gather verbatim quotes and specific examples to support all scores',
              'Brand Consistency Check: Validate messaging hierarchy, visual identity, and approved content usage',
              'Strategic Recommendations: Prioritize improvements by impact, effort, and urgency',
            ]}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>
      </div>
    );
  };

  const renderScoring = () => {
    const scoring = (mappedData as any).scoring || {};
    const descriptors = scoring.descriptors || {};
    const evidence = (mappedData as any).evidence || {};
    return (
      <div>
        <Card className="mb-24" title={<Title level={4}>Scoring Scale</Title>}>
          <Paragraph>
            All criteria are scored on a <Text strong>{scoring.scale?.min || 0}-{scoring.scale?.max || 10}</Text> scale with mandatory evidence requirements.
          </Paragraph>
        </Card>

        <Card className="mb-24" title={<Title level={4}>Score Interpretation</Title>}>
          <List
            dataSource={Object.entries(descriptors)}
            renderItem={([range, details]) => {
              const det = details as any;
              return (
                <List.Item>
                  <Text strong>{range}: {det.label}</Text> - <Text>{det.status}</Text>
                </List.Item>
              );
            }}
          />
        </Card>

        <Card title={<Title level={4}>Evidence Requirements</Title>}>
          <Paragraph>All scores must be supported by specific evidence from the audited content:</Paragraph>
          <div className="mb-24">
            <Title level={5}>High Scores (≥7)</Title>
            <Paragraph>
              <Text strong>Requirement:</Text> {evidence.high_scores?.requirement || ''}
            </Paragraph>
            <Paragraph>
              <Text strong>Penalty:</Text> {evidence.high_scores?.penalty || ''}
            </Paragraph>
          </div>
          <div>
            <Title level={5}>Low Scores (≤4)</Title>
            <Paragraph>
              <Text strong>Requirement:</Text> {evidence.low_scores?.requirement || ''}
            </Paragraph>
            <Paragraph>
              <Text strong>Penalty:</Text> {evidence.low_scores?.penalty || ''}
            </Paragraph>
          </div>
        </Card>
      </div>
    );
  };

  const renderClassification = () => {
    const classification = (mappedData as any).classification || {};
    const onsite = classification.onsite || {};
    const offsite = classification.offsite || {};
    return (
      <div>
        <Card className="mb-24" title={<Title level={4}>Onsite Tiers</Title>}>
          {Object.entries(onsite).map(([tierKey, tierData]) => {
            const tier = tierData as any;
            return (
              <Card key={tierKey} type="inner" title={`${tierKey.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}: ${tier.name}`} className="mb-24">
                <List
                  dataSource={[
                    `Weight in Onsite: ${(tier.weight_in_onsite * 100).toFixed(0)}%`,
                    `Brand Focus: ${tier.brand_percentage}%`,
                    `Performance Focus: ${tier.performance_percentage}%`,
                  ]}
                  renderItem={(item) => <List.Item>{item}</List.Item>}
                />
                <List
                  header={<Text strong>Triggers</Text>}
                  dataSource={tier.triggers || []}
                  renderItem={(item) => <List.Item>{item}</List.Item>}
                />
                <List
                  header={<Text strong>Examples</Text>}
                  dataSource={tier.examples || []}
                  renderItem={(item) => <List.Item>{item}</List.Item>}
                />
              </Card>
            );
          })}
        </Card>

        <Card title={<Title level={4}>Offsite Channels</Title>}>
          {Object.entries(offsite).map(([channelKey, channelData]) => {
            const channel = channelData as any;
            return (
              <Card key={channelKey} type="inner" title={channel.name} className="mb-24">
                <List
                  dataSource={[
                    `Weight in Offsite: ${(channel.weight_in_offsite * 100).toFixed(0)}%`,
                    channel.brand_percentage !== undefined ? `Brand Focus: ${channel.brand_percentage}%` : undefined,
                    channel.authenticity_percentage !== undefined ? `Authenticity Focus: ${channel.authenticity_percentage}%` : undefined,
                    channel.sentiment_percentage !== undefined ? `Sentiment Focus: ${channel.sentiment_percentage}%` : undefined,
                    `Examples: ${(channel.examples || []).join(', ')}`,
                  ].filter(Boolean)}
                  renderItem={(item) => <List.Item>{item}</List.Item>}
                />
              </Card>
            );
          })}
        </Card>
      </div>
    );
  };

  const renderCriteria = () => {
    const criteria = (mappedData as any).criteria || {};
    return (
      <div>
        {Object.entries(criteria).map(([tierKey, tierCriteria]) => {
          const tier = tierCriteria as any;
          return (
            <Card key={tierKey} title={<Title level={4}>{tierKey.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())} Criteria</Title>} className="mb-24">
              {tier.brand_criteria && (
                <div className="mb-24">
                  <Title level={5}>Brand Criteria</Title>
                  {Object.entries(tier.brand_criteria).map(([criterionKey, criterionData]) => {
                    const criterion = criterionData as any;
                    return (
                      <Card key={criterionKey} type="inner" title={`${criterionKey.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())} (${criterion.weight}%)`} className="mb-24">
                        <Paragraph>
                          <Text strong>Description:</Text> {criterion.description}
                        </Paragraph>
                        <Paragraph>
                          <Text strong>Requirements:</Text>
                        </Paragraph>
                        <List dataSource={criterion.requirements || []} renderItem={(item) => <List.Item>{item}</List.Item>} />
                      </Card>
                    );
                  })}
                </div>
              )}
              {tier.performance_criteria && (
                <div>
                  <Title level={5}>Performance Criteria</Title>
                  {Object.entries(tier.performance_criteria).map(([criterionKey, criterionData]) => {
                    const criterion = criterionData as any;
                    return (
                      <Card key={criterionKey} type="inner" title={`${criterionKey.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())} (${criterion.weight}%)`} className="mb-24">
                        <Paragraph>
                          <Text strong>Description:</Text> {criterion.description}
                        </Paragraph>
                        <Paragraph>
                          <Text strong>Requirements:</Text>
                        </Paragraph>
                        <List dataSource={criterion.requirements || []} renderItem={(item) => <List.Item>{item}</List.Item>} />
                      </Card>
                    );
                  })}
                </div>
              )}
            </Card>
          );
        })}
      </div>
    );
  };

  const renderStandards = () => {
    const standards = (mappedData as any).standards || {};
    return (
      <div>
        <Card className="mb-24" title={<Title level={4}>Messaging Hierarchy</Title>}>
          {Object.entries(standards.messaging_hierarchy || {}).map(([levelKey, levelData]) => {
            const level = levelData as any;
            return (
              <Card key={levelKey} type="inner" title={`${level.level}: ${level.name}`} className="mb-24">
                <Paragraph>
                  <Text strong>Description:</Text> {level.description}
                </Paragraph>
                <Paragraph>
                  <Text strong>Examples:</Text>
                </Paragraph>
                <List dataSource={level.examples || []} renderItem={(item) => <List.Item>{item}</List.Item>} />
              </Card>
            );
          })}
        </Card>

        <Card className="mb-24" title={<Title level={4}>Approved Content</Title>}>
          {Object.entries(standards.approved_content || {}).map(([contentKey, contentData]) => {
            const content = contentData as any;
            return (
              <Card key={contentKey} type="inner" title={contentKey.replace(/_/g, ' ')} className="mb-24">
                <Paragraph>
                  <Text strong>Description:</Text> {content.description}
                </Paragraph>
                <Paragraph>
                  <Text strong>Approved Sources:</Text>
                </Paragraph>
                <List dataSource={content.approved_sources || []} renderItem={(item) => <List.Item>{item}</List.Item>} />
                {content.usage_guidelines && (
                  <>
                    <Paragraph>
                      <Text strong>Usage Guidelines:</Text>
                    </Paragraph>
                    <List dataSource={content.usage_guidelines || []} renderItem={(item) => <List.Item>{item}</List.Item>} />
                  </>
                )}
              </Card>
            );
          })}
        </Card>

        <Card title={<Title level={4}>Visual Identity</Title>}>
          {Object.entries(standards.visual_identity || {}).map(([elementKey, elementData]) => {
            const element = elementData as any;
            return (
              <Card key={elementKey} type="inner" title={element.name} className="mb-24">
                <Paragraph>
                  <Text strong>Description:</Text> {element.description}
                </Paragraph>
                <Paragraph>
                  <Text strong>Guidelines:</Text>
                </Paragraph>
                <List dataSource={element.guidelines || []} renderItem={(item) => <List.Item>{item}</List.Item>} />
              </Card>
            );
          })}
        </Card>
      </div>
    );
  };

  const renderControls = () => {
    const gating = (mappedData as any).gating_rules || {};
    const penalties = (mappedData as any).quality_penalties || {};
    const flags = (mappedData as any).validation_flags || {};
    const examples = (mappedData as any).examples || {};
    return (
      <div>
        <Card className="mb-24" title={<Title level={4}>Hard Gating Rules (Non-Negotiable)</Title>}>
          <Paragraph>These rules automatically trigger score penalties and cannot be overridden:</Paragraph>
          {Object.entries(gating).map(([ruleKey, ruleData]) => {
            const rule = ruleData as any;
            return (
              <Card key={ruleKey} type="inner" title={`${rule.severity} - ${ruleKey.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}`} className="mb-24">
                <Paragraph>
                  <Text strong>Trigger:</Text> {rule.trigger}
                </Paragraph>
                <Paragraph>
                  <Text strong>Penalty:</Text> {rule.penalty}
                </Paragraph>
              </Card>
            );
          })}
        </Card>

        <Card className="mb-24" title={<Title level={4}>Copy Quality Penalties</Title>}>
          {Object.entries(penalties).map(([penaltyKey, penaltyData]) => {
            const penalty = penaltyData as any;
            return (
              <Card key={penaltyKey} type="inner" title={`${penaltyKey.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}: ${penalty.points} points`} className="mb-24">
                {penalty.example && (
                  <Paragraph>
                    <Text strong>Example:</Text> {penalty.example}
                  </Paragraph>
                )}
                {penalty.examples && (
                  <>
                    <Paragraph>
                      <Text strong>Examples:</Text>
                    </Paragraph>
                    <List dataSource={penalty.examples} renderItem={(item) => <List.Item>{item}</List.Item>} />
                  </>
                )}
              </Card>
            );
          })}
        </Card>

        <Card className="mb-24" title={<Title level={4}>Validation Flags</Title>}>
          {Object.entries(flags).map(([category, flagList]) => (
            <Card key={category} type="inner" title={`${category.replace(/\b\w/g, (l) => l.toUpperCase())} Flags`} className="mb-24">
              {Object.entries(flagList as any).map(([flagKey, flagData]) => {
                const flag = flagData as any;
                return (
                  <Paragraph key={flagKey}>
                    • <Text strong>{flagKey.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}:</Text> {flag.penalty}
                  </Paragraph>
                );
              })}
            </Card>
          ))}
        </Card>

        {Object.keys(examples).length > 0 && (
          <Card title={<Title level={4}>Scoring Examples</Title>}>
            {Object.entries(examples).map(([exampleKey, exampleData]) => {
              const example = exampleData as any;
              return (
                <Card key={exampleKey} type="inner" title={`${exampleKey.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())} (Score: ${example.score}/10)`} className="mb-24">
                  <Paragraph>
                    <Text strong>Example Text:</Text>
                  </Paragraph>
                  <Paragraph>"{example.text}"</Paragraph>
                  {example.why_good && (
                    <>
                      <Paragraph>
                        <Text strong>Why this scores well:</Text>
                      </Paragraph>
                      <List dataSource={example.why_good} renderItem={(item) => <List.Item>{item}</List.Item>} />
                    </>
                  )}
                  {example.why_bad && (
                    <>
                      <Paragraph>
                        <Text strong>Why this scores poorly:</Text>
                      </Paragraph>
                      <List dataSource={example.why_bad} renderItem={(item) => <List.Item>{item}</List.Item>} />
                    </>
                  )}
                </Card>
              );
            })}
          </Card>
        )}
      </div>
    );
  };

  const items = [
    { key: 'overview', label: 'Overview', children: renderOverview() },
    { key: 'scoring', label: 'Scoring Framework', children: renderScoring() },
    { key: 'classification', label: 'Page Classification', children: renderClassification() },
    { key: 'criteria', label: 'Tier Criteria', children: renderCriteria() },
    { key: 'standards', label: 'Brand Standards', children: renderStandards() },
    { key: 'controls', label: 'Quality Controls', children: renderControls() },
  ];

  return (
    <div className="ant-design-root">
      <Layout className="dashboard-layout">
        <Content>
          <Title level={1}>🔬 Methodology</Title>
          <Tabs items={items} />
        </Content>
      </Layout>
    </div>
  );
}

export default Methodology_AntDesign;
