export interface Opportunity {
  id: string;
  title: string;
  description: string;
  persona: string;
  page_id: string;
  priority_score: number;
  evidence?: string;
}

export interface SuccessStory {
  id: string;
  page_id: string;
  description: string;
  persona: string;
  url?: string;
  score: number;
}

// Generic mapping utility (identity by default)
export function mapApiData<T>(data: T): T {
  return data;
}

// Specific mapping helpers used by Ant pages
export function mapOpportunity(data: any): Opportunity {
  return {
    id: data.id || data.opportunity_id || '',
    title: data.title || data.name || '',
    description: data.description || data.desc || '',
    persona: data.persona || data.persona_name || 'Unknown',
    page_id: data.page_id || data.page || '',
    priority_score:
      data.priority_score !== undefined ? data.priority_score : data.score || 0,
    evidence: data.evidence || data.evidence_text || '',
  };
}

export function mapSuccessStory(data: any): SuccessStory {
  return {
    id: data.id || data.story_id || '',
    page_id: data.page_id || data.page || '',
    description: data.description || data.story || '',
    persona: data.persona || data.persona_name || 'Unknown',
    url: data.url || data.link || '',
    score: data.score !== undefined ? data.score : data.story_score || 0,
  };
}
