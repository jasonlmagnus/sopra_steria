#!/usr/bin/env python3
"""generate_ai_reports.py

Create persona-specific brand-audit reports using the `vector/report_prompt.md` template
and OpenAI ChatCompletion. Requires an `OPENAI_API_KEY` env variable.

Usage:
  python vector/generate_ai_reports.py --model gpt-4o --temperature 0.2
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import textwrap
from datetime import datetime
from typing import Any, Dict, List

import openai

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parents[1]  # project root
DATA_DIR = ROOT / "vector" / "data"
PROMPT_PATH = ROOT / "vector" / "report_prompt.md"
REPORT_DIR = ROOT / "vector" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_system_prompt() -> str:
    """System directive for the LLM."""
    return (
        "You are a meticulous brand-audit analyst. "
        "You produce markdown reports that strictly follow the provided template."
    )


def build_user_prompt(base_prompt: str, persona: Dict[str, Any], pages: List[Dict[str, Any]],
                      social_snippet: str, journey_snippet: str) -> str:
    """Insert runtime data into the template under the Inputs section."""
    # Serialize pages as JSON (stringified, compact)
    pages_json = json.dumps(pages, ensure_ascii=False, indent=2)
    persona_json = json.dumps(persona, ensure_ascii=False, indent=2)

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    documents_analyzed = len(pages)

    filled = base_prompt.replace("generated_timestamp = \"2025-07-03 08:03:52\"",
                                 f"generated_timestamp = \"{now}\"")
    filled = filled.replace("documents_analyzed  = 18", f"documents_analyzed  = {documents_analyzed}")

    # Quick hack: inject persona and pages JSON at the top of Inputs section
    injection = textwrap.dedent(
        f"""
        persona = {persona_json}

        pages = {pages_json}
        """
    )
    filled = filled.replace("```json", "```json\n" + injection)

    # Append social / journey snippets at end (the prompt instructs using those files)
    filled += "\n\n" + social_snippet + "\n" + journey_snippet
    return filled


def load_social_snippet() -> str:
    sm_path = ROOT / "audit_inputs" / "social_media" / "sm_dashboard_data_enhanced.md"
    if sm_path.exists():
        return sm_path.read_text(encoding="utf-8")
    return ""


def load_journey_snippet() -> str:
    journey_path = ROOT / "audit_inputs" / "persona_journeys" / "unified_journey_analysis.md"
    if journey_path.exists():
        return journey_path.read_text(encoding="utf-8")
    return ""


# ---------------------------------------------------------------------------
# Main generation routine
# ---------------------------------------------------------------------------

def generate_report(persona_file: pathlib.Path, args: argparse.Namespace, base_prompt: str,
                     social_snippet: str, journey_snippet: str) -> None:
    data = json.loads(persona_file.read_text())
    persona_meta: Dict[str, Any] = data[0]["persona"]  # assumes at least one page exists
    pages: List[Dict[str, Any]] = data

    user_prompt = build_user_prompt(base_prompt, persona_meta, pages, social_snippet, journey_snippet)

    response = openai.ChatCompletion.create(
        model=args.model,
        temperature=args.temperature,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
    )
    report_md = response.choices[0].message.content

    out_path = REPORT_DIR / f"{persona_file.stem}_ai_report.md"
    out_path.write_text(report_md, encoding="utf-8")
    print(f"✅ generated {out_path.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate persona audit reports via OpenAI")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model name (default: gpt-4o)")
    parser.add_argument("--temperature", type=float, default=0.3, help="Sampling temperature (default: 0.3)")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY environment variable not set.")

    base_prompt = load_prompt()
    social_snippet = load_social_snippet()
    journey_snippet = load_journey_snippet()

    persona_files = sorted(DATA_DIR.glob("persona_*.json"))
    if not persona_files:
        parser.error("No persona_*.json files found in vector/data/.")

    for pf in persona_files:
        generate_report(pf, args, base_prompt, social_snippet, journey_snippet)


if __name__ == "__main__":
    main() 