"""
This module handles all interactions with third-party AI APIs.
"""
import os
import anthropic
import logging
from dotenv import load_dotenv
from .models import PageData
import json

load_dotenv()

class AIInterface:
    """A class to handle interactions with the Anthropic API."""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_narrative(self, persona_content: str, page_text: str) -> str:
        """
        Calls the AI to generate a narrative report, with retries.
        """
        prompt = f"""
You are an expert at emulating a specific persona to analyze a webpage. Your task is to adopt the mindset, goals, and pain points of the persona provided below and write a first-person analysis from their perspective.

<persona_to_emulate>
{persona_content}
</persona_to_emulate>

You have been given the raw text content from a webpage to analyze:
<webpage_text>
{page_text[:12000]}
</webpage_text>

---
**TONE & STYLE**

Your tone must match the persona. Your analysis must be **professional, analytical, and constructive**, framed from the persona's point of view.
- **BE:** Objective, direct, and candid in the persona's voice.
- **AVOID:** Generic or melodramatic language.
- **FOCUS:** Frame all analysis in terms of the persona's goals and how this webpage helps or hinders them.
---

Your task is to write a professional, first-person strategic analysis of this content *from the persona's perspective*.

First, provide a table of specific copy examples from the text. Identify "Effective Copy" that resonates with the persona and "Ineffective Copy" that is vague or fails to meet their needs. For each, provide a concise strategic analysis *from the persona's viewpoint*. Use this markdown format:

| Finding         | Example from Text | Strategic Analysis (from Persona's View) |
|-----------------|-------------------|------------------------------------------|
| Ineffective Copy | "Example..."      | "As a [Persona Role], this is unhelpful because..."   |
| Effective Copy   | "Example..."      | "As a [Persona Role], this is useful because..."       |

After the table, write a first-person narrative analysis (2-3 paragraphs) as if you are the persona. Provide a balanced view of strengths and weaknesses. Structure your analysis around these key questions:

*   **First Impression:** What is my immediate impression of this page as [Persona Role]? How clear is the value proposition *for me*?
*   **Language & Tone:** How well does the language resonate with me? Where is it effective and where does it fall short? Refer to your examples.
*   **Gaps in Information:** What critical information is missing *for me* to move forward? (e.g., proof points, outcomes, differentiators relevant to my role).
*   **Trust and Credibility:** Does this page build or erode my trust in this company? What specific elements contribute to this?
*   **Business Impact & Next Steps:** What is the likely impact of this page on someone like me? What would I, as [Persona Role], recommend they change?
"""
        retries = 3
        for attempt in range(retries):
            try:
                message = self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1500,
                    temperature=0.6,
                    system="You are an expert persona simulator. Your task is to adopt the provided persona and write a first-person analysis of a webpage from their specific point of view. Maintain the persona's voice and perspective throughout.",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )
                return message.content[0].text
            except Exception as e:
                logging.warning(f"API call failed on attempt {attempt + 1} of {retries}. Error: {e}")
                if attempt + 1 == retries:
                    logging.error("Final API call attempt failed. Could not generate narrative.")
                    return "Error: Could not generate the narrative report due to a persistent API error."
        return "Error: Should not be reached."

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