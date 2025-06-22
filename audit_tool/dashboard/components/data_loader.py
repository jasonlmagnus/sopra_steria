"""
Enhanced Data Loader for Brand Health Command Center
Handles loading and merging all CSV files with proper data type handling
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrandHealthDataLoader:
    """Enhanced data loader with proper type handling and derived metrics"""
    
    def __init__(self, audit_outputs_dir: str = "audit_outputs"):
        self.audit_outputs_dir = Path("audit_outputs")
        self.unified_data_dir = Path("audit_data")
        
    def safe_sort_unique(self, series):
        """Handle mixed float/string types in sorting"""
        try:
            return sorted(series.dropna().astype(str).unique())
        except Exception as e:
            logger.warning(f"Error sorting series: {e}")
            return list(series.dropna().unique())
    
    def load_unified_data(self) -> pd.DataFrame:
        """Load the unified dataset from CSV"""
        try:
            # Load standard unified dataset (enhanced version removed - was identical)
            standard_path = self.unified_data_dir / "unified_audit_data.csv"
            if standard_path.exists():
                df = pd.read_csv(standard_path)
                logger.info(f"Loaded unified dataset: {len(df)} rows, {len(df.columns)} columns")
                
                # Ensure avg_score column exists for dashboard compatibility
                if 'avg_score' not in df.columns:
                    if 'final_score' in df.columns:
                        df['avg_score'] = df['final_score']
                    elif 'raw_score' in df.columns:
                        df['avg_score'] = df['raw_score']
                    elif 'raw_score' in df.columns:
                        df['avg_score'] = df['raw_score']
                
                return df
            
            logger.error("No unified dataset found")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error loading unified data: {e}")
            return pd.DataFrame()

    @st.cache_data  
    def load_experience_data(_self):
        """Load unified experience dataset"""
        try:
            experience_file = _self.unified_data_dir / "unified_experience_data.csv"
            if experience_file.exists():
                df = pd.read_csv(experience_file)
                logger.info(f"Loaded unified experience data: {len(df)} rows, {len(df.columns)} columns")
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading experience data: {str(e)}")
            return pd.DataFrame()

    def load_all_data(self):
        """Load all data (unified dataset only)"""
        # Load primary unified dataset
        master_df = self.load_unified_data()
        
        if master_df.empty:
            logger.error("Failed to load unified dataset")
            return {}, pd.DataFrame()
        
        # Create datasets dictionary for compatibility with existing dashboard pages
        # ALL pages should use the same unified dataset with consistent column names
        datasets = {
            'master': master_df,
            'criteria_scores': master_df,  # Legacy compatibility
            'criteria': master_df,  # Fix for pages expecting 'criteria' key
            'experience': master_df,  # All experience data is in unified CSV
            'recommendations': master_df,  # All recommendation data is in unified CSV
            'pages': master_df  # All page data is in unified CSV
        }
        
        logger.info(f"Loaded unified data: {len(master_df)} rows, {len(master_df.columns)} columns")
        return datasets, master_df
    
    def _add_unified_derived_metrics(self, df):
        """Add derived metrics for unified dataset"""
        try:
            # Brand health descriptor
            if 'raw_score' in df.columns:
                df['brand_health_descriptor'] = df['raw_score'].apply(self._get_brand_health_descriptor)
                df['criterion_gap'] = 10 - df['raw_score']
            
            # Critical issue flag
            if 'descriptor' in df.columns:
                df['critical_issue_flag'] = df['descriptor'].str.contains('FAIL|CONCERN', case=False, na=False)
            
            # Success flag
            if 'raw_score' in df.columns:
                df['success_flag'] = df['raw_score'] >= 8.0
            
            # Quick win potential (high impact, low current score)
            if 'raw_score' in df.columns:
                df['quick_win_potential'] = (df['raw_score'] < 6.0) & (df['raw_score'] > 2.0)
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding unified derived metrics: {e}")
            return df

    @st.cache_data
    def load_unified_experience_data(_self):
        """Load unified experience data from CSV file"""
        try:
            experience_file = _self.unified_data_dir / "unified_experience_data.csv"
            if not experience_file.exists():
                logger.warning(f"Unified experience data not found at {experience_file}")
                return pd.DataFrame()
            
            df = pd.read_csv(experience_file)
            logger.info(f"Loaded unified experience data: {len(df)} rows, {len(df.columns)} columns")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading unified experience data: {e}")
            return pd.DataFrame()

    @st.cache_data
    def load_enhanced_data(_self, persona_name: str = None):
        """Load and merge all CSV files with proper data types"""
        try:
            if persona_name:
                data_path = _self.audit_outputs_dir / persona_name
            else:
                # Auto-detect available personas
                available_personas = [d.name for d in _self.audit_outputs_dir.iterdir() if d.is_dir()]
                if not available_personas:
                    raise FileNotFoundError("No persona directories found")
                data_path = _self.audit_outputs_dir / available_personas[0]
                logger.info(f"Auto-selected persona: {available_personas[0]}")
            
            # Define expected files and their key columns
            file_configs = {
                'pages.csv': {
                    'required_cols': ['page_id', 'url', 'tier', 'final_score'],
                    'optional_cols': ['slug', 'persona', 'audited_ts']
                },
                'criteria_scores.csv': {
                    'required_cols': ['page_id', 'criterion_code', 'raw_score'],
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
            
            # Merge criteria_scores for the master dataframe (but keep separate datasets)
            if 'criteria_scores.csv' in loaded_dfs:
                master_df = master_df.merge(
                    loaded_dfs['criteria_scores.csv'], 
                    on='page_id', 
                    how='left', 
                    suffixes=('', '_criteria')
                )
                logger.info(f"Merged criteria_scores.csv: {len(master_df)} rows after merge")
            
            # Merge experience data into master dataframe for sentiment/conversion metrics
            if 'experience.csv' in loaded_dfs:
                master_df = master_df.merge(
                    loaded_dfs['experience.csv'], 
                    on='page_id', 
                    how='left', 
                    suffixes=('', '_experience')
                )
                logger.info(f"Merged experience.csv: {len(master_df)} rows after merge")
            
            # Add derived metrics to master
            master_df = _self._add_derived_metrics(master_df)
            
            _self.master_df = master_df
            logger.info(f"Final master dataset: {len(master_df)} rows, {len(master_df.columns)} columns")
            
            # Return both master dataframe and separate datasets
            datasets = {
                'master': master_df,
                'criteria': master_df,  # For backwards compatibility
                'pages': loaded_dfs.get('pages.csv'),
                'criteria_scores': loaded_dfs.get('criteria_scores.csv'),
                'recommendations': loaded_dfs.get('recommendations.csv'),
                'experience': loaded_dfs.get('experience.csv'),
                'scorecard_data': loaded_dfs.get('scorecard_data.csv')
            }
            
            return datasets
            
        except Exception as e:
            logger.error(f"Error in load_enhanced_data: {e}")
            st.error(f"Error loading data: {e}")
            return {
                'master': pd.DataFrame(),
                'criteria': pd.DataFrame(),
                'pages': None,
                'criteria_scores': None,
                'recommendations': None,
                'experience': None,
                'scorecard_data': None
            }
    
    def _add_derived_metrics(self, df):
        """Add calculated fields and derived metrics"""
        try:
            # Ensure numeric columns
            numeric_cols = ['final_score', 'raw_score', 'weight_pct', 'conversion_likelihood']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Criterion gap (10 - score)
            if 'raw_score' in df.columns:
                df['criterion_gap'] = 10 - df['raw_score']
            
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
            return [d.name for d in self.audit_outputs_dir.iterdir() if d.is_dir()]
        except Exception:
            return []
    
    def get_summary_stats(self, master_df: pd.DataFrame, datasets: Dict = None) -> Dict:
        """Generate summary statistics for the dashboard"""
        if master_df.empty:
            return {
                'total_pages': 0,
                'total_personas': 0,
                'total_criteria': 0,
                'has_experience_data': False,
                'has_recommendations': False
            }
        
        # Calculate summary stats from unified data
        summary = {
            'total_pages': master_df['page_id'].nunique() if 'page_id' in master_df.columns else 0,
            'total_personas': master_df['persona_id'].nunique() if 'persona_id' in master_df.columns else 0,
            'total_criteria': master_df['criterion_id'].nunique() if 'criterion_id' in master_df.columns else 0,
            'has_experience_data': any(col in master_df.columns for col in ['overall_sentiment', 'engagement_level', 'conversion_likelihood']),
            'has_recommendations': 'quick_win_flag' in master_df.columns or (datasets and 'recommendations' in datasets),
            'data_shape': master_df.shape,
            'available_columns': master_df.columns.tolist()
        }
        
        # Add score-related stats if available
        if 'raw_score' in master_df.columns:
            summary['avg_score'] = master_df['raw_score'].mean()
            summary['score_column'] = 'raw_score'
        elif 'final_score' in master_df.columns:
            summary['avg_score'] = master_df['final_score'].mean()
            summary['score_column'] = 'final_score'
        
        logger.info(f"Generated summary stats: {summary}")
        return summary 