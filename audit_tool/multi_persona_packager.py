"""
Multi-Persona Packager for Brand Audit Tool

STATUS: ACTIVE

This module provides functionality to process and package audit data for multiple personas.
It serves as a critical integration component that:
1. Processes audit data for multiple personas in parallel
2. Aggregates and normalizes scores across different persona perspectives
3. Generates unified CSV and parquet files for dashboard consumption
4. Supports cross-persona comparison and analysis
5. Enables the Brand Health Command Center dashboard with multi-persona data

The packager ensures consistent data structure and format across different persona
evaluations, enabling meaningful comparison and aggregation of brand health metrics.
"""

import os
import re
import glob
import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .packager import AuditDataPackager as Packager

logger = logging.getLogger(__name__)

class MultiPersonaPackager:
    """Processes and packages audit data for multiple personas."""
    
    def __init__(self, base_dir: str = None):
        """
        Initialize with base directory containing persona-specific audit outputs.
        
        Args:
            base_dir: Base directory containing persona-specific audit outputs
        """
        self.base_dir = Path(base_dir) if base_dir else Path("audit_outputs")
        self.output_dir = Path("audit_data")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process_all_personas(self, max_workers: int = 4) -> Dict[str, Any]:
        """
        Process all persona directories in parallel.
        
        Args:
            max_workers: Maximum number of worker threads
            
        Returns:
            Dictionary of processing results
        """
        logger.info(f"Processing all personas in {self.base_dir}")
        
        # Find all persona directories
        persona_dirs = [d for d in self.base_dir.iterdir() if d.is_dir()]
        
        if not persona_dirs:
            logger.warning(f"No persona directories found in {self.base_dir}")
            return {"status": "error", "message": "No persona directories found"}
        
        results = {}
        
        # Process each persona directory in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_persona = {
                executor.submit(self._process_persona, persona_dir): persona_dir.name
                for persona_dir in persona_dirs
            }
            
            for future in as_completed(future_to_persona):
                persona_name = future_to_persona[future]
                try:
                    result = future.result()
                    results[persona_name] = result
                    logger.info(f"Processed persona: {persona_name}")
                except Exception as e:
                    logger.error(f"Error processing persona {persona_name}: {str(e)}")
                    results[persona_name] = {"status": "error", "message": str(e)}
        
        # Generate unified files
        self._generate_unified_files(results)
        
        return results
    
    def _process_persona(self, persona_dir: Path) -> Dict[str, Any]:
        """
        Process a single persona directory.
        
        Args:
            persona_dir: Path to the persona directory
            
        Returns:
            Dictionary of processing results
        """
        logger.info(f"Processing persona directory: {persona_dir}")
        
        try:
            # Create a packager for this persona
            packager = Packager(persona_dir.name)
            
            # Process the data
            result = packager.package_run()
            
            # Save persona-specific parquet files
            self._save_persona_parquet(persona_dir.name, result)
            
            return {
                "status": "success",
                "page_count": len(result.get("pages", [])),
                "criteria_count": len(result.get("criteria", [])),
                "experience_count": len(result.get("experience", [])),
                "recommendation_count": len(result.get("recommendations", []))
            }
            
        except Exception as e:
            logger.error(f"Error in _process_persona for {persona_dir}: {str(e)}")
            raise
    
    def _save_persona_parquet(self, persona_name: str, result: Dict[str, Any]) -> None:
        """
        Save persona-specific parquet files.
        
        Args:
            persona_name: Name of the persona
            result: Processing results
        """
        # Create persona-specific directory
        persona_dir = self.output_dir / persona_name
        os.makedirs(persona_dir, exist_ok=True)
        
        # Save each dataframe as parquet
        for key, data in result.items():
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                output_path = persona_dir / f"{key}.parquet"
                df.to_parquet(output_path, index=False)
                logger.info(f"Saved {key} parquet for {persona_name}: {len(df)} rows")
    
    def _generate_unified_files(self, results: Dict[str, Any]) -> None:
        """
        Generate unified CSV and parquet files from all persona data.
        
        Args:
            results: Dictionary of processing results by persona
        """
        logger.info("Generating unified files")
        
        # Initialize dataframes
        unified_audit_data = []
        unified_experience_data = []
        persona_comparison_data = []
        
        # Process each persona's data
        for persona_name, result in results.items():
            if result.get("status") != "success":
                logger.warning(f"Skipping {persona_name} due to processing error")
                continue
            
            try:
                # Load persona-specific parquet files
                persona_dir = self.output_dir / persona_name
                
                # Process pages and criteria
                if (persona_dir / "pages.parquet").exists() and (persona_dir / "criteria_scores.parquet").exists():
                    pages_df = pd.read_parquet(persona_dir / "pages.parquet")
                    criteria_df = pd.read_parquet(persona_dir / "criteria_scores.parquet")
                    
                    # Add persona column
                    pages_df["persona"] = persona_name
                    criteria_df["persona"] = persona_name
                    
                    # Add to unified audit data
                    unified_audit_data.append(criteria_df)
                    
                    # Add summary to persona comparison
                    persona_summary = {
                        "persona": persona_name,
                        "page_count": len(pages_df),
                        "average_score": pages_df["final_score"].mean() if "final_score" in pages_df.columns else 0,
                        "tier_1_score": pages_df[pages_df["tier"] == "tier_1"]["final_score"].mean() if "tier" in pages_df.columns else 0,
                        "tier_2_score": pages_df[pages_df["tier"] == "tier_2"]["final_score"].mean() if "tier" in pages_df.columns else 0,
                        "tier_3_score": pages_df[pages_df["tier"] == "tier_3"]["final_score"].mean() if "tier" in pages_df.columns else 0
                    }
                    persona_comparison_data.append(persona_summary)
                
                # Process experience data
                if (persona_dir / "experience.parquet").exists():
                    experience_df = pd.read_parquet(persona_dir / "experience.parquet")
                    experience_df["persona"] = persona_name
                    unified_experience_data.append(experience_df)
                
            except Exception as e:
                logger.error(f"Error processing unified files for {persona_name}: {str(e)}")
        
        # Combine and save unified audit data
        if unified_audit_data:
            unified_df = pd.concat(unified_audit_data, ignore_index=True)
            unified_df.to_parquet(self.output_dir / "unified_audit_data.parquet", index=False)
            unified_df.to_csv(self.output_dir / "unified_audit_data.csv", index=False)
            logger.info(f"Saved unified audit data: {len(unified_df)} rows")
        
        # Combine and save unified experience data
        if unified_experience_data:
            experience_df = pd.concat(unified_experience_data, ignore_index=True)
            experience_df.to_parquet(self.output_dir / "unified_experience_data.parquet", index=False)
            experience_df.to_csv(self.output_dir / "unified_experience_data.csv", index=False)
            logger.info(f"Saved unified experience data: {len(experience_df)} rows")
        
        # Save persona comparison data
        if persona_comparison_data:
            comparison_df = pd.DataFrame(persona_comparison_data)
            comparison_df.to_parquet(self.output_dir / "persona_comparison.parquet", index=False)
            comparison_df.to_csv(self.output_dir / "persona_comparison.csv", index=False)
            logger.info(f"Saved persona comparison data: {len(comparison_df)} rows")
    
    def generate_cross_persona_insights(self) -> Dict[str, Any]:
        """
        Generate insights by comparing data across personas.
        
        Returns:
            Dictionary of cross-persona insights
        """
        logger.info("Generating cross-persona insights")
        
        insights = {
            "agreement_areas": [],
            "disagreement_areas": [],
            "persona_biases": {},
            "url_variance": {}
        }
        
        try:
            # Load unified audit data
            audit_df = pd.read_parquet(self.output_dir / "unified_audit_data.parquet")
            
            # Calculate agreement and disagreement areas
            if "criterion_code" in audit_df.columns and "score" in audit_df.columns and "persona" in audit_df.columns:
                # Group by criterion and calculate variance across personas
                criterion_variance = audit_df.groupby("criterion_code")["score"].agg(["mean", "std"]).reset_index()
                
                # Identify agreement areas (low variance)
                agreement_areas = criterion_variance[criterion_variance["std"] < 1.0].sort_values("std")
                for _, row in agreement_areas.head(5).iterrows():
                    insights["agreement_areas"].append({
                        "criterion": row["criterion_code"],
                        "mean_score": row["mean"],
                        "std_dev": row["std"]
                    })
                
                # Identify disagreement areas (high variance)
                disagreement_areas = criterion_variance[criterion_variance["std"] >= 1.0].sort_values("std", ascending=False)
                for _, row in disagreement_areas.head(5).iterrows():
                    insights["disagreement_areas"].append({
                        "criterion": row["criterion_code"],
                        "mean_score": row["mean"],
                        "std_dev": row["std"]
                    })
                
                # Calculate persona biases
                persona_means = audit_df.groupby("persona")["score"].mean().to_dict()
                global_mean = audit_df["score"].mean()
                
                for persona, mean_score in persona_means.items():
                    bias = mean_score - global_mean
                    insights["persona_biases"][persona] = {
                        "mean_score": mean_score,
                        "bias": bias,
                        "tendency": "Positive" if bias > 0.5 else ("Negative" if bias < -0.5 else "Neutral")
                    }
                
                # Calculate URL variance if page_id exists
                if "page_id" in audit_df.columns:
                    url_variance = audit_df.groupby(["page_id", "persona"])["score"].mean().reset_index()
                    url_variance = url_variance.groupby("page_id")["score"].agg(["mean", "std"]).reset_index()
                    
                    # Get top 5 URLs with highest variance
                    high_variance_urls = url_variance.sort_values("std", ascending=False).head(5)
                    for _, row in high_variance_urls.iterrows():
                        insights["url_variance"][row["page_id"]] = {
                            "mean_score": row["mean"],
                            "std_dev": row["std"]
                        }
            
        except Exception as e:
            logger.error(f"Error generating cross-persona insights: {str(e)}")
        
        return insights
