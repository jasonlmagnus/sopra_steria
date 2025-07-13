import React, { useState, useEffect } from 'react';
import { Layout, Typography, Select, Button, Card, Spin, Alert } from 'antd';
import { mapApiData } from '../utils/mapApiData';
import '../styles/ant.css';

const { Title, Text } = Typography;
const { Option } = Select;
const { Content } = Layout;

interface HtmlReport {
  file_path: string;
  file_name: string;
  persona_name: string;
  report_type: string;
  category: 'Executive' | 'Persona' | 'Other';
  size: string;
  modified: string;
  relative_path: string;
}

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:3000';

function AuditReports_AntDesign() {
  const [reports, setReports] = useState<HtmlReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<HtmlReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [htmlContent, setHtmlContent] = useState('');
  const [regenerating, setRegenerating] = useState(false);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${apiBase}/api/html-reports`);
      if (!res.ok) throw new Error('Failed to fetch reports');
      const data = mapApiData(await res.json()) as any;
      const reportsData = Array.isArray(data.reports) ? data.reports : [];
      setReports(reportsData);
      const def = findDefaultReport(reportsData);
      if (def) {
        setSelectedReport(def);
        await loadHtmlContent(def);
      }
    } catch (err) {
      console.error('Error loading reports:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const findDefaultReport = (reps: HtmlReport[]): HtmlReport | null => {
    let def = reps.find((r) => r.file_name.toLowerCase().includes('index'));
    if (!def)
      def = reps.find((r) =>
        r.file_name.toLowerCase().includes('consolidated'),
      );
    if (!def) def = reps.find((r) => r.category === 'Executive');
    return def || reps[0] || null;
  };

  const loadHtmlContent = async (report: HtmlReport) => {
    try {
      const res = await fetch(
        `${apiBase}/api/html-reports/${report.relative_path}`,
      );
      if (!res.ok) throw new Error('Failed to load report');
      setHtmlContent(await res.text());
    } catch (err) {
      console.error('Error loading HTML:', err);
      setHtmlContent('<p>Error loading report</p>');
    }
  };

  const handleReportChange = async (value: string) => {
    const rep = reports.find(
      (r) => `${r.persona_name} - ${r.report_type}` === value,
    );
    if (rep) {
      setSelectedReport(rep);
      await loadHtmlContent(rep);
    }
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const res = await fetch(`${apiBase}/api/regenerate-reports`, {
        method: 'POST',
      });
      if (res.ok) {
        await fetchReports();
      } else {
        throw new Error('Failed to regenerate');
      }
    } catch (err) {
      console.error('Regenerate error:', err);
    } finally {
      setRegenerating(false);
    }
  };

  const handleDownloadReport = () => {
    if (!selectedReport) return;
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = selectedReport.file_name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadAll = async () => {
    const res = await fetch(`${apiBase}/api/download-all-reports`);
    if (res.ok) {
      const blob = await res.blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'sopra_steria_brand_reports.zip';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const reportOptions = reports.map(
    (r) => `${r.persona_name} - ${r.report_type}`,
  );

  if (loading) {
    return (
      <div className="ant-design-root">
        <Layout className="dashboard-layout">
          <Content className="content-center">
            <Spin size="large" />
            <Title level={2} className="mt-24">
              Loading reports...
            </Title>
          </Content>
        </Layout>
      </div>
    );
  }

  return (
    <div className="ant-design-root">
      <Layout className="dashboard-layout">
        <Content>
          <Title level={1}>📄 Audit Reports</Title>

          <div style={{ marginBottom: 24 }}>
            <Select
              style={{ width: '100%' }}
              onChange={handleReportChange}
              value={
                selectedReport
                  ? `${selectedReport.persona_name} - ${selectedReport.report_type}`
                  : undefined
              }
            >
              {reportOptions.map((opt) => (
                <Option key={opt} value={opt}>
                  {opt}
                </Option>
              ))}
            </Select>
          </div>

          <div style={{ marginBottom: 24 }}>
            <Button
              type="primary"
              onClick={handleRegenerate}
              loading={regenerating}
            >
              🔄 Regenerate All
            </Button>
            <Button
              onClick={handleDownloadReport}
              disabled={!selectedReport}
              style={{ marginLeft: 8 }}
            >
              Download Selected
            </Button>
            <Button onClick={handleDownloadAll} style={{ marginLeft: 8 }}>
              Download All ZIP
            </Button>
            {selectedReport && (
              <Button
                href={`${apiBase}/api/html-reports/${selectedReport.relative_path}`}
                target="_blank"
                style={{ marginLeft: 8 }}
              >
                Open in New Tab
              </Button>
            )}
          </div>

          {selectedReport ? (
            <Card
              title={`${selectedReport.persona_name} - ${selectedReport.report_type}`}
              className="mb-24"
            >
              <iframe
                srcDoc={htmlContent}
                title="Audit Report"
                style={{
                  width: '100%',
                  minHeight: '80vh',
                  border: '1px solid #ddd',
                }}
              />
              <Card type="inner" title="Technical Details" className="mt-24">
                <Text strong>File Path:</Text> {selectedReport.file_path}
                <br />
                <Text strong>Relative Path:</Text>{' '}
                {selectedReport.relative_path}
                <br />
                <Text strong>Size:</Text> {selectedReport.size}
              </Card>
            </Card>
          ) : (
            <Alert message="No report selected" type="info" />
          )}
        </Content>
      </Layout>
    </div>
  );
}

export default AuditReports_AntDesign;
