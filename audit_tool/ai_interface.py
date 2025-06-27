"""
AI Interface for Brand Audit Tool

STATUS: ACTIVE

This module provides a unified interface to AI services that:
1. Connects to various AI providers (OpenAI, Anthropic, etc.)
2. Generates hygiene scorecards with brand evaluation criteria
3. Creates persona-specific experience reports
4. Produces strategic summaries and recommendations
5. Handles prompt engineering and response parsing

The interface abstracts away the complexities of working with different
AI providers, ensuring consistent outputs regardless of the underlying model.
"""

import os
import re
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .methodology_parser import MethodologyParser

logger = logging.getLogger(__name__)

class AIInterface:
    """Interface for AI services used in brand audits."""
    
    def __init__(self, model_provider: str = "openai"):
        """
        Initialize with model provider.
        
        Args:
            model_provider: The AI provider to use ("anthropic" or "openai")
        """
        self.model_provider = model_provider
        
        # Load API keys from environment
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        # Set default models
        self.anthropic_model = "claude-3-opus-20240229"
        self.openai_model = "gpt-4-turbo"
        
        # Validate API keys
        if model_provider == "anthropic" and not self.anthropic_api_key:
            logger.warning("Anthropic API key not found in environment variables")
        elif model_provider == "openai" and not self.openai_api_key:
            logger.warning("OpenAI API key not found in environment variables")

    def _load_prompt_template(self, name: str) -> str:
        """Load a prompt template from the templates directory."""
        templates_dir = Path(__file__).parent / "templates"
        for ext in [".md", ".j2", ".txt"]:
            path = templates_dir / f"{name}{ext}"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        raise FileNotFoundError(f"Prompt template not found: {name}")

    def _get_system_message(self, name: str) -> str:
        """Return a default system prompt for a template name."""
        defaults = {
            "narrative_analysis": "You are a brand audit expert analyzing narrative quality and brand alignment.",
            "scorecard": "You are a brand audit expert analyzing digital content.",
        }
        return defaults.get(name, "You are a brand audit expert analyzing digital content.")
    
    def generate_hygiene_scorecard(self, url: str, page_content: str, persona_content: str, methodology: MethodologyParser) -> str:
        """
        Generate a hygiene scorecard for a URL.
        
        Args:
            url: The URL to evaluate
            page_content: The content of the page
            persona_content: The persona markdown content
            methodology: The methodology parser instance
            
        Returns:
            Markdown formatted hygiene scorecard
        """
        logger.info(f"Generating hygiene scorecard for {url}")
        
        # Get tier information
        tier_name, tier_config = methodology.classify_url(url)
        
        # Get criteria for this tier
        criteria = methodology.get_criteria_for_tier(tier_name)
        
        # Construct prompt
        prompt = self._construct_hygiene_prompt(
            url=url,
            page_content=page_content,
            persona_content=persona_content,
            tier_name=tier_name,
            tier_config=tier_config,
            criteria=criteria
        )
        
        # Generate response
        response = self._generate_ai_response(prompt)
        
        return response
    
    def generate_experience_report(self, url: str, page_content: str, persona_content: str, methodology: MethodologyParser) -> str:
        """
        Generate an experience report for a URL.
        
        Args:
            url: The URL to evaluate
            page_content: The content of the page
            persona_content: The persona markdown content
            methodology: The methodology parser instance
            
        Returns:
            Markdown formatted experience report
        """
        logger.info(f"Generating experience report for {url}")
        
        # Get tier information
        tier_name, tier_config = methodology.classify_url(url)
        
        # Construct prompt
        prompt = self._construct_experience_prompt(
            url=url,
            page_content=page_content,
            persona_content=persona_content,
            tier_name=tier_name,
            tier_config=tier_config
        )
        
        # Generate response
        response = self._generate_ai_response(prompt)
        
        return response
    
    def generate_strategic_summary(self, persona_name: str, scorecard_data: List[Dict], methodology: MethodologyParser) -> str:
        """
        Generate a strategic summary from scorecard data.
        
        Args:
            persona_name: The name of the persona
            scorecard_data: List of scorecard data dictionaries
            methodology: The methodology parser instance
            
        Returns:
            Markdown formatted strategic summary
        """
        logger.info(f"Generating strategic summary for {persona_name}")
        
        # Construct prompt
        prompt = self._construct_summary_prompt(
            persona_name=persona_name,
            scorecard_data=scorecard_data,
            methodology=methodology
        )
        
        # Generate response
        response = self._generate_ai_response(prompt)
        
        return response
    
    def _construct_hygiene_prompt(self, url: str, page_content: str, persona_content: str, 
                                 tier_name: str, tier_config: Dict[str, Any], 
                                 criteria: List[Dict[str, Any]]) -> str:
        """
        Construct the prompt for hygiene scorecard generation.
        
        Args:
            url: The URL to evaluate
            page_content: The content of the page
            persona_content: The persona markdown content
            tier_name: The tier name
            tier_config: The tier configuration
            criteria: The criteria for this tier
            
        Returns:
            Formatted prompt
        """
        # Format criteria for prompt
        criteria_text = ""
        for criterion in criteria:
            criteria_text += f"- {criterion['name']}: {criterion['description']}\n"
        
        # Construct prompt
        prompt = f"""
You are a brand audit expert evaluating digital content for Sopra Steria.

# URL
{url}

# Page Content
{page_content[:10000]}  # Truncate to avoid token limits

# Persona
{persona_content}

# Tier Classification
This URL is classified as: {tier_config.get('name', tier_name.upper())}

# Evaluation Criteria
{criteria_text}

# Task
Generate a detailed brand hygiene scorecard for this URL from the perspective of the persona.
For each criterion, provide:
1. A score from 0-10 (where 10 is excellent)
2. Specific evidence from the page content that justifies the score
3. Brief explanation of how well the content meets the criterion for this persona

Then provide an overall score and 3-5 specific recommendations for improvement.

Format your response as a markdown document with the following sections:
1. Title: "Brand Hygiene Scorecard for [Persona Name]"
2. URL section
3. Introduction
4. Criteria Scores (in a table with columns for Criterion, Score, and Evidence)
5. Overall Assessment with Final Score
6. Recommendations (numbered list)

Be specific, objective, and focus on how well the content meets the needs of the persona.
"""
        
        return prompt
    
    def _construct_experience_prompt(self, url: str, page_content: str, persona_content: str,
                                    tier_name: str, tier_config: Dict[str, Any]) -> str:
        """
        Construct the prompt for experience report generation.
        
        Args:
            url: The URL to evaluate
            page_content: The content of the page
            persona_content: The persona markdown content
            tier_name: The tier name
            tier_config: The tier configuration
            
        Returns:
            Formatted prompt
        """
        # Construct prompt
        prompt = f"""
You are a brand experience analyst evaluating digital content for Sopra Steria.

# URL
{url}

# Page Content
{page_content[:10000]}  # Truncate to avoid token limits

# Persona
{persona_content}

# Tier Classification
This URL is classified as: {tier_config.get('name', tier_name.upper())}

# Task
Generate a detailed brand experience report for this URL from the perspective of the persona.
Analyze how the content would be experienced by this specific persona, considering:

1. First Impressions: What would the persona notice first? How would they feel?
2. Content Relevance: How relevant is the content to the persona's needs and priorities?
3. Brand Perception: How would this content affect the persona's perception of the Sopra Steria brand?
4. Journey Analysis: What would be the persona's likely path through this content? Where might they get stuck or confused?
5. Emotional Response: What emotions would the content evoke in this persona?

Then provide:
1. Overall sentiment (Positive, Neutral, or Negative)
2. Engagement level (High, Medium, or Low)
3. Conversion likelihood (High, Medium, or Low)
4. 3-5 specific recommendations for improving the experience for this persona

Format your response as a markdown document with the following sections:
1. Title: "Brand Experience Report for [Persona Name]"
2. URL section
3. Introduction
4. Analysis sections (First Impressions, Content Relevance, Brand Perception, Journey Analysis, Emotional Response)
5. Experience Metrics (Sentiment, Engagement, Conversion)
6. Recommendations (numbered list)

Be specific, empathetic, and focus on the persona's likely experience with this content.
"""
        
        return prompt
    
    def _construct_summary_prompt(self, persona_name: str, scorecard_data: List[Dict], 
                                 methodology: MethodologyParser) -> str:
        """
        Construct the prompt for strategic summary generation.
        
        Args:
            persona_name: The name of the persona
            scorecard_data: List of scorecard data dictionaries
            methodology: The methodology parser instance
            
        Returns:
            Formatted prompt
        """
        # Format scorecard data for prompt
        data_text = json.dumps(scorecard_data, indent=2)
        
        # Construct prompt
        prompt = f"""
You are a strategic brand consultant analyzing audit data for Sopra Steria.

# Persona
{persona_name}

# Audit Data
{data_text[:15000]}  # Truncate to avoid token limits

# Task
Generate a strategic summary of the brand audit results for this persona.
Analyze the data to identify:

1. Overall brand health score and what it means
2. Key strengths and weaknesses across the digital estate
3. Patterns and trends in the data
4. Strategic implications for the brand
5. Prioritized recommendations for improvement

Format your response as a markdown document with the following sections:
1. Title: "Strategic Brand Audit Summary for [Persona Name]"
2. Executive Summary (1-2 paragraphs)
3. Key Findings (bullet points)
4. Strengths (bullet points)
5. Weaknesses (bullet points)
6. Strategic Recommendations (numbered list with bold headings)
7. Next Steps (numbered list)

Be strategic, insightful, and focus on actionable recommendations that will improve the brand experience for this persona.
"""
        
        return prompt
    
    def _generate_ai_response(self, prompt: str) -> str:
        """
        Generate a response from the AI model.
        
        Args:
            prompt: The prompt to send to the AI
            
        Returns:
            The AI's response
        """
        if self.model_provider == "anthropic":
            return self._generate_anthropic_response(prompt)
        elif self.model_provider == "openai":
            return self._generate_openai_response(prompt)
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def _generate_anthropic_response(self, prompt: str) -> str:
        """
        Generate a response from Anthropic's Claude.
        
        Args:
            prompt: The prompt to send to Claude
            
        Returns:
            Claude's response
        """
        if not self.anthropic_api_key:
            logger.warning("Anthropic API key not found, using dummy response")
            return "[DUMMY ANTHROPIC RESPONSE]"
        
        try:
            headers = {
                "x-api-key": self.anthropic_api_key,
                "content-type": "application/json"
            }
            
            data = {
                "model": self.anthropic_model,
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": 4000,
                "temperature": 0.2
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/complete",
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result.get("completion", "")
            
        except Exception as e:
            logger.error(f"Error generating Anthropic response: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def _generate_openai_response(self, prompt: str) -> str:
        """
        Generate a response from OpenAI's GPT.
        
        Args:
            prompt: The prompt to send to GPT
            
        Returns:
            GPT's response
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found, using dummy response")
            return "[DUMMY OPENAI RESPONSE]"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.openai_model,
                "messages": [
                    {"role": "system", "content": "You are a brand audit expert analyzing digital content."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.2
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            return f"Error generating response: {str(e)}"
