import React, { useState } from 'react';
// Using simple SVG icons instead of Heroicons for now
const ChevronDownIcon = ({ className }: { className: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

const ChevronUpIcon = ({ className }: { className: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
  </svg>
);

const DocumentTextIcon = ({ className }: { className: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const ExclamationTriangleIcon = ({ className }: { className: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
  </svg>
);

const CheckCircleIcon = ({ className }: { className: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

interface EvidenceItem {
  type: 'evidence' | 'effective_copy' | 'ineffective_copy' | 'trust_assessment' | 'business_impact' | 'information_gaps';
  content: string;
  title?: string;
}

interface EvidenceDisplayProps {
  evidence: EvidenceItem[];
  title?: string;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  maxHeight?: string;
}

export const EvidenceDisplay: React.FC<EvidenceDisplayProps> = ({
  evidence,
  title = "Evidence & Analysis",
  collapsible = true,
  defaultExpanded = false,
  maxHeight = "300px"
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const getEvidenceIcon = (type: EvidenceItem['type']) => {
    switch (type) {
      case 'effective_copy':
        return <CheckCircleIcon className="w-4 h-4 text-green-500" />;
      case 'ineffective_copy':
        return <ExclamationTriangleIcon className="w-4 h-4 text-red-500" />;
      case 'trust_assessment':
        return <DocumentTextIcon className="w-4 h-4 text-blue-500" />;
      case 'business_impact':
        return <DocumentTextIcon className="w-4 h-4 text-purple-500" />;
      case 'information_gaps':
        return <ExclamationTriangleIcon className="w-4 h-4 text-orange-500" />;
      default:
        return <DocumentTextIcon className="w-4 h-4 text-gray-500" />;
    }
  };

  const getEvidenceTypeLabel = (type: EvidenceItem['type']) => {
    switch (type) {
      case 'evidence':
        return 'AI Analysis';
      case 'effective_copy':
        return 'Effective Examples';
      case 'ineffective_copy':
        return 'Areas for Improvement';
      case 'trust_assessment':
        return 'Trust & Credibility';
      case 'business_impact':
        return 'Business Impact';
      case 'information_gaps':
        return 'Information Gaps';
      default:
        return 'Evidence';
    }
  };

  const getEvidenceColor = (type: EvidenceItem['type']) => {
    switch (type) {
      case 'effective_copy':
        return 'border-green-200 bg-green-50';
      case 'ineffective_copy':
        return 'border-red-200 bg-red-50';
      case 'trust_assessment':
        return 'border-blue-200 bg-blue-50';
      case 'business_impact':
        return 'border-purple-200 bg-purple-50';
      case 'information_gaps':
        return 'border-orange-200 bg-orange-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  if (!evidence || evidence.length === 0) {
    return (
      <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
        <p className="text-gray-500 text-sm">No evidence available</p>
      </div>
    );
  }

  return (
    <div className="border border-gray-200 rounded-lg bg-white">
      {collapsible ? (
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center space-x-2">
            <DocumentTextIcon className="w-5 h-5 text-gray-600" />
            <h3 className="font-medium text-gray-900">{title}</h3>
            <span className="text-sm text-gray-500">({evidence.length} items)</span>
          </div>
          {isExpanded ? (
            <ChevronUpIcon className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDownIcon className="w-5 h-5 text-gray-400" />
          )}
        </button>
      ) : (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <DocumentTextIcon className="w-5 h-5 text-gray-600" />
            <h3 className="font-medium text-gray-900">{title}</h3>
            <span className="text-sm text-gray-500">({evidence.length} items)</span>
          </div>
        </div>
      )}
      
      {(!collapsible || isExpanded) && (
        <div 
          className="p-4 space-y-4 overflow-y-auto"
          style={{ maxHeight: collapsible ? maxHeight : 'none' }}
        >
          {evidence.map((item, index) => (
            <div
              key={index}
              className={`p-3 border rounded-lg ${getEvidenceColor(item.type)}`}
            >
              <div className="flex items-start space-x-2">
                {getEvidenceIcon(item.type)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-sm font-medium text-gray-700">
                      {item.title || getEvidenceTypeLabel(item.type)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">
                    {item.content}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

interface EvidenceSearchProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

export const EvidenceSearch: React.FC<EvidenceSearchProps> = ({
  onSearch,
  placeholder = "Search evidence..."
}) => {
  const [query, setQuery] = useState('');

  const handleSearch = (value: string) => {
    setQuery(value);
    onSearch(value);
  };

  return (
    <div className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      <DocumentTextIcon className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
    </div>
  );
};

interface EvidenceBrowserProps {
  data: any[];
  evidenceColumns: string[];
  onEvidenceSelect?: (evidence: EvidenceItem[]) => void;
}

export const EvidenceBrowser: React.FC<EvidenceBrowserProps> = ({
  data,
  evidenceColumns,
  onEvidenceSelect
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');

  const extractEvidenceFromRow = (row: any): EvidenceItem[] => {
    const evidence: EvidenceItem[] = [];
    
    evidenceColumns.forEach(column => {
      if (row[column] && typeof row[column] === 'string' && row[column].trim().length > 0) {
        let type: EvidenceItem['type'] = 'evidence';
        
        if (column.includes('effective_copy')) type = 'effective_copy';
        else if (column.includes('ineffective_copy')) type = 'ineffective_copy';
        else if (column.includes('trust')) type = 'trust_assessment';
        else if (column.includes('business_impact')) type = 'business_impact';
        else if (column.includes('information_gaps')) type = 'information_gaps';
        
        evidence.push({
          type,
          content: row[column].trim(),
          title: column.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())
        });
      }
    });
    
    return evidence;
  };

  const filteredData = data.filter(row => {
    const evidence = extractEvidenceFromRow(row);
    
    if (searchQuery) {
      const hasMatch = evidence.some(item => 
        item.content.toLowerCase().includes(searchQuery.toLowerCase())
      );
      if (!hasMatch) return false;
    }
    
    if (selectedType !== 'all') {
      const hasType = evidence.some(item => item.type === selectedType);
      if (!hasType) return false;
    }
    
    return evidence.length > 0;
  });

  return (
    <div className="space-y-4">
      <div className="flex space-x-4">
        <div className="flex-1">
          <EvidenceSearch onSearch={setSearchQuery} />
        </div>
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">All Evidence Types</option>
          <option value="evidence">AI Analysis</option>
          <option value="effective_copy">Effective Examples</option>
          <option value="ineffective_copy">Areas for Improvement</option>
          <option value="trust_assessment">Trust & Credibility</option>
          <option value="business_impact">Business Impact</option>
          <option value="information_gaps">Information Gaps</option>
        </select>
      </div>

      <div className="space-y-4">
        {filteredData.map((row, index) => {
          const evidence = extractEvidenceFromRow(row);
          const pageTitle = row.url_slug || row.page_id || `Page ${index + 1}`;
          const score = row.raw_score || row.final_score || 0;
          
          return (
            <div key={index} className="border border-gray-200 rounded-lg bg-white">
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-gray-900">
                    {pageTitle.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                  </h3>
                  <span className="text-sm font-medium text-gray-600">
                    Score: {score.toFixed(1)}/10
                  </span>
                </div>
                {row.url && (
                  <a 
                    href={row.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    {row.url}
                  </a>
                )}
              </div>
              <div className="p-4">
                <EvidenceDisplay 
                  evidence={evidence}
                  title="Evidence Details"
                  collapsible={true}
                  defaultExpanded={false}
                />
              </div>
            </div>
          );
        })}
      </div>

      {filteredData.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No evidence found matching your criteria.
        </div>
      )}
    </div>
  );
};

export default EvidenceDisplay; 