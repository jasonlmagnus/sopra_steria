"""
This module contains the logic for generating the content of the reports.
"""
import logging
from .models import PageData, Methodology, Scorecard, ScoredCriterion, Tier, OffsiteChannel
from .ai_interface import AIInterface
import os
import glob
from .models import SummaryReport, AggregatedTierScore, RankedPage, AggregatedOffsiteScore
import re
import json
from typing import List

def _extract_json_from_response(text: str) -> str:
    """Finds and extracts a JSON object from a string that might have surrounding text."""
    # Look for a JSON object between ```json and ```
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    # Fallback to looking for the first { and last }
    match = re.search(r"(\{.*?\})", text, re.DOTALL)
    if match:
        return match.group(1)
    return text # Return original text if no JSON object is found

class NarrativeGenerator:
    """
    Generates the Persona Experience Report.
    """
    def __init__(self, ai_interface: AIInterface):
        self.ai_interface = ai_interface

    def create_report(self, persona_content: str, page_data: PageData) -> str:
        """
        Calls the AI to generate a narrative report.
        """
        logging.info("Generating narrative report...")
        narrative = self.ai_interface.generate_narrative(
            persona_content,
            page_data.raw_text
        )
        logging.info("...report generation complete.")
        return narrative

class ScorecardGenerator:
    """
    Generates a Brand Hygiene Scorecard based on scraped data and methodology.
    """
    def __init__(self, methodology: Methodology, ai_interface: AIInterface):
        self.methodology = methodology
        self.ai_interface = ai_interface

    def _is_offsite(self, url: str) -> bool:
        """Determines if a URL is an offsite property."""
        # Simple check: if it's not a soprasteria domain, it's offsite.
        return "soprasteria" not in url.lower()

    def classify_tier(self, page_data: PageData) -> Tier:
        """
        Classifies an ONSITE page into a Tier based on URL patterns and content.
        """
        findings = page_data.objective_findings
        url = page_data.url

        # Tier 1 Check: Based on tagline in h1 or specific nav links
        tagline = "the world is how we shape it"
        if tagline in findings.get("h1_text", "").lower():
            return next((t for t in self.methodology.tiers if "TIER 1" in t.name), self.methodology.tiers[0])
        
        tier1_nav_keywords = ["about", "investors", "careers"]
        if any(keyword in ' '.join(findings.get("nav_links", [])).lower() for keyword in tier1_nav_keywords):
             return next((t for t in self.methodology.tiers if "TIER 1" in t.name), self.methodology.tiers[0])

        # Tier 2 Check: Based on URL path
        tier2_url_patterns = ["/services/", "/industries/", "/transformation/", "/what-we-do/"]
        if any(pattern in url for pattern in tier2_url_patterns):
            return next((t for t in self.methodology.tiers if "TIER 2" in t.name), self.methodology.tiers[1])

        # Tier 3 Check: Based on URL path
        tier3_url_patterns = ["/blog", "/newsroom", "/case-study", "/white-paper", "/press-release", "/event"]
        if any(pattern in url for pattern in tier3_url_patterns):
            return next((t for t in self.methodology.tiers if "TIER 3" in t.name), self.methodology.tiers[2])
        
        logging.info("No specific onsite tier pattern matched. Defaulting to Tier 1.")
        return next((t for t in self.methodology.tiers if "TIER 1" in t.name), self.methodology.tiers[0])

    def classify_offsite_channel(self, url: str) -> OffsiteChannel:
        """
        Classifies an OFFSITE page into a channel based on URL.
        """
        url_lower = url.lower()
        
        # Owned: Social media profiles the company runs
        owned_keywords = ["linkedin.com/company", "twitter.com", "youtube.com", "facebook.com"]
        if any(keyword in url_lower for keyword in owned_keywords):
            return next((c for c in self.methodology.offsite_channels if "Owned" in c.name), self.methodology.offsite_channels[0])

        # Influenced: Review sites, employee content
        influenced_keywords = ["glassdoor.com", "linkedin.com/in/"] # Employee profile
        if any(keyword in url_lower for keyword in influenced_keywords):
            return next((c for c in self.methodology.offsite_channels if "Influenced" in c.name), self.methodology.offsite_channels[1])
            
        # Independent: News, review sites, directories
        # This will be the default for anything not matching the others.
        return next((c for c in self.methodology.offsite_channels if "Independent" in c.name), self.methodology.offsite_channels[2])

    def create_scorecard(self, page_data: PageData) -> Scorecard:
        """
        Creates the full scorecard by classifying, scoring, and assembling the data.
        Handles both Onsite and Offsite pages.
        """
        logging.info("Generating brand hygiene scorecard...")
        
        if self._is_offsite(page_data.url):
            active_class = self.classify_offsite_channel(page_data.url)
            logging.info(f"Page classified as Offsite: {active_class.name}")
        else:
            active_class = self.classify_tier(page_data)
            logging.info(f"Page classified as Onsite: {active_class.name}")
        
        scored_criteria = []
        total_score = 0.0

        OBJECTIVE_CRITERIA = ["Corporate Positioning Alignment"]

        for criterion in active_class.criteria:
            score = 5.0  # Default score
            notes = "Default score assigned."

            # Simple objective check for tagline presence (can be expanded)
            if "Corporate Positioning Alignment" in criterion.name:
                if not self._is_offsite(page_data.url):
                    if page_data.objective_findings.get("has_tagline", False):
                        score = 8.0
                        notes = "Tagline present."
                    else:
                        score = 3.0
                        notes = "Gated to 3.0 for missing corporate tagline."
                else:
                    # AI must score this for offsite as it's about alignment, not presence.
                    score = self.ai_interface.get_subjective_score(
                        criterion_name=criterion.name, page_text=page_data.raw_text
                    )
                    notes = "Scored by AI."
            else:
                # All other criteria are subjectively scored by the AI for now
                score = self.ai_interface.get_subjective_score(
                    criterion_name=criterion.name,
                    page_text=page_data.raw_text
                )
                notes = "Scored by AI."
            
            scored_criteria.append(
                ScoredCriterion(
                    name=criterion.name,
                    weight=criterion.weight,
                    score=score,
                    notes=notes
                )
            )
            total_score += score * criterion.weight

        return Scorecard(
            url=page_data.url,
            final_score=total_score,
            tier_name=active_class.name,
            scored_criteria=scored_criteria
        )

class SummaryGenerator:
    """
    Generates a strategic summary report by aggregating data from all
    individual audit reports for a given persona.
    """
    def __init__(self, persona_name: str, ai_interface: AIInterface, methodology: Methodology):
        self.persona_name = persona_name
        self.ai_interface = ai_interface
        self.methodology = methodology
        # Sanitize persona_name to create a valid directory name
        safe_persona_name = os.path.basename(persona_name).replace('.md', '')
        self.output_dir = os.path.join("audit_outputs", safe_persona_name)

    def _parse_scorecards(self) -> dict:
        """
        Parses all scorecard markdown files in the output directory to
        aggregate quantitative data.
        """
        logging.info(f"Parsing scorecards from: {self.output_dir}")
        scorecard_files = glob.glob(os.path.join(self.output_dir, "*_hygiene_scorecard.md"))
        
        if not scorecard_files:
            logging.warning("No scorecard files found to generate a summary.")
            return {"all_pages": []}

        all_pages = []
        for filepath in scorecard_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # More robust parsing
                    url_match = re.search(r"\*\*URL:\*\*\s*(https?://[^\s]+)", content)
                    score_match = re.search(r"\*\*Final Score:\*\*\s*([\d.]+)/10", content)
                    tier_match = re.search(r"\*\*Tier/Channel:\*\*\s*(.+)", content)

                    if url_match and score_match and tier_match:
                        all_pages.append({
                            "url": url_match.group(1).strip(),
                            "score": float(score_match.group(1)),
                            "tier_name": tier_match.group(1).strip()
                        })
                    else:
                        logging.warning(f"Could not parse all required fields from {filepath}")
                        if not url_match: logging.debug("URL not found in scorecard.")
                        if not score_match: logging.debug("Score not found in scorecard.")
                        if not tier_match: logging.debug("Tier/Channel not found in scorecard.")

            except Exception as e:
                logging.error(f"Error parsing scorecard file {filepath}: {e}")
        
        logging.info(f"Successfully parsed {len(all_pages)} scorecards.")
        return {"all_pages": all_pages}

    def _synthesize_narratives(self) -> dict:
        """Parses all experience reports and uses AI to find themes."""
        logging.info(f"Synthesizing narrative reports from: {self.output_dir}")
        experience_reports = glob.glob(os.path.join(self.output_dir, "*_experience_report.md"))

        if not experience_reports:
            logging.warning("No experience reports found to synthesize.")
            return {"executive_summary": "No qualitative data found.", "key_strengths": [], "key_weaknesses": []}

        all_narratives = []
        for report_path in experience_reports:
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    # Add a separator to distinguish between reports
                    all_narratives.append(f"--- START OF REPORT: {os.path.basename(report_path)} ---\n\n{f.read()}")
            except Exception as e:
                logging.error(f"Error reading experience report file {report_path}: {e}")

        combined_narratives = "\n\n--- END OF REPORT ---\n\n".join(all_narratives)

        logging.info(f"Passing {len(experience_reports)} concatenated reports to AI for synthesis.")
        summary_json = self.ai_interface.generate_strategic_summary(combined_narratives)
        
        cleaned_json = _extract_json_from_response(summary_json)
        
        try:
            return json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON after cleaning: {e}")
            logging.error(f"Cleaned JSON content was: {cleaned_json}")
            # Return a structured error to avoid crashing the whole process
            return {
                "executive_summary": "FATAL: Could not parse summary from AI.",
                "key_strengths": [f"Error: {e}"],
                "key_weaknesses": [f"Content: {summary_json[:500]}..."]
            }

    def create_summary(self) -> SummaryReport:
        """
        Orchestrates the creation of the summary report.
        """
        logging.info(f"Starting summary generation for persona: {self.persona_name}")

        quant_data = self._parse_scorecards()
        qual_insights = self._synthesize_narratives()

        all_pages = quant_data.get("all_pages", [])
        
        if not all_pages:
            logging.warning("Cannot generate summary report, no pages were parsed.")
            return SummaryReport(
                persona_name=self.persona_name,
                overall_score=0, onsite_score=0, offsite_score=0, tier_scores=[],
                offsite_scores=[],
                top_performing_pages=[], bottom_performing_pages=[], 
                executive_summary="No data found to generate summary.",
                key_strengths=[], key_weaknesses=[]
            )

        onsite_pages = [p for p in all_pages if not self._is_offsite_tier_name(p["tier_name"])]
        offsite_pages = [p for p in all_pages if self._is_offsite_tier_name(p["tier_name"])]

        # --- Onsite Scoring ---
        onsite_score = self._calculate_weighted_onsite_score(onsite_pages)
        aggregated_tier_scores = self._get_aggregated_tier_scores(onsite_pages)
        
        # --- Offsite Scoring ---
        offsite_score = self._calculate_weighted_offsite_score(offsite_pages)
        aggregated_offsite_scores = self._get_aggregated_offsite_scores(offsite_pages)

        # --- Final Score ---
        overall_score = (onsite_score * 0.7) + (offsite_score * 0.3)

        all_pages_sorted = sorted(all_pages, key=lambda p: p["score"], reverse=True)
        top_pages = [RankedPage(url=p["url"], score=p["score"]) for p in all_pages_sorted[:3]]
        bottom_pages = [RankedPage(url=p["url"], score=p["score"]) for p in reversed(all_pages_sorted[-3:])]

        return SummaryReport(
            persona_name=self.persona_name,
            overall_score=overall_score,
            onsite_score=onsite_score,
            offsite_score=offsite_score,
            tier_scores=aggregated_tier_scores,
            offsite_scores=aggregated_offsite_scores,
            top_performing_pages=top_pages,
            bottom_performing_pages=bottom_pages,
            executive_summary=qual_insights.get("executive_summary", ""),
            key_strengths=qual_insights.get("key_strengths", []),
            key_weaknesses=qual_insights.get("key_weaknesses", [])
        )
    
    def _is_offsite_tier_name(self, tier_name: str) -> bool:
        """Checks if a tier name corresponds to an offsite channel."""
        offsite_keywords = ["Owned", "Influenced", "Independent"]
        return any(keyword in tier_name for keyword in offsite_keywords)

    def _get_aggregated_tier_scores(self, onsite_pages: list) -> List[AggregatedTierScore]:
        tier_scores_map = {}
        for page in onsite_pages:
            tier_name = page["tier_name"]
            if tier_name not in tier_scores_map:
                tier_scores_map[tier_name] = []
            tier_scores_map[tier_name].append(page["score"])
        
        aggregated_tier_scores = []
        for tier_name, scores in tier_scores_map.items():
            aggregated_tier_scores.append(AggregatedTierScore(
                tier_name=tier_name,
                average_score=sum(scores) / len(scores) if scores else 0,
                page_count=len(scores)
            ))
        return aggregated_tier_scores

    def _get_aggregated_offsite_scores(self, offsite_pages: list) -> List[AggregatedOffsiteScore]:
        offsite_scores_map = {}
        for page in offsite_pages:
            tier_name = page["tier_name"] # e.g. "Owned Channels"
            if tier_name not in offsite_scores_map:
                offsite_scores_map[tier_name] = []
            offsite_scores_map[tier_name].append(page["score"])

        aggregated_offsite_scores = []
        for channel_name, scores in offsite_scores_map.items():
            aggregated_offsite_scores.append(AggregatedOffsiteScore(
                channel_name=channel_name,
                average_score=sum(scores) / len(scores) if scores else 0,
                page_count=len(scores)
            ))
        return aggregated_offsite_scores

    def _calculate_weighted_onsite_score(self, onsite_pages: list) -> float:
        """Calculates the final weighted score for all onsite pages."""
        aggregated_scores = self._get_aggregated_tier_scores(onsite_pages)
        total_onsite_score = 0.0
        
        for tier_data in aggregated_scores:
            # Find the corresponding tier in the methodology to get its weight
            methodology_tier = next((t for t in self.methodology.tiers if t.name == tier_data.tier_name), None)
            if methodology_tier:
                total_onsite_score += tier_data.average_score * methodology_tier.weight
            else:
                logging.warning(f"Could not find weight for tier: {tier_data.tier_name}")

        return total_onsite_score

    def _calculate_weighted_offsite_score(self, offsite_pages: list) -> float:
        """Calculates the final weighted score for all offsite pages."""
        aggregated_scores = self._get_aggregated_offsite_scores(offsite_pages)
        total_offsite_score = 0.0

        for channel_data in aggregated_scores:
            methodology_channel = next((c for c in self.methodology.offsite_channels if c.name == channel_data.channel_name), None)
            if methodology_channel:
                total_offsite_score += channel_data.average_score * methodology_channel.weight
            else:
                logging.warning(f"Could not find weight for offsite channel: {channel_data.channel_name}")
        
        return total_offsite_score 