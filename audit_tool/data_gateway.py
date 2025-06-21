#!/usr/bin/env python3
"""
Data Gateway for Brand Audit Dashboard
Handles loading and caching of structured audit data
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class DataGateway:
    def __init__(self):
        # Look for audit_runs from the project root, regardless of where we're running from
        current_dir = Path(__file__).parent
        project_root = current_dir.parent  # Go up from audit_tool to project root
        self.runs_dir = project_root / "audit_runs"
    
    @st.cache_resource
    def load_available_runs(_self) -> List[str]:
        """Get list of available audit runs"""
        if not _self.runs_dir.exists():
            return []
        
        runs = []
        for d in _self.runs_dir.iterdir():
            if d.is_dir() and (d / "run_manifest.json").exists():
                runs.append(d.name)
        
        return sorted(runs, reverse=True)  # Most recent first
    
    @st.cache_resource
    def load_run_data(_self, run_id: str) -> Optional[Dict]:
        """Load all data for a specific run"""
        run_dir = _self.runs_dir / run_id
        
        if not run_dir.exists():
            return None
        
        try:
            # Load page facts
            page_facts_path = run_dir / "page_facts.parquet"
            page_facts = pd.read_parquet(page_facts_path) if page_facts_path.exists() else pd.DataFrame()
            
            # Load evidence
            evidence_path = run_dir / "evidence.parquet"
            evidence = pd.read_parquet(evidence_path) if evidence_path.exists() else pd.DataFrame()
            
            # Load manifest
            manifest_path = run_dir / "run_manifest.json"
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            return {
                'page_facts': page_facts,
                'evidence': evidence,
                'manifest': manifest,
                'run_id': run_id
            }
            
        except Exception as e:
            st.error(f"Error loading run data: {e}")
            return None
    
    @st.cache_data
    def get_filtered_data(_self, run_data: Dict, persona_filter: List[str] = None, 
                         score_filter: Tuple[float, float] = None, 
                         tier_filter: List[str] = None) -> pd.DataFrame:
        """Apply filters to page facts data"""
        if not run_data or run_data['page_facts'].empty:
            return pd.DataFrame()
            
        df = run_data['page_facts'].copy()
        
        if persona_filter:
            df = df[df['persona_id'].isin(persona_filter)]
        
        if score_filter:
            df = df[(df['raw_score'] >= score_filter[0]) & (df['raw_score'] <= score_filter[1])]
        
        if tier_filter:
            df = df[df['tier'].isin(tier_filter)]
        
        return df
    
    @st.cache_data
    def get_summary_stats(_self, df: pd.DataFrame) -> Dict:
        """Calculate summary statistics for filtered data"""
        if df.empty:
            return {}
        
        return {
            'total_pages': len(df['page_id'].unique()),
            'total_criteria': len(df),
            'average_score': df['raw_score'].mean(),
            'median_score': df['raw_score'].median(),
            'std_score': df['raw_score'].std(),
            'min_score': df['raw_score'].min(),
            'max_score': df['raw_score'].max(),
            'pass_count': len(df[df['descriptor'] == 'PASS']),
            'warn_count': len(df[df['descriptor'] == 'WARN']),
            'fail_count': len(df[df['descriptor'] == 'FAIL']),
            'pass_rate': len(df[df['descriptor'] == 'PASS']) / len(df) * 100 if len(df) > 0 else 0
        }
    
    @st.cache_data
    def get_tier_breakdown(_self, df: pd.DataFrame) -> pd.DataFrame:
        """Get performance breakdown by tier"""
        if df.empty:
            return pd.DataFrame()
        
        tier_stats = df.groupby('tier').agg({
            'raw_score': ['mean', 'count', 'std'],
            'descriptor': lambda x: (x == 'PASS').sum() / len(x) * 100
        }).round(2)
        
        tier_stats.columns = ['avg_score', 'count', 'std_dev', 'pass_rate']
        return tier_stats.reset_index()
    
    @st.cache_data
    def get_persona_comparison(_self, df: pd.DataFrame) -> pd.DataFrame:
        """Get comparison data across personas"""
        if df.empty:
            return pd.DataFrame()
        
        persona_stats = df.groupby('persona_id').agg({
            'raw_score': ['mean', 'count', 'std'],
            'descriptor': lambda x: (x == 'PASS').sum() / len(x) * 100
        }).round(2)
        
        persona_stats.columns = ['avg_score', 'count', 'std_dev', 'pass_rate']
        return persona_stats.reset_index()
    
    @st.cache_data
    def get_criteria_performance(_self, df: pd.DataFrame) -> pd.DataFrame:
        """Get performance by individual criteria"""
        if df.empty:
            return pd.DataFrame()
        
        criteria_stats = df.groupby('criterion_id').agg({
            'raw_score': ['mean', 'count', 'std', 'min', 'max'],
            'descriptor': lambda x: (x == 'PASS').sum() / len(x) * 100
        }).round(2)
        
        criteria_stats.columns = ['avg_score', 'count', 'std_dev', 'min_score', 'max_score', 'pass_rate']
        return criteria_stats.reset_index().sort_values('avg_score', ascending=False)
    
    def get_evidence_for_page(_self, run_data: Dict, page_id: str) -> List[Dict]:
        """Get evidence (justifications/recommendations) for a specific page"""
        if not run_data or run_data['evidence'].empty:
            return []
        
        evidence_df = run_data['evidence']
        page_evidence = evidence_df[evidence_df['page_id'] == page_id]
        
        return page_evidence.to_dict('records')
    
    def get_worst_performers(_self, df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
        """Get worst performing pages/criteria"""
        if df.empty:
            return pd.DataFrame()
        
        return df.nsmallest(limit, 'raw_score')[['url_slug', 'criterion_id', 'raw_score', 'descriptor']]
    
    def get_best_performers(_self, df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
        """Get best performing pages/criteria"""
        if df.empty:
            return pd.DataFrame()
        
        return df.nlargest(limit, 'raw_score')[['url_slug', 'criterion_id', 'raw_score', 'descriptor']] 