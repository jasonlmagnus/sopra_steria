"""
This module handles all interactions with third-party AI APIs.
"""
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from .models import PageData
from .persona_parser import PersonaParser
from .methodology_parser import MethodologyParser
import json

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    print("Anthropic package not found. Install with: pip install anthropic")
    ANTHROPIC_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    print("OpenAI package not found. Install with: pip install openai")
    OPENAI_AVAILABLE = False

load_dotenv()

class AIInterface:
    """A class to handle interactions with AI APIs (Anthropic Claude and OpenAI GPT)."""

    def __init__(self, model_provider: str = "anthropic"):
        """
        Initialize AI interface with specified model provider.
        
        Args:
            model_provider: "anthropic" or "openai"
        """
        self.model_provider = model_provider.lower()
        self.persona_parser = PersonaParser()
        
        # Initialize the appropriate client
        if self.model_provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic package not available")
            self.anthropic_client = Anthropic()
            self.openai_client = None
        elif self.model_provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI package not available")
            self.openai_client = OpenAI()
            self.anthropic_client = None
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}")
        
        # Find the project root directory (where audit_inputs is located)
        self.project_root = self._find_project_root()
        
        # Cache for parsed persona to avoid redundant parsing
        self._cached_persona_content = None
        self._cached_persona_attributes = None

    @classmethod
    def get_available_models(cls) -> dict:
        """Get available models for each provider."""
        models = {}
        if ANTHROPIC_AVAILABLE:
            models["anthropic"] = {
                "claude-3-opus-20240229": "Claude 3 Opus (High Quality)",
                "claude-3-sonnet-20240229": "Claude 3 Sonnet (Balanced)",
                "claude-3-haiku-20240307": "Claude 3 Haiku (Fast)"
            }
        if OPENAI_AVAILABLE:
            models["openai"] = {
                "gpt-4.1-mini": "GPT-4.1 Mini (Cost Effective)",
                "gpt-4-turbo": "GPT-4 Turbo (High Quality)",
                "gpt-3.5-turbo": "GPT-3.5 Turbo (Fast)"
            }
        return models

    def switch_provider(self, model_provider: str):
        """Switch between AI providers."""
        if model_provider.lower() == self.model_provider:
            return  # Already using this provider
        
        self.model_provider = model_provider.lower()
        
        if self.model_provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic package not available")
            self.anthropic_client = Anthropic()
            self.openai_client = None
        elif self.model_provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI package not available")
            self.openai_client = OpenAI()
            self.anthropic_client = None

    def _make_api_call(self, system_message: str, user_prompt: str, max_tokens: int = 2000, temperature: float = 0.3) -> str:
        """Make API call to the selected provider."""
        retries = 3
        for attempt in range(retries):
            try:
                if self.model_provider == "anthropic":
                    message = self.anthropic_client.messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=system_message,
                        messages=[{"role": "user", "content": user_prompt}],
                    )
                    return message.content[0].text
                
                elif self.model_provider == "openai":
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4.1-mini",
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                    return response.choices[0].message.content
                
            except Exception as e:
                logging.warning(f"API call failed on attempt {attempt + 1} of {retries}. Error: {e}")
                if attempt + 1 == retries:
                    provider_name = "Anthropic" if self.model_provider == "anthropic" else "OpenAI"
                    logging.error(f"Final {provider_name} API call attempt failed.")
                    return f"Error: Could not generate response due to persistent {provider_name} API error."
        
        return "Error: Should not be reached."

    def _find_project_root(self) -> Path:
        """Find the project root directory by looking for audit_inputs folder."""
        current_path = Path(__file__).parent
        
        # Go up directories until we find audit_inputs
        while current_path != current_path.parent:
            if (current_path / "audit_inputs").exists():
                return current_path
            current_path = current_path.parent
        
        # If not found, assume current working directory
        if (Path.cwd() / "audit_inputs").exists():
            return Path.cwd()
        
        # Fallback to the parent of audit_tool directory
        return Path(__file__).parent.parent

    def _load_prompt_template(self, template_name: str) -> str:
        """Load prompt template from audit_inputs/prompts folder."""
        template_path = self.project_root / "audit_inputs" / "prompts" / f"{template_name}.md"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract the main prompt section (everything after "## Main Prompt")
                if "## Main Prompt" in content:
                    return content.split("## Main Prompt")[1].strip()
                return content
        except FileNotFoundError:
            logging.error(f"Prompt template not found: {template_path}")
            return "Error: Prompt template not found."
    
    def _get_system_message(self, template_name: str) -> str:
        """Extract system message from prompt template."""
        template_path = self.project_root / "audit_inputs" / "prompts" / f"{template_name}.md"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract system message section
                if "## System Message" in content:
                    lines = content.split("## System Message")[1].split("## Main Prompt")[0].strip()
                    return lines
                return "You are a helpful AI assistant."
        except FileNotFoundError:
            return "You are a helpful AI assistant."
    
    def _get_cached_persona_attributes(self, persona_content: str):
        """Get cached persona attributes or parse if not cached."""
        if self._cached_persona_content != persona_content:
            # Content changed, need to re-parse
            logging.info("Parsing persona content...")
            self._cached_persona_attributes = self.persona_parser.extract_attributes_from_content(persona_content, log_parsing=False)
            self._cached_persona_content = persona_content
        
        return self._cached_persona_attributes

    def _format_persona_attributes(self, persona_attributes) -> dict:
        """Format persona attributes for template substitution."""
        return {
            'persona_name': persona_attributes.name,
            'persona_role': persona_attributes.role,
            'persona_industry': persona_attributes.industry,
            'persona_geographic_scope': persona_attributes.geographic_scope,
            'persona_business_context': persona_attributes.business_context,
            'persona_communication_style': persona_attributes.communication_style,
            'persona_priorities': '\n'.join([f"- {priority}" for priority in persona_attributes.key_priorities]),
            'persona_pain_points': '\n'.join([f"- {pain}" for pain in persona_attributes.pain_points])
        }

    def generate_experience_report(self, url: str, page_content: str, persona_content: str, methodology) -> str:
        """Generate experience report using configurable prompts and structured persona parsing."""
        
        # Get cached persona attributes (parsed only once per persona)
        persona_attributes = self._get_cached_persona_attributes(persona_content)
        
        # Load prompt template
        prompt_template = self._load_prompt_template("narrative_analysis")
        system_message = self._get_system_message("narrative_analysis")
        
        # Format persona attributes for template
        persona_vars = self._format_persona_attributes(persona_attributes)
        
        # Substitute variables in prompt
        prompt = prompt_template.format(
            page_content=page_content[:12000],  # Limit content length
            **persona_vars
        )
        
        return self._make_api_call(system_message, prompt, max_tokens=1500, temperature=0.6)

    def generate_hygiene_scorecard(self, url: str, page_content: str, persona_content: str, methodology) -> str:
        """Generate hygiene scorecard using configurable prompts and YAML methodology."""
        
        # Get cached persona attributes (parsed only once per persona)
        persona_attributes = self._get_cached_persona_attributes(persona_content)
        
        # Get criteria from methodology (this would need to be implemented)
        # For now, use basic criteria
        criteria_list = self._get_criteria_for_page(page_content, methodology)
        
        # Load prompt template
        prompt_template = self._load_prompt_template("hygiene_scorecard")
        system_message = self._get_system_message("hygiene_scorecard")
        
        # Format persona attributes for template
        persona_vars = self._format_persona_attributes(persona_attributes)
        
        # Substitute variables in prompt
        prompt = prompt_template.format(
            page_url=url,
            page_content=page_content[:8000],  # Limit content length
            criteria_list=criteria_list,
            current_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            scoring_table="[To be filled by AI]",
            **persona_vars
        )
        
        return self._make_api_call(system_message, prompt, max_tokens=2000, temperature=0.3)
    
    def _get_criteria_for_page(self, page_content: str, methodology) -> str:
        """Get appropriate criteria based on page content and methodology."""
        # This is a simplified version - would need full implementation
        # based on page classification and YAML methodology
        
        basic_criteria = [
            "Corporate Positioning Alignment - How well does the page reflect the company's core brand message?",
            "Brand Differentiation - Does the content clearly differentiate from competitors?", 
            "Value Proposition Clarity - Is the value proposition clear and compelling for the target persona?",
            "Trust & Credibility Signals - Are there sufficient trust indicators and proof points?",
            "Call-to-Action Effectiveness - Are the next steps clear and relevant to the persona?"
        ]
        
        return '\n'.join([f"- {criterion}" for criterion in basic_criteria])

    def generate_narrative(self, persona_content: str, page_text: str) -> str:
        """
        Legacy method - redirects to new experience report generation
        """
        return self.generate_experience_report("", page_text, persona_content, None)

    def get_subjective_score(self, criterion_name: str, page_text: str) -> float:
        """
        Gets a single numerical score for a subjective criterion from the AI, with retries.
        """
        prompt = f"""
You are a brand analyst. Your task is to provide a single numerical score from 0.0 to 10.0 based on the provided criterion and webpage text.

**Criterion to score:** {criterion_name}
Scoring Scale:
- 0-3: Poor/Missing
- 4-5: Below Average
- 6-7: Average
- 8-9: Strong
- 10: Exceptional

**Webpage Text (first 4000 characters):**
<page_text>
{page_text[:4000]}
</page_text>

Based on the text and the criterion "{criterion_name}", what is the score?

Respond with ONLY a single floating-point number (e.g., 7.5). Do not include any other text, explanation, or punctuation.
"""
        retries = 3
        for attempt in range(retries):
            try:
                message = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=10,
                    temperature=0.1,
                    system="You are a brand analyst who provides only a single numerical score from 0.0 to 10.0 and nothing else.",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )
                response_text = message.content[0].text.strip()
                score = float(response_text)
                return max(0.0, min(10.0, score))
            except (ValueError, IndexError):
                logging.warning(f"Could not parse float from AI response for '{criterion_name}'. Got: '{response_text}'. Defaulting to 5.0.")
                return 5.0 # Don't retry on parsing errors
            except Exception as e:
                logging.warning(f"API call failed for subjective score on attempt {attempt + 1} of {retries}. Error: {e}")
                if attempt + 1 == retries:
                    logging.error(f"Final API call attempt failed for '{criterion_name}'. Defaulting to 5.0.")
                    return 5.0
        return 5.0

    def generate_strategic_summary(self, compiled_text: str) -> str:
        """
        Performs a thematic analysis on a large body of text to extract
        an executive summary and key themes.
        """
        prompt = f"""
You are a strategic analyst. You have been given a series of narrative reports, each written from a specific persona's point of view about a webpage. Your task is to perform a thematic analysis on these reports to synthesize an executive summary, key strengths, and key weaknesses.

<compiled_narratives>
{compiled_text}
</compiled_narratives>

Analyze the compiled narratives and provide a raw JSON object with the following structure. Do NOT include any explanatory text before or after the JSON object. Ensure all strings within the JSON are properly escaped.

{{
  "executive_summary": "A concise, high-level summary of the overall findings from all reports.",
  "key_strengths": ["A list of 3-5 key strengths that appeared consistently across the reports."],
  "key_weaknesses": ["A list of 3-5 key weaknesses or recurring issues identified in the reports."]
}}
"""
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                temperature=0.2,
                system="You are a strategic analyst who synthesizes qualitative data into a raw, valid JSON object and nothing else.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            return message.content[0].text
        except Exception as e:
            logging.error(f"Could not generate strategic summary due to an API error: {e}")
            # Fallback to a placeholder JSON if the API call fails
            placeholder = {
                "executive_summary": "Error: The AI-powered summary could not be generated.",
                "key_strengths": ["Could not be determined."],
                "key_weaknesses": ["Could not be determined."]
            }
            return json.dumps(placeholder) 