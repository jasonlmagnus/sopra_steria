"""
This is the main entry point for the Persona Experience & Brand Audit Tool.
"""
import argparse
import sys
import logging
import re
from audit_tool.scraper import Scraper
from audit_tool.ai_interface import AIInterface
from audit_tool.generators import NarrativeGenerator, ScorecardGenerator, SummaryGenerator
from audit_tool.reporter import Reporter
from audit_tool.methodology_parser import MethodologyParser
from tqdm import tqdm

METHODOLOGY_PATH = "prompts/audit/audit_method.md"

def process_url(url: str, persona_content: str, scraper: Scraper, narrative_generator: NarrativeGenerator, scorecard_generator: ScorecardGenerator, reporter: Reporter):
    """Processes a single URL."""
    logging.info(f"--- Starting Audit for URL: {url} ---")
    page_data = scraper.fetch_page(url)

    if page_data.is_404:
        logging.error(f"Could not fetch {url}. Skipping.")
        return

    narrative_report = narrative_generator.create_report(persona_content, page_data)
    scorecard = scorecard_generator.create_scorecard(page_data)
    
    reporter.write_narrative_report(url, narrative_report)
    reporter.write_scorecard(scorecard)
    logging.info(f"--- Finished Audit for URL: {url} ---")

def main():
    """
    Main function to run the audit tool.
    - Parses command-line arguments for URL and persona.
    - Orchestrates the scraping, generation, and reporting process.
    """
    # --- Setup Logging ---
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("audit_tool.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    # --- End Setup ---

    parser = argparse.ArgumentParser(description="Run a persona-based experience audit on one or more URLs.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", type=str, help="A single URL to audit.")
    group.add_argument("--file", type=str, help="A file containing a list of URLs to audit (one per line).")
    
    parser.add_argument("--persona", type=str, required=True, help="The file path to the persona markdown file.")
    args = parser.parse_args()

    try:
        with open(args.persona, 'r', encoding='utf-8') as f:
            persona_content = f.read()
    except FileNotFoundError:
        logging.error(f"Persona file not found at {args.persona}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error reading persona file: {e}")
        sys.exit(1)

    logging.info(f"Starting audit for persona: {args.persona}")

    # 1. Instantiate components
    logging.info("--- Initializing Components ---")
    scraper = Scraper()
    ai_interface = AIInterface()
    
    methodology_parser = MethodologyParser(METHODOLOGY_PATH)
    methodology = methodology_parser.parse()
    
    narrative_generator = NarrativeGenerator(ai_interface)
    scorecard_generator = ScorecardGenerator(methodology, ai_interface)
    
    reporter = Reporter(persona_name=args.persona)

    urls_to_process = []
    if args.url:
        urls_to_process.append(args.url)
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Use regex to find all URLs in the markdown file
                urls_to_process = re.findall(r'https?://[^\s|)]+', content)
        except FileNotFoundError:
            logging.error(f"URL file not found at {args.file}")
            sys.exit(1)

    if not urls_to_process:
        logging.error("No URLs found to process. Please check the input file.")
        sys.exit(1)

    logging.info(f"Found {len(urls_to_process)} URL(s) to process.")

    for url in tqdm(urls_to_process, desc="Auditing URLs"):
        process_url(url, persona_content, scraper, narrative_generator, scorecard_generator, reporter)

    logging.info("--- All individual audits complete. Starting summary generation. ---")
    summary_generator = SummaryGenerator(
        persona_name=args.persona, 
        ai_interface=ai_interface,
        methodology=methodology
    )
    summary_report = summary_generator.create_summary()
    reporter.write_summary_report(summary_report)

    logging.info("Audit complete.")

if __name__ == "__main__":
    main() 