import os
import re
import json
from typing import Dict, List, Any, Optional
import pandas as pd

class JourneyAnalysisProcessor:
    """
    Processes P1 journey analysis markdown files and integrates them with dashboard data
    """
    
    def __init__(self, p1_directory: str = "audit outputs/P1"):
        self.p1_directory = p1_directory
        self.journey_data = {}
        self.stage_mapping = {
            "stage1": {
                "name": "Discovery & Initial Awareness",
                "categories": ["Main Website", "Industries", "Public & EU Organisations"],
                "icon": "🔍",
                "description": "Government executives discover Sopra Steria through regulatory compliance searches"
            },
            "stage2": {
                "name": "Industry & Solution Exploration", 
                "categories": ["Services", "Solutions", "Cybersecurity"],
                "icon": "🛍️",
                "description": "Executives explore service categories and solution portfolios"
            },
            "stage3": {
                "name": "Deep Solution Research",
                "categories": ["Case Studies", "Whitepapers", "Technical Documentation"],
                "icon": "🔬", 
                "description": "Detailed technical validation and compliance assessment"
            },
            "stage4": {
                "name": "Content & Insight Consumption",
                "categories": ["Newsroom", "Insights", "Thought Leadership"],
                "icon": "📰",
                "description": "Thought leadership content assessment and expert credibility evaluation"
            },
            "stage5": {
                "name": "Decision & Contact Consideration",
                "categories": ["Contact", "About Us", "Careers"],
                "icon": "📞",
                "description": "Contact and engagement options assessment for procurement"
            }
        }
        
    def load_journey_data(self) -> Dict[str, Any]:
        """Load and parse all P1 journey analysis files"""
        if not os.path.exists(self.p1_directory):
            print(f"Warning: P1 directory not found at {self.p1_directory}")
            return {}
            
        journey_files = {
            "overview": "P1_Understanding the Persona Research Report.md",
            "stage1": "stage1_analysis.md", 
            "stage2": "stage2_anaysis.md",  # Note: keeping original typo in filename
            "stage3": "stage3_analysis.md",
            "stage4": "stage4_analysis.md",
            "stage5": "stage5_analysis.md",
            "brand_analysis": "brand_application_findings.md"
        }
        
        for key, filename in journey_files.items():
            filepath = os.path.join(self.p1_directory, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.journey_data[key] = self._parse_markdown_content(content, key)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    
        return self.journey_data
    
    def _parse_markdown_content(self, content: str, stage_key: str) -> Dict[str, Any]:
        """Parse markdown content and extract structured insights"""
        parsed = {
            "raw_content": content,
            "cognitive_insights": [],
            "emotional_insights": [],
            "behavioral_insights": [],
            "pain_points": [],
            "recommendations": [],
            "key_quotes": []
        }
        
        # Extract sections based on markdown headers
        sections = self._extract_sections(content)
        
        # Parse cognitive analysis
        cognitive_section = self._find_section(sections, ["cognitive", "thinking"])
        if cognitive_section:
            parsed["cognitive_insights"] = self._extract_insights(cognitive_section)
            
        # Parse emotional analysis  
        emotional_section = self._find_section(sections, ["emotional", "feels"])
        if emotional_section:
            parsed["emotional_insights"] = self._extract_insights(emotional_section)
            
        # Parse behavioral analysis
        behavioral_section = self._find_section(sections, ["behavioral", "sees"])
        if behavioral_section:
            parsed["behavioral_insights"] = self._extract_insights(behavioral_section)
            
        # Extract pain points
        pain_points = self._extract_pain_points(content)
        parsed["pain_points"] = pain_points
        
        # Extract recommendations
        recommendations = self._extract_recommendations(content)
        parsed["recommendations"] = recommendations
        
        # Extract key quotes
        quotes = self._extract_quotes(content)
        parsed["key_quotes"] = quotes
        
        return parsed
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections based on markdown headers"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('#'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip('#').strip().lower()
                current_content = []
            else:
                current_content.append(line)
                
        if current_section:
            sections[current_section] = '\n'.join(current_content)
            
        return sections
    
    def _find_section(self, sections: Dict[str, str], keywords: List[str]) -> Optional[str]:
        """Find section containing any of the keywords"""
        for section_name, content in sections.items():
            if any(keyword in section_name for keyword in keywords):
                return content
        return None
    
    def _extract_insights(self, content: str) -> List[str]:
        """Extract bullet points and insights from content"""
        insights = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                insight = line.lstrip('-*•').strip()
                if len(insight) > 10:  # Filter out very short items
                    insights.append(insight)
        return insights
    
    def _extract_pain_points(self, content: str) -> List[Dict[str, str]]:
        """Extract pain points with context"""
        pain_points = []
        
        # Look for pain point indicators
        pain_indicators = [
            "pain point", "issue", "problem", "gap", "missing", "limited", 
            "insufficient", "unclear", "generic", "concern", "barrier"
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in pain_indicators):
                pain_point = {
                    "issue": line.strip(),
                    "context": self._get_context(lines, i, 2)
                }
                pain_points.append(pain_point)
                
        return pain_points[:10]  # Limit to top 10
    
    def _extract_recommendations(self, content: str) -> List[Dict[str, str]]:
        """Extract recommendations with priority"""
        recommendations = []
        
        # Look for recommendation sections
        rec_patterns = [
            r"recommendation[s]?:?\s*(.+)",
            r"should\s+(.+)",
            r"need[s]?\s+to\s+(.+)",
            r"implement\s+(.+)",
            r"create\s+(.+)",
            r"develop\s+(.+)"
        ]
        
        for line in content.split('\n'):
            for pattern in rec_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    rec_text = match.group(1).strip()
                    if len(rec_text) > 15:
                        priority = self._determine_priority(line)
                        recommendations.append({
                            "recommendation": rec_text,
                            "priority": priority,
                            "context": line.strip()
                        })
                        
        return recommendations[:15]  # Limit to top 15
    
    def _extract_quotes(self, content: str) -> List[str]:
        """Extract key quotes from the content"""
        quotes = []
        
        # Look for quoted text
        quote_patterns = [
            r'"([^"]+)"',
            r'"([^"]+)"',
            r"'([^']+)'"
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 20 and len(match) < 200:  # Reasonable quote length
                    quotes.append(match)
                    
        return quotes[:10]  # Limit to top 10
    
    def _get_context(self, lines: List[str], index: int, context_size: int = 2) -> str:
        """Get surrounding context for a line"""
        start = max(0, index - context_size)
        end = min(len(lines), index + context_size + 1)
        return ' '.join(lines[start:end]).strip()
    
    def _determine_priority(self, text: str) -> str:
        """Determine priority based on text content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["critical", "urgent", "immediate", "must"]):
            return "High"
        elif any(word in text_lower for word in ["important", "should", "need"]):
            return "Medium"
        else:
            return "Low"
    
    def get_stage_insights(self, stage_number: int) -> Dict[str, Any]:
        """Get insights for a specific journey stage"""
        stage_key = f"stage{stage_number}"
        
        if stage_key not in self.journey_data:
            return {}
            
        stage_data = self.journey_data[stage_key].copy()
        stage_data.update(self.stage_mapping.get(stage_key, {}))
        
        return stage_data
    
    def get_journey_overview(self) -> Dict[str, Any]:
        """Get complete journey overview"""
        overview = {
            "persona": "BENELUX Public Sector IT Executive",
            "journey_stages": [],
            "key_findings": [],
            "overall_recommendations": []
        }
        
        # Compile insights from all stages
        for i in range(1, 6):
            stage_insights = self.get_stage_insights(i)
            if stage_insights:
                overview["journey_stages"].append({
                    "stage": i,
                    "name": stage_insights.get("name", f"Stage {i}"),
                    "icon": stage_insights.get("icon", "📍"),
                    "pain_points_count": len(stage_insights.get("pain_points", [])),
                    "recommendations_count": len(stage_insights.get("recommendations", []))
                })
        
        # Extract key findings from overview document
        if "overview" in self.journey_data:
            overview_content = self.journey_data["overview"]["raw_content"]
            overview["key_findings"] = self._extract_key_findings(overview_content)
            
        return overview
    
    def _extract_key_findings(self, content: str) -> List[str]:
        """Extract key findings from overview content"""
        findings = []
        
        # Look for findings sections
        sections = content.split('\n')
        in_findings = False
        
        for line in sections:
            line = line.strip()
            if "key findings" in line.lower() or "findings" in line.lower():
                in_findings = True
                continue
            elif line.startswith('#') and in_findings:
                break
            elif in_findings and (line.startswith('-') or line.startswith('*')):
                finding = line.lstrip('-*').strip()
                if len(finding) > 20:
                    findings.append(finding)
                    
        return findings[:8]  # Limit to top 8
    
    def link_to_dashboard_data(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Link journey insights to dashboard performance data"""
        linked_data = {
            "journey_performance": {},
            "stage_category_mapping": {},
            "enhanced_insights": []
        }
        
        # Map journey stages to dashboard categories
        for stage_key, stage_info in self.stage_mapping.items():
            stage_num = int(stage_key.replace('stage', ''))
            categories = stage_info["categories"]
            
            # Find matching dashboard data for these categories
            stage_performance = {
                "stage": stage_num,
                "name": stage_info["name"],
                "categories": [],
                "avg_score": 0,
                "journey_insights": self.get_stage_insights(stage_num)
            }
            
            total_score = 0
            category_count = 0
            
            for category in categories:
                # This would link to actual dashboard data
                # For now, we'll create placeholder structure
                category_data = {
                    "category": category,
                    "score": 1.8,  # Placeholder - would come from dashboard_data
                    "journey_context": f"Stage {stage_num} context for {category}"
                }
                stage_performance["categories"].append(category_data)
                total_score += category_data["score"]
                category_count += 1
                
            if category_count > 0:
                stage_performance["avg_score"] = total_score / category_count
                
            linked_data["journey_performance"][stage_key] = stage_performance
            
        return linked_data
    
    def export_journey_data(self, output_file: str = "journey_analysis.json"):
        """Export processed journey data to JSON"""
        export_data = {
            "journey_overview": self.get_journey_overview(),
            "stage_insights": {},
            "processing_metadata": {
                "source_directory": self.p1_directory,
                "stages_processed": len([k for k in self.journey_data.keys() if k.startswith('stage')]),
                "total_pain_points": sum(len(data.get("pain_points", [])) for data in self.journey_data.values()),
                "total_recommendations": sum(len(data.get("recommendations", [])) for data in self.journey_data.values())
            }
        }
        
        # Add individual stage insights
        for i in range(1, 6):
            stage_insights = self.get_stage_insights(i)
            if stage_insights:
                export_data["stage_insights"][f"stage_{i}"] = stage_insights
                
        # Write to file
        output_path = os.path.join("dashboard", output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        print(f"Journey analysis exported to {output_path}")
        return export_data

# Usage example
if __name__ == "__main__":
    processor = JourneyAnalysisProcessor()
    journey_data = processor.load_journey_data()
    
    if journey_data:
        print("Journey data loaded successfully!")
        print(f"Stages processed: {len([k for k in journey_data.keys() if k.startswith('stage')])}")
        
        # Export for dashboard use
        exported_data = processor.export_journey_data()
        print(f"Exported {len(exported_data['stage_insights'])} stages")
    else:
        print("No journey data found. Please ensure P1 directory exists with markdown files.") 