"""
Enhanced Data Loader for Brand Health Command Center
Handles loading and merging all CSV files with proper data type handling
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrandHealthDataLoader:
    """Enhanced data loader with proper type handling and derived metrics"""
    
    def __init__(self, data_directory: str = "audit_outputs"):
        # Always resolve relative to project root, not current working directory
        # This file is at audit_tool/dashboard/components/data_loader.py
        # So we need to go up 3 levels to get to project root
        project_root = Path(__file__).parent.parent.parent.parent
        self.data_directory = project_root / data_directory
        self.master_df = None
        
    def safe_sort_unique(self, series):
        """Handle mixed float/string types in sorting"""
        try:
            return sorted(series.dropna().astype(str).unique())
        except Exception as e:
            logger.warning(f"Error sorting series: {e}")
            return list(series.dropna().unique())
    
    @st.cache_data
    def load_enhanced_data(_self, persona_name: str = None):
        """Load and merge all CSV files with proper data types"""
        try:
            if persona_name:
                data_path = _self.data_directory / persona_name
            else:
                # Auto-detect available personas
                available_personas = [d.name for d in _self.data_directory.iterdir() if d.is_dir()]
                if not available_personas:
                    raise FileNotFoundError("No persona directories found")
                data_path = _self.data_directory / available_personas[0]
                logger.info(f"Auto-selected persona: {available_personas[0]}")
            
            # Define expected files and their key columns
            file_configs = {
                'pages.csv': {
                    'required_cols': ['page_id', 'url', 'tier', 'final_score'],
                    'optional_cols': ['slug', 'persona', 'audited_ts']
                },
                'criteria_scores.csv': {
                    'required_cols': ['page_id', 'criterion_code', 'score'],
                    'optional_cols': ['criterion_name', 'evidence', 'weight_pct', 'tier', 'descriptor']
                },
                'recommendations.csv': {
                    'required_cols': ['page_id', 'recommendation'],
                    'optional_cols': ['strategic_impact', 'complexity', 'urgency', 'resources']
                },
                'experience.csv': {
                    'required_cols': ['page_id', 'persona_id'],
                    'optional_cols': ['first_impression', 'sentiment', 'engagement', 'conversion_likelihood']
                },
                'scorecard_data.csv': {
                    'required_cols': ['page', 'url', 'tier', 'final_score'],
                    'optional_cols': []
                }
            }
            
            loaded_dfs = {}
            
            # Load each CSV file
            for filename, config in file_configs.items():
                file_path = data_path / filename
                if file_path.exists():
                    try:
                        df = pd.read_csv(file_path)
                        
                        # Validate required columns
                        missing_required = set(config['required_cols']) - set(df.columns)
                        if missing_required:
                            logger.warning(f"{filename}: Missing required columns: {missing_required}")
                            continue
                        
                        # Handle scorecard_data.csv special case (legacy compatibility)
                        if filename == 'scorecard_data.csv' and 'pages.csv' not in loaded_dfs:
                            # Rename columns to match standard format
                            df = df.rename(columns={'page': 'page_id'})
                            # Create page_id if it doesn't exist
                            if 'page_id' not in df.columns:
                                df['page_id'] = df['url'].str.replace('https://', '').str.replace('/', '_')
                        
                        # Ensure page_id exists for merging
                        if 'page_id' not in df.columns and 'page' in df.columns:
                            df['page_id'] = df['page']
                        
                        loaded_dfs[filename] = df
                        logger.info(f"Loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
                        
                    except Exception as e:
                        logger.error(f"Error loading {filename}: {e}")
                        continue
                else:
                    logger.warning(f"File not found: {file_path}")
            
            if not loaded_dfs:
                raise FileNotFoundError("No valid CSV files found")
            
            # Start with the main pages dataframe
            if 'pages.csv' in loaded_dfs:
                master_df = loaded_dfs['pages.csv'].copy()
            elif 'scorecard_data.csv' in loaded_dfs:
                master_df = loaded_dfs['scorecard_data.csv'].copy()
            else:
                raise ValueError("No base pages data found")
            
            # Merge other dataframes
            for filename, df in loaded_dfs.items():
                if filename in ['pages.csv', 'scorecard_data.csv']:
                    continue  # Already used as base
                
                try:
                    master_df = master_df.merge(df, on='page_id', how='left', suffixes=('', f'_{filename.split(".")[0]}'))
                    logger.info(f"Merged {filename}: {len(master_df)} rows after merge")
                except Exception as e:
                    logger.error(f"Error merging {filename}: {e}")
                    continue
            
            # Add derived metrics
            master_df = _self._add_derived_metrics(master_df)
            
            _self.master_df = master_df
            logger.info(f"Final master dataset: {len(master_df)} rows, {len(master_df.columns)} columns")
            
            return master_df
            
        except Exception as e:
            logger.error(f"Error in load_enhanced_data: {e}")
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def _add_derived_metrics(self, df):
        """Add calculated fields and derived metrics"""
        try:
            # Ensure numeric columns
            numeric_cols = ['final_score', 'score', 'weight_pct', 'conversion_likelihood']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Criterion gap (10 - score)
            if 'score' in df.columns:
                df['criterion_gap'] = 10 - df['score']
            
            # Effort level based on evidence length
            if 'evidence' in df.columns:
                df['evidence_length'] = df['evidence'].astype(str).str.len()
                df['effort_level'] = df['evidence_length'].apply(self._calculate_effort_level)
            
            # Potential impact
            if 'criterion_gap' in df.columns and 'weight_pct' in df.columns:
                df['potential_impact'] = df['criterion_gap'] * df['weight_pct'].fillna(1.0) * 0.1
            
            # Quick win flag
            if 'potential_impact' in df.columns and 'effort_level' in df.columns:
                df['quick_win_flag'] = (df['potential_impact'] >= 1.5) & (df['effort_level'] == 'Low')
            
            # Critical issue flag
            if 'descriptor' in df.columns:
                df['critical_issue_flag'] = df['descriptor'].str.contains('CONCERN', case=False, na=False)
            
            # Success page flag
            if 'final_score' in df.columns:
                df['success_page_flag'] = df['final_score'] >= 8.0
            
            # Sentiment numeric conversion
            if 'sentiment' in df.columns:
                sentiment_map = {'Positive': 1, 'Neutral': 0, 'Negative': -1}
                df['sentiment_numeric'] = df['sentiment'].map(sentiment_map).fillna(0)
            
            # Brand health descriptor
            if 'final_score' in df.columns:
                df['brand_health_descriptor'] = df['final_score'].apply(self._get_brand_health_descriptor)
            
            # Tier performance (will be calculated at aggregation level)
            df['tier_clean'] = df['tier'].astype(str) if 'tier' in df.columns else 'Unknown'
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding derived metrics: {e}")
            return df
    
    def _calculate_effort_level(self, evidence_length):
        """Calculate effort level based on evidence length"""
        if pd.isna(evidence_length):
            return 'Medium'
        if evidence_length < 300:
            return 'Low'
        elif evidence_length > 800:
            return 'High'
        else:
            return 'Medium'
    
    def _get_brand_health_descriptor(self, score):
        """Get brand health descriptor based on score"""
        if pd.isna(score):
            return 'Unknown'
        if score >= 8.0:
            return 'Excellent'
        elif score >= 4.0:
            return 'Good'
        else:
            return 'Critical'
    
    def get_available_personas(self):
        """Get list of available persona directories"""
        try:
            return [d.name for d in self.data_directory.iterdir() if d.is_dir()]
        except Exception:
            return []
    
    def get_summary_stats(self, df=None):
        """Get summary statistics for the dataset"""
        if df is None:
            df = self.master_df
        
        if df is None or df.empty:
            return {}
        
        try:
            stats = {
                'total_pages': len(df['page_id'].unique()) if 'page_id' in df.columns else 0,
                'total_records': len(df),
                'avg_score': df['final_score'].mean() if 'final_score' in df.columns else 0,
                'critical_issues': df['critical_issue_flag'].sum() if 'critical_issue_flag' in df.columns else 0,
                'quick_wins': df['quick_win_flag'].sum() if 'quick_win_flag' in df.columns else 0,
                'success_pages': df['success_page_flag'].sum() if 'success_page_flag' in df.columns else 0,
                'available_columns': list(df.columns),
                'data_quality': {
                    'missing_scores': df['final_score'].isna().sum() if 'final_score' in df.columns else 0,
                    'missing_tiers': df['tier'].isna().sum() if 'tier' in df.columns else 0,
                    'unique_pages': df['page_id'].nunique() if 'page_id' in df.columns else 0
                }
            }
            return stats
        except Exception as e:
            logger.error(f"Error calculating summary stats: {e}")
            return {} 