// Utility functions to normalize API data for dashboard components

export function isOidLike(str: string) {
  // Simple check: 8+ hex chars, no spaces, not a URL
  return /^[a-f0-9]{8,}$/i.test(str) && !str.startsWith('http');
}

export function mapOpportunity(raw: any) {
  let title = raw.title || raw.pageTitle || raw.page_title || raw.page_id || '';
  if (isOidLike(title)) title = 'Untitled Opportunity';
  const persona = raw.persona || raw.persona_id || raw.personaName || '';
  return {
    id: raw.id || raw.pageId || raw.page_id || '',
    title,
    description: raw.description || raw.recommendation || raw.evidence || '',
    persona,
    evidence: raw.evidence || '',
    score: raw.priority_score ?? raw.potentialImpact ?? raw.score ?? 0,
    url: raw.url || '',
    // Add more fields as needed for your UI
  };
}

export function mapSuccessStory(raw: any) {
  let title = raw.page_title || raw.title || raw.page_id || '';
  if (isOidLike(title)) title = 'Untitled Success Story';
  const persona = raw.persona || raw.persona_id || raw.personaName || '';
  return {
    id: raw.id || raw.page_id || '',
    title,
    description: raw.description || raw.evidence || '',
    persona,
    url: raw.url || '',
    score: raw.score ?? raw.raw_score ?? 0,
    // Add more fields as needed for your UI
  };
} 