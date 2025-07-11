import sys
import os
from typing import Optional, List, Dict, Any
import pandas as pd
import re
import json
import io
import zipfile
import tempfile
import subprocess
import threading
import asyncio
from datetime import datetime
from pathlib import Path
import uuid

# Add parent directory to Python path to import audit_tool
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

import yaml
from fastapi import FastAPI, HTTPException, Response, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from audit_tool.dashboard.components.data_loader import BrandHealthDataLoader
from audit_tool.dashboard.components.metrics_calculator import (
    BrandHealthMetricsCalculator,
)
from audit_tool.html_report_generator import HTMLReportGenerator

app = FastAPI(title="Sopra Steria Audit FastAPI")

# Global audit status tracking
audit_sessions: Dict[str, Dict[str, Any]] = {}

# Data models for API requests
class ReportRequest(BaseModel):
    reportType: str
    personas: List[str] = []
    tiers: List[str] = []
    includeAnalysis: bool = True
    includeRecommendations: bool = True
    format: str = "PDF"

class HTMLReportRequest(BaseModel):
    generationMode: str
    personas: List[str] = []
    includeTierAnalysis: bool = True
    includePersonaVoice: bool = True
    includeRecommendations: bool = True
    includeVisualBrand: bool = True
    autoOpen: bool = False
    createZip: bool = True

class ExportRequest(BaseModel):
    format: str
    scope: str
    filters: Optional[Dict[str, Any]] = None
    columns: Optional[List[str]] = None

class BulkExportRequest(BaseModel):
    includeMaster: bool = True
    includeDatasets: bool = True
    includeReports: bool = True
    includeRaw: bool = False

class AuditRunRequest(BaseModel):
    persona_content: str
    persona_filename: str
    urls: List[str]
    model_provider: str = "openai"

class AuditProcessRequest(BaseModel):
    session_id: str
    persona_name: str

def extract_persona_name(persona_content: str, filename: Optional[str] = None) -> str:
    """Extract a human-readable persona name from content"""
    lines = persona_content.strip().split('\n')
    if lines:
        first_line = lines[0].strip()
        if first_line.startswith("Persona Brief:"):
            return first_line.replace("Persona Brief:", "").strip()
        if first_line and not first_line.startswith('#'):
            return first_line
    
    # Fallback to pattern matching
    match = re.search(r"P\d+", persona_content)
    if not match and filename:
        match = re.search(r"P\d+", filename)
    return match.group(0) if match else "default_persona"

def run_audit_subprocess(session_id: str, persona_file_path: str, urls_file_path: str, 
                        persona_name: str, model_provider: str = "openai"):
    """Run audit as subprocess with real-time logging"""
    try:
        # Update session status
        audit_sessions[session_id]['status'] = 'running'
        audit_sessions[session_id]['progress'] = 10
        audit_sessions[session_id]['message'] = f'Starting audit for {persona_name} using {model_provider.upper()}...'
        
        # Create output directory
        output_dir = os.path.join("audit_outputs", persona_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # Build command
        command = [
            "python",
            "-m",
            "audit_tool.main",
            "--urls",
            urls_file_path,
            "--persona",
            persona_file_path,
            "--output",
            output_dir,
            "--model",
            model_provider
        ]
        
        # Start subprocess
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )
        
        audit_sessions[session_id]['process'] = process
        audit_sessions[session_id]['progress'] = 20
        audit_sessions[session_id]['message'] = 'Audit process started...'
        
        # Stream logs
        log_lines = []
        url_pattern = re.compile(r'Analyzing URL \d+/\d+')
        completion_keywords = ['completed', 'finished', 'done', 'success']
        
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
                
            line = line.rstrip()
            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")
            
            # Update progress based on log content
            if url_pattern.search(line):
                # Extract progress from URL analysis
                url_match = re.search(r'(\d+)/(\d+)', line)
                if url_match:
                    current, total = int(url_match.group(1)), int(url_match.group(2))
                    progress = 20 + int((current / total) * 60)  # 20-80% for URL analysis
                    audit_sessions[session_id]['progress'] = min(progress, 80)
            
            elif any(keyword in line.lower() for keyword in completion_keywords):
                audit_sessions[session_id]['progress'] = 90
            
            # Keep last 100 log lines
            if len(log_lines) > 100:
                log_lines = log_lines[-100:]
            
            audit_sessions[session_id]['logs'] = log_lines
            audit_sessions[session_id]['message'] = line
        
        # Wait for completion
        process.wait()
        
        if process.returncode == 0:
            audit_sessions[session_id]['status'] = 'completed'
            audit_sessions[session_id]['progress'] = 100
            audit_sessions[session_id]['message'] = '✅ Audit completed successfully!'
            audit_sessions[session_id]['completed_persona'] = persona_name
        else:
            audit_sessions[session_id]['status'] = 'failed'
            audit_sessions[session_id]['message'] = '❌ Audit failed. Check logs for details.'
            
    except Exception as e:
        audit_sessions[session_id]['status'] = 'failed'
        audit_sessions[session_id]['message'] = f'❌ Audit error: {str(e)}'
        audit_sessions[session_id]['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {str(e)}")

def process_audit_results_background(session_id: str, persona_name: str):
    """Process audit results in background"""
    try:
        audit_sessions[session_id]['processing_status'] = 'running'
        audit_sessions[session_id]['processing_progress'] = 10
        audit_sessions[session_id]['processing_message'] = '📦 Importing post-processor...'
        
        # Import post-processor
        from audit_tool.audit_post_processor import AuditPostProcessor
        
        audit_sessions[session_id]['processing_progress'] = 20
        audit_sessions[session_id]['processing_message'] = '🏗️ Initializing processor...'
        
        processor = AuditPostProcessor(persona_name)
        
        audit_sessions[session_id]['processing_progress'] = 30
        audit_sessions[session_id]['processing_message'] = '✅ Validating audit output...'
        
        if not processor.validate_audit_output():
            audit_sessions[session_id]['processing_status'] = 'failed'
            audit_sessions[session_id]['processing_message'] = '❌ Invalid audit output - cannot process'
            return
        
        audit_sessions[session_id]['processing_progress'] = 40
        audit_sessions[session_id]['processing_message'] = '🏷️ Classifying page tiers...'
        
        classifications = processor.classify_page_tiers()
        
        audit_sessions[session_id]['processing_progress'] = 60
        audit_sessions[session_id]['processing_message'] = '📊 Processing backfill data...'
        
        processed_data = processor.run_backfill_processing()
        
        audit_sessions[session_id]['processing_progress'] = 80
        audit_sessions[session_id]['processing_message'] = '📋 Generating strategic summary...'
        
        summary_path = processor.generate_strategic_summary()
        
        audit_sessions[session_id]['processing_progress'] = 90
        audit_sessions[session_id]['processing_message'] = '🗄️ Adding to unified database...'
        
        db_success = processor.add_to_database()
        
        if db_success:
            audit_sessions[session_id]['processing_status'] = 'completed'
            audit_sessions[session_id]['processing_progress'] = 100
            audit_sessions[session_id]['processing_message'] = '🎉 Successfully added to database!'
        else:
            audit_sessions[session_id]['processing_status'] = 'failed'
            audit_sessions[session_id]['processing_message'] = '❌ Failed to add to database'
        
    except Exception as e:
        audit_sessions[session_id]['processing_status'] = 'failed'
        audit_sessions[session_id]['processing_message'] = f'❌ Processing error: {str(e)}'

def extract_persona_quotes_success(text):
    """Extract persona voice quotes from success text"""
    if not text or pd.isna(text):
        return []
    
    quotes = []
    text_str = str(text)
    
    # Look for quoted text patterns
    quote_patterns = [
        r'"([^"]{20,200})"',  # Text in double quotes
        r"'([^']{20,200})'",  # Text in single quotes
        r'—([^—]{20,200})—',  # Text between em dashes
        r'–([^–]{20,200})–',  # Text between en dashes
    ]
    
    for pattern in quote_patterns:
        matches = re.findall(pattern, text_str)
        quotes.extend(matches[:2])  # Limit to 2 quotes per pattern
    
    return quotes[:5]  # Return max 5 quotes

def load_master_data():
    """Load master dataset"""
    try:
        data_loader = BrandHealthDataLoader()
        datasets, master_df = data_loader.load_all_data()
        return master_df
    except Exception as e:
        print(f"Error loading master data: {e}")
        return pd.DataFrame()

def filter_data(df: pd.DataFrame, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Apply filters to dataframe"""
    if not filters:
        return df
    
    filtered_df = df.copy()
    
    if 'persona' in filters and filters['persona'] and filters['persona'] != 'All':
        filtered_df = filtered_df[filtered_df['persona_id'] == filters['persona']]
    
    if 'tier' in filters and filters['tier'] and filters['tier'] != 'All':
        filtered_df = filtered_df[filtered_df['tier'] == filters['tier']]
    
    if 'scoreRange' in filters:
        min_score, max_score = filters['scoreRange']
        if 'avg_score' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['avg_score'] >= min_score) & 
                (filtered_df['avg_score'] <= max_score)
            ]
    
    return filtered_df

def generate_executive_summary_report(df: pd.DataFrame, metrics_calc: BrandHealthMetricsCalculator) -> Dict[str, Any]:
    """Generate executive summary report"""
    if df.empty:
        return {'error': 'No data available for executive summary'}
    
    try:
        # Calculate real metrics from data
        total_records = len(df)
        unique_pages = df['page_id'].nunique() if 'page_id' in df.columns else 0
        avg_score = df['final_score'].mean() if 'final_score' in df.columns else 0
        
        # Count issues by severity
        critical_issues = len(df[df['descriptor'] == 'CRITICAL']) if 'descriptor' in df.columns else 0
        concerns = len(df[df['descriptor'] == 'CONCERN']) if 'descriptor' in df.columns else 0
        warnings = len(df[df['descriptor'] == 'WARN']) if 'descriptor' in df.columns else 0
        good_scores = len(df[df['descriptor'] == 'GOOD']) if 'descriptor' in df.columns else 0
        
        # Top issues by criteria
        top_issues = []
        if 'criterion_id' in df.columns and 'final_score' in df.columns:
            low_scoring_criteria = df[df['final_score'] < 6].groupby('criterion_id')['final_score'].mean().sort_values().head(5)
            for criterion, score in low_scoring_criteria.items():
                top_issues.append({
                    'criterion': criterion.replace('_', ' ').title(),
                    'score': round(score, 1)
                })
        
        return {
            'type': 'Executive Summary Report',
            'generated_date': datetime.now().isoformat(),
            'metrics': {
                'total_records': total_records,
                'unique_pages': unique_pages,
                'average_score': round(avg_score, 1),
                'critical_issues': critical_issues,
                'concerns': concerns,
                'warnings': warnings,
                'good_scores': good_scores
            },
            'top_issues': top_issues,
            'summary': f"Analyzed {total_records:,} records across {unique_pages:,} pages with an average score of {avg_score:.1f}/10. Found {critical_issues} critical issues and {concerns} concerns."
        }
    except Exception as e:
        return {'error': f'Error generating executive summary: {str(e)}'}

def generate_persona_performance_report(df: pd.DataFrame, metrics_calc: BrandHealthMetricsCalculator) -> Dict[str, Any]:
    """Generate persona performance report"""
    if df.empty or 'persona_id' not in df.columns:
        return {'error': 'No persona data available'}
    
    try:
        persona_performance = df.groupby('persona_id').agg({
            'avg_score': ['mean', 'count'],
            'final_score': 'mean'
        }).round(2)
        
        # Flatten column names
        persona_performance.columns = ['avg_score_mean', 'page_count', 'final_score_mean']
        persona_performance = persona_performance.sort_values('avg_score_mean', ascending=False)
        
        # Convert to dict for JSON serialization
        personas = []
        for persona_id, row in persona_performance.iterrows():
            personas.append({
                'persona_id': persona_id,
                'average_score': row['avg_score_mean'],
                'page_count': row['page_count'],
                'final_score': row['final_score_mean']
            })
        
        best_persona = personas[0]['persona_id'] if personas else 'Unknown'
        worst_persona = personas[-1]['persona_id'] if personas else 'Unknown'
        
        return {
            'type': 'Persona Performance Report',
            'generated_date': datetime.now().isoformat(),
            'personas': personas,
            'insights': {
                'best_performing': best_persona,
                'needs_attention': worst_persona,
                'total_personas': len(personas)
            }
        }
    except Exception as e:
        return {'error': f'Error generating persona performance report: {str(e)}'}

def generate_content_tier_report(df: pd.DataFrame, metrics_calc: BrandHealthMetricsCalculator) -> Dict[str, Any]:
    """Generate content tier analysis report"""
    if df.empty or 'tier' not in df.columns:
        return {'error': 'No tier data available'}
    
    try:
        tier_performance = df.groupby('tier').agg({
            'avg_score': ['mean', 'count', 'std'],
            'final_score': 'mean'
        }).round(2)
        
        # Flatten column names
        tier_performance.columns = ['avg_score_mean', 'page_count', 'score_variation', 'final_score_mean']
        tier_performance = tier_performance.sort_values('avg_score_mean', ascending=False)
        
        # Convert to dict for JSON serialization
        tiers = []
        for tier_name, row in tier_performance.iterrows():
            tiers.append({
                'tier_name': tier_name,
                'average_score': row['avg_score_mean'],
                'page_count': row['page_count'],
                'score_variation': row['score_variation'],
                'final_score': row['final_score_mean']
            })
        
        return {
            'type': 'Content Tier Analysis Report',
            'generated_date': datetime.now().isoformat(),
            'tiers': tiers,
            'insights': {
                'total_tiers': len(tiers),
                'best_performing_tier': tiers[0]['tier_name'] if tiers else 'Unknown',
                'most_variable_tier': max(tiers, key=lambda x: x['score_variation'])['tier_name'] if tiers else 'Unknown'
            }
        }
    except Exception as e:
        return {'error': f'Error generating content tier report: {str(e)}'}

def generate_success_stories_report(df: pd.DataFrame, metrics_calc: BrandHealthMetricsCalculator) -> Dict[str, Any]:
    """Generate success stories report"""
    if df.empty or 'final_score' not in df.columns:
        return {'error': 'No score data available for success stories'}
    
    try:
        success_threshold = 7.5
        success_stories = df[df['final_score'] >= success_threshold]
        
        if success_stories.empty:
            max_score = df['final_score'].max()
            return {
                'type': 'Success Stories Report',
                'generated_date': datetime.now().isoformat(),
                'success_stories': [],
                'message': f'No pages found with score ≥ {success_threshold}. Highest score: {max_score:.1f}'
            }
        
        # Group by page to show unique pages
        if 'page_id' in success_stories.columns and 'url' in success_stories.columns:
            page_scores = success_stories.groupby(['page_id', 'url'])['final_score'].mean().sort_values(ascending=False).head(10)
            
            stories = []
            for i, ((page_id, url), score) in enumerate(page_scores.items(), 1):
                page_data = success_stories[success_stories['page_id'] == page_id].iloc[0]
                tier = page_data.get('tier_name', 'Unknown') if 'tier_name' in page_data else 'Unknown'
                
                stories.append({
                    'rank': i,
                    'page_id': page_id,
                    'url': url[:100] + '...' if len(url) > 100 else url,
                    'score': round(score, 1),
                    'tier': tier
                })
        else:
            # Fallback if no page grouping available
            stories = []
            for i, (_, story) in enumerate(success_stories.head(5).iterrows(), 1):
                stories.append({
                    'rank': i,
                    'page_id': story.get('page_id', 'Unknown'),
                    'score': round(story['final_score'], 1),
                    'tier': story.get('tier_name', 'Unknown')
                })
        
        return {
            'type': 'Success Stories Report',
            'generated_date': datetime.now().isoformat(),
            'success_stories': stories,
            'summary': f'Found {len(success_stories)} success stories with score ≥ {success_threshold}',
            'threshold': success_threshold
        }
    except Exception as e:
        return {'error': f'Error generating success stories report: {str(e)}'}

# Audit Runner API endpoints
@app.post("/api/audit/run")
async def run_audit(request: AuditRunRequest, background_tasks: BackgroundTasks):
    """Start a new audit process"""
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Extract persona name
        persona_name = extract_persona_name(request.persona_content, request.persona_filename)
        
        # Validate URLs
        valid_urls = [url for url in request.urls if url.startswith(('http://', 'https://'))]
        if not valid_urls:
            raise HTTPException(status_code=400, detail="No valid URLs provided")
        
        # Initialize session
        audit_sessions[session_id] = {
            'status': 'initializing',
            'progress': 0,
            'message': 'Initializing audit...',
            'logs': [],
            'persona_name': persona_name,
            'total_urls': len(valid_urls),
            'start_time': datetime.now().isoformat(),
            'process': None,
            'completed_persona': None
        }
        
        # Create temporary files
        temp_dir = tempfile.mkdtemp(prefix="audit_")
        
        # Save persona file
        persona_file_path = os.path.join(temp_dir, request.persona_filename)
        with open(persona_file_path, "w", encoding="utf-8") as f:
            f.write(request.persona_content)
        
        # Save URLs file
        urls_file_path = os.path.join(temp_dir, "urls_to_audit.txt")
        with open(urls_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(valid_urls))
        
        # Store file paths for cleanup
        audit_sessions[session_id]['temp_dir'] = temp_dir
        audit_sessions[session_id]['persona_file'] = persona_file_path
        audit_sessions[session_id]['urls_file'] = urls_file_path
        
        # Start audit in background
        background_tasks.add_task(
            run_audit_subprocess,
            session_id,
            persona_file_path,
            urls_file_path,
            persona_name,
            request.model_provider
        )
        
        return JSONResponse(content={
            'session_id': session_id,
            'persona_name': persona_name,
            'total_urls': len(valid_urls),
            'model_provider': request.model_provider,
            'status': 'started'
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audit/status/{session_id}")
async def get_audit_status(session_id: str):
    """Get real-time audit status"""
    if session_id not in audit_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = audit_sessions[session_id]
    
    return JSONResponse(content={
        'session_id': session_id,
        'status': session.get('status', 'unknown'),
        'progress': session.get('progress', 0),
        'message': session.get('message', ''),
        'logs': session.get('logs', [])[-50:],  # Last 50 log lines
        'persona_name': session.get('persona_name', ''),
        'total_urls': session.get('total_urls', 0),
        'start_time': session.get('start_time', ''),
        'completed_persona': session.get('completed_persona', None)
    })

@app.post("/api/audit/stop/{session_id}")
async def stop_audit(session_id: str):
    """Stop a running audit"""
    if session_id not in audit_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = audit_sessions[session_id]
    
    # Terminate process if running
    if 'process' in session and session['process']:
        try:
            session['process'].terminate()
            session['process'].wait(timeout=5)
        except:
            try:
                session['process'].kill()
            except:
                pass
    
    # Update session status
    audit_sessions[session_id]['status'] = 'stopped'
    audit_sessions[session_id]['message'] = '🛑 Audit stopped by user'
    
    # Cleanup temp files
    if 'temp_dir' in session and os.path.exists(session['temp_dir']):
        import shutil
        shutil.rmtree(session['temp_dir'])
    
    return JSONResponse(content={'status': 'stopped'})

@app.post("/api/audit/process")
async def process_audit_results(request: AuditProcessRequest, background_tasks: BackgroundTasks):
    """Process audit results and add to database"""
    session_id = request.session_id
    
    if session_id not in audit_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = audit_sessions[session_id]
    
    if session.get('status') != 'completed':
        raise HTTPException(status_code=400, detail="Audit not completed")
    
    # Initialize processing status
    audit_sessions[session_id]['processing_status'] = 'starting'
    audit_sessions[session_id]['processing_progress'] = 0
    audit_sessions[session_id]['processing_message'] = 'Starting post-processing...'
    
    # Start processing in background
    background_tasks.add_task(
        process_audit_results_background,
        session_id,
        request.persona_name
    )
    
    return JSONResponse(content={'status': 'processing_started'})

@app.get("/api/audit/processing-status/{session_id}")
async def get_processing_status(session_id: str):
    """Get processing status"""
    if session_id not in audit_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = audit_sessions[session_id]
    
    return JSONResponse(content={
        'session_id': session_id,
        'processing_status': session.get('processing_status', 'not_started'),
        'processing_progress': session.get('processing_progress', 0),
        'processing_message': session.get('processing_message', ''),
        'persona_name': session.get('persona_name', '')
    })

@app.get("/success-library")
def get_success_library(
    successThreshold: float = 7.5,
    persona: str = "All",
    tier: str = "All",
    maxStories: int = 10,
    evidenceType: str = "All",
    searchTerm: str = ""
):
    """Return comprehensive success library data matching Streamlit functionality"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    if master_df.empty:
        return JSONResponse(status_code=404, content={"error": "No data available"})
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    metrics = BrandHealthMetricsCalculator(master_df, recommendations_df)
    
    # Apply filters
    filtered_df = master_df.copy()
    
    # Persona filter
    if persona != "All":
        filtered_df = filtered_df[filtered_df['persona_id'] == persona]
    
    # Tier filter
    if tier != "All":
        filtered_df = filtered_df[filtered_df['tier'] == tier]
    
    # Success threshold filter
    if 'avg_score' in filtered_df.columns:
        success_stories_df = filtered_df[filtered_df['avg_score'] >= successThreshold]
    else:
        success_stories_df = pd.DataFrame()
    
    if success_stories_df.empty:
        return {
            "successStories": [],
            "overview": {
                "totalPages": 0,
                "successPages": 0,
                "successRate": 0,
                "avgScore": 0,
                "excellent": 0,
                "veryGood": 0,
                "good": 0
            },
            "patternData": [],
            "evidenceItems": [],
            "replicationTemplates": [],
            "personas": [],
            "tiers": []
        }
    
    # AGGREGATE TO PAGE LEVEL to avoid duplicates and get richer data
    page_success = success_stories_df.groupby('page_id').agg({
        'avg_score': 'mean',
        'tier': 'first',
        'url': 'first',
        'url_slug': 'first',
        'persona_id': 'first',
        'effective_copy_examples': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 20])[:400],
        'ineffective_copy_examples': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 20])[:400],
        'evidence': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip()])[:500],
        'business_impact_analysis': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:300],
        'trust_credibility_assessment': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:200],
        'information_gaps': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:200]
    }).reset_index()
    
    # Filter to keep only pages that still meet the success threshold after aggregation
    page_success = page_success[page_success['avg_score'] >= successThreshold]
    
    # Sort by score and limit to max stories
    page_success = page_success.sort_values('avg_score', ascending=False).head(maxStories)
    
    # Calculate percentiles for each story
    all_scores = master_df['avg_score'].dropna() if 'avg_score' in master_df.columns else pd.Series([])
    
    # Build success stories with comprehensive data
    success_stories = []
    for _, story in page_success.iterrows():
        page_id = story.get('page_id', 'Unknown')
        score = story.get('avg_score', 0)
        url = story.get('url', '')
        
        # Create friendly page title
        title = create_friendly_page_title(page_id, url)
        
        # Calculate percentile
        percentile = (all_scores < score).mean() * 100 if len(all_scores) > 0 else 0
        
        # Extract persona quotes
        effective_examples = story.get('effective_copy_examples', '')
        persona_quotes = extract_persona_quotes_success(effective_examples)
        
        # Determine sentiment/engagement/conversion based on score (instead of removed fields)
        sentiment = "Positive" if score >= 7.0 else "Neutral" if score >= 5.0 else "Negative"
        engagement = "High" if score >= 8.0 else "Medium" if score >= 6.0 else "Low"
        conversion = "High" if score >= 8.5 else "Medium" if score >= 6.5 else "Low"
        
        story_data = {
            'id': page_id,
            'title': title,
            'score': round(score, 1),
            'tier': story.get('tier', 'Unknown'),
            'persona': story.get('persona_id', 'Unknown'),
            'url': url,
            'percentile': int(percentile),
            'sentiment': sentiment,
            'engagement': engagement,
            'conversion': conversion,
            'effectiveExamples': effective_examples,
            'ineffectiveExamples': story.get('ineffective_copy_examples', ''),
            'trustAssessment': story.get('trust_credibility_assessment', ''),
            'businessImpact': story.get('business_impact_analysis', ''),
            'evidence': story.get('evidence', ''),
            'personaQuotes': persona_quotes
        }
        
        success_stories.append(story_data)
    
    # Calculate overview metrics
    total_pages = len(filtered_df['page_id'].unique()) if 'page_id' in filtered_df.columns else len(filtered_df)
    success_pages = len(page_success)
    success_rate = (success_pages / total_pages * 100) if total_pages > 0 else 0
    avg_success_score = page_success['avg_score'].mean() if success_pages > 0 else 0
    
    # Performance distribution
    excellent = len(page_success[page_success['avg_score'] >= 9.0])
    very_good = len(page_success[(page_success['avg_score'] >= 8.0) & (page_success['avg_score'] < 9.0)])
    good = len(page_success[(page_success['avg_score'] >= 7.5) & (page_success['avg_score'] < 8.0)])
    
    # Pattern analysis by tier
    pattern_data = []
    if 'tier' in success_stories_df.columns:
        tier_patterns = success_stories_df.groupby('tier').agg({
            'avg_score': 'mean',
            'page_id': 'nunique'
        }).reset_index()
        
        for _, row in tier_patterns.iterrows():
            pattern_data.append({
                'tier': row['tier'],
                'avgScore': round(row['avg_score'], 1),
                'count': int(row['page_id'])
            })
    
    # Evidence browser items
    evidence_items = []
    for _, story in page_success.iterrows():
        page_title = create_friendly_page_title(story.get('page_id', 'Unknown'), story.get('url', ''))
        score = story.get('avg_score', 0)
        
        # Extract evidence from various columns
        evidence_sources = {
            'Copy Examples': story.get('effective_copy_examples', ''),
            'Performance Data': story.get('business_impact_analysis', ''),
            'User Feedback': story.get('evidence', ''),
            'Trust Assessment': story.get('trust_credibility_assessment', '')
        }
        
        for evidence_type_key, content in evidence_sources.items():
            if content and len(str(content).strip()) > 20:
                content_str = str(content).strip()
                
                # Apply evidence type filter
                if evidenceType != "All" and evidence_type_key != evidenceType:
                    continue
                
                # Apply search term filter
                if searchTerm and searchTerm.lower() not in content_str.lower():
                    continue
                
                evidence_items.append({
                    'type': evidence_type_key,
                    'content': content_str[:300] + '...' if len(content_str) > 300 else content_str,
                    'pageTitle': page_title,
                    'score': round(score, 1)
                })
    
    # Replication templates
    replication_templates = []
    for pattern in pattern_data:
        replication_templates.append({
            'tier': pattern['tier'],
            'avgScore': pattern['avgScore'],
            'keyElements': [
                'Focus on high-performing criteria patterns',
                'Maintain consistent messaging tone',
                'Implement proven design elements',
                'Apply successful content structure'
            ]
        })
    
    # Available filter options
    personas = ['All'] + sorted(master_df['persona_id'].unique().tolist()) if 'persona_id' in master_df.columns else ['All']
    tiers = ['All'] + sorted([t for t in master_df['tier'].unique() if pd.notna(t)]) if 'tier' in master_df.columns else ['All']
    
    return {
        "successStories": success_stories,
        "overview": {
            "totalPages": total_pages,
            "successPages": success_pages,
            "successRate": round(success_rate, 1),
            "avgScore": round(avg_success_score, 1),
            "excellent": excellent,
            "veryGood": very_good,
            "good": good
        },
        "patternData": pattern_data,
        "evidenceItems": evidence_items,
        "replicationTemplates": replication_templates,
        "personas": personas,
        "tiers": tiers
    }



@app.get("/methodology")
def get_methodology():
    """Return the complete methodology configuration from YAML"""
    try:
        methodology_path = os.path.join(parent_dir, "audit_tool", "config", "methodology.yaml")
        with open(methodology_path, 'r', encoding='utf-8') as file:
            methodology = yaml.safe_load(file)
        return methodology
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to load methodology: {str(e)}"})

@app.get("/hello")
def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/datasets")
def list_datasets():
    data_loader = BrandHealthDataLoader()
    datasets, _ = data_loader.load_all_data()
    return {"datasets": list(datasets.keys())}

@app.get("/datasets/master")
def get_master_dataset():
    """Get the master dataset for Reports Export page"""
    try:
        data_loader = BrandHealthDataLoader()
        datasets, master_df = data_loader.load_all_data()
        if master_df.empty:
            raise HTTPException(status_code=404, detail="No master data available")
        return master_df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading master data: {str(e)}")

@app.get("/datasets/metadata")
def get_datasets_metadata():
    """Get detailed metadata for all datasets"""
    try:
        data_loader = BrandHealthDataLoader()
        datasets, master_df = data_loader.load_all_data()
        
        metadata = []
        for name, df in datasets.items():
            if df is not None and not df.empty:
                metadata.append({
                    'name': name.title(),
                    'records': len(df),
                    'columns': len(df.columns),
                    'memoryMB': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.1f}"
                })
        
        return {"datasets": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dataset metadata: {str(e)}")

@app.get("/datasets/{name}")
def get_dataset(name: str):
    data_loader = BrandHealthDataLoader()
    datasets, _ = data_loader.load_all_data()
    if name not in datasets:
        return JSONResponse(status_code=404, content={"error": "Dataset not found"})
    df = datasets[name]
    json_str = df.to_json(orient="records")
    return Response(content=json_str, media_type="application/json")

@app.get("/opportunities")
def get_opportunities(limit: int = 20):
    """Return top improvement opportunities"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    metrics = BrandHealthMetricsCalculator(master_df, recommendations_df)
    opportunities = metrics.get_top_opportunities(limit=limit)
    return {"opportunities": opportunities}

@app.get("/executive-summary")
def get_executive_summary():
    """Return executive summary metrics"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    metrics = BrandHealthMetricsCalculator(master_df, recommendations_df)
    summary = metrics.generate_executive_summary()
    return summary

@app.get("/strategic-assessment")
def get_strategic_assessment(tier: Optional[str] = None):
    """Return strategic brand assessment (distinctiveness, resonance, conversion)"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    metrics = BrandHealthMetricsCalculator(master_df, recommendations_df)
    
    # Apply tier filtering if specified
    if tier and tier != "All Tiers":
        tier_parts = tier.split()
        if len(tier_parts) >= 2 and "Tier" in tier:
            tier_num = tier_parts[1]
            tier_name = f"tier_{tier_num}"
            
            # Filter the DataFrame
            filtered_df = metrics.df[metrics.df['tier'] == tier_name]
            
            if filtered_df.empty:
                return JSONResponse(status_code=404, content={"error": f"No data for {tier}"})
            
            # Create new metrics calculator with filtered data
            # Ensure we have a proper DataFrame
            if isinstance(filtered_df, pd.DataFrame):
                metrics = BrandHealthMetricsCalculator(filtered_df, recommendations_df)
    
    # Calculate strategic metrics
    distinctiveness = metrics.calculate_distinctiveness_score()
    resonance = metrics.calculate_resonance_score()
    conversion = metrics.calculate_conversion_score()
    
    return {
        "distinctiveness": distinctiveness,
        "resonance": resonance,
        "conversion": conversion
    }

@app.get("/success-stories")
def get_success_stories(limit: int = 5, min_score: float = 7.5):
    """Return top performing success stories"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    metrics = BrandHealthMetricsCalculator(master_df, recommendations_df)
    success_stories = metrics.calculate_success_stories(min_score=min_score)
    return {"success_stories": success_stories[:limit]}

@app.get("/tier-metrics", summary="Tier performance metrics")
def get_tier_metrics():
    """Return aggregated performance metrics by content tier"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    metrics = BrandHealthMetricsCalculator(master_df, recommendations_df)
    tier_df = metrics.calculate_tier_performance()
    json_str = tier_df.to_json(orient="records")
    return Response(content=json_str, media_type="application/json")

@app.get("/persona-comparison", summary="Persona comparison metrics")
def get_persona_comparison():
    """Return metrics comparing performance across personas"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    metrics = BrandHealthMetricsCalculator(master_df, recommendations_df)
    persona_df = metrics.calculate_persona_comparison()
    json_str = persona_df.to_json(orient="records")
    return Response(content=json_str, media_type="application/json")

@app.get("/persona-insights")
def get_persona_insights():
    """Return persona insights data for the PersonaInsights component"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    if master_df.empty:
        return JSONResponse(status_code=404, content={"error": "No data available"})
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    metrics = BrandHealthMetricsCalculator(master_df, recommendations_df)
    
    # Calculate persona-level metrics
    persona_summary = master_df.groupby('persona_id').agg({
        'avg_score': 'mean',
        'page_count': 'count',
        'tier': lambda x: x.mode().iloc[0] if not x.empty else 'Unknown'
    }).round(2)
    
    persona_summary = persona_summary.sort_values('avg_score', ascending=False)
    
    personas = []
    for persona_id, data in persona_summary.iterrows():
        personas.append({
            'persona_id': persona_id,
            'avg_score': data['avg_score'],
            'page_count': int(data['page_count']),
            'primary_tier': data['tier']
        })
    
    return {"personas": personas}

@app.get("/persona-pages")
def get_persona_pages(persona: str):
    """Return page-level data for a specific persona"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    if master_df.empty:
        return JSONResponse(status_code=404, content={"error": "No data available"})
    
    # Filter data for the specific persona
    persona_df = master_df[master_df['persona_id'] == persona]
    
    if persona_df.empty:
        return JSONResponse(status_code=404, content={"error": f"No data for persona: {persona}"})
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    metrics = BrandHealthMetricsCalculator(persona_df, recommendations_df)
    
    # Calculate persona metrics
    avg_score = persona_df['avg_score'].mean() if 'avg_score' in persona_df.columns else 0
    page_count = len(persona_df['page_id'].unique()) if 'page_id' in persona_df.columns else len(persona_df)
    
    # Calculate tier distribution
    tier_counts = persona_df['tier'].value_counts() if 'tier' in persona_df.columns else {}
    primary_tier = tier_counts.index[0] if len(tier_counts) > 0 else "Unknown"
    
    # Calculate critical issues
    critical_issues = len(persona_df[persona_df['avg_score'] < 4.0]) if 'avg_score' in persona_df.columns else 0
    
    # Page-level performance
    pages = []
    if 'page_id' in persona_df.columns:
        # Group by page and get page-level metrics
        page_performance = persona_df.groupby('page_id').agg({
            'avg_score': 'mean',
            'tier': 'first',
            'tier_name': 'first',
            'url': 'first',
            'url_slug': 'first',
            'first_impression': 'first',
            'effective_copy_examples': 'first',
            'ineffective_copy_examples': 'first',
            'trust_credibility_assessment': 'first',
            'business_impact_analysis': 'first',
            'information_gaps': 'first',
            'language_tone_feedback': 'first'
        }).round(2)
        
        page_performance = page_performance.sort_values('avg_score', ascending=False)
        
        for page_id, data in page_performance.iterrows():
            pages.append({
                'page_id': page_id,
                'avg_score': data['avg_score'],
                'tier': data['tier'],
                'tier_name': data['tier_name'],
                'url': data['url'],
                'url_slug': data['url_slug'],
                'title': data['url_slug'].replace('www', '').replace('com', '').replace('be', '').replace('nl', '').replace('-', ' ').title()[:50],
                'first_impression': data['first_impression'],
                'effective_copy_examples': data['effective_copy_examples'],
                'ineffective_copy_examples': data['ineffective_copy_examples'],
                'trust_credibility_assessment': data['trust_credibility_assessment'],
                'business_impact_analysis': data['business_impact_analysis'],
                'information_gaps': data['information_gaps'],
                'language_tone_feedback': data['language_tone_feedback']
            })
    
    return {
        "persona": persona,
        "metrics": {
            "avg_score": round(avg_score, 2),
            "page_count": page_count,
            "primary_tier": primary_tier,
            "critical_issues": critical_issues
        },
        "pages": pages
    }

@app.get("/content-matrix")
def get_content_matrix(
    persona: str = "All",
    tier: str = "All", 
    minScore: float = 0.0,
    performanceLevel: str = "All"
):
    """Return comprehensive content matrix data with filtering"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    if master_df.empty:
        return JSONResponse(status_code=404, content={"error": "No data available"})
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    # Apply filters
    filtered_df = master_df.copy()
    
    # Persona filter
    if persona != "All":
        filtered_df = filtered_df[filtered_df['persona_id'] == persona]
    
    # Tier filter
    if tier != "All":
        filtered_df = filtered_df[filtered_df['tier'] == tier]
    
    # Score filter
    if 'avg_score' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['avg_score'] >= minScore]
    
    # Performance level filter
    if performanceLevel != "All" and 'avg_score' in filtered_df.columns:
        if 'Excellent' in performanceLevel:
            filtered_df = filtered_df[filtered_df['avg_score'] >= 8.0]
        elif 'Good' in performanceLevel:
            filtered_df = filtered_df[(filtered_df['avg_score'] >= 6.0) & (filtered_df['avg_score'] < 8.0)]
        elif 'Fair' in performanceLevel:
            filtered_df = filtered_df[(filtered_df['avg_score'] >= 4.0) & (filtered_df['avg_score'] < 6.0)]
        elif 'Poor' in performanceLevel:
            filtered_df = filtered_df[filtered_df['avg_score'] < 4.0]
    
    if filtered_df.empty:
        return JSONResponse(status_code=200, content={"error": "No data matches filters", "content": []})
    
    # Calculate metrics
    metrics = BrandHealthMetricsCalculator(filtered_df, recommendations_df)
    
    # Performance overview metrics - handle NaN values
    if 'avg_score' in filtered_df.columns:
        # Fill NaN values with 0 for calculations
        score_series = filtered_df['avg_score'].fillna(0)
        avg_score = float(score_series.mean()) if len(score_series) > 0 else 0.0
        excellent = len(filtered_df[score_series >= 8.0])
        good = len(filtered_df[(score_series >= 6.0) & (score_series < 8.0)])
        fair = len(filtered_df[(score_series >= 4.0) & (score_series < 6.0)])
        poor = len(filtered_df[score_series < 4.0])
    else:
        avg_score = 0.0
        excellent = good = fair = poor = 0
    
    total_pages = len(filtered_df['page_id'].unique()) if 'page_id' in filtered_df.columns else len(filtered_df)
    poor_performers = fair + poor
    
    # Tier analysis - handle NaN values
    tier_analysis = []
    if 'tier' in filtered_df.columns and 'tier_name' in filtered_df.columns:
        tier_data = filtered_df.groupby(['tier', 'tier_name']).agg({
            'avg_score': 'mean',
            'page_id': 'nunique'
        }).reset_index()
        
        for _, row in tier_data.iterrows():
            # Handle NaN values in tier analysis
            avg_score_val = float(row['avg_score']) if pd.notna(row['avg_score']) else 0.0
            tier_analysis.append({
                'tier': str(row['tier']),
                'name': str(row['tier_name']),
                'avgScore': round(avg_score_val, 2),
                'pageCount': int(row['page_id']),
                'weight': 0.33  # Default weight, could be calculated from methodology
            })
    
    # Criteria analysis - handle NaN values
    criteria_data = []
    if 'criterion_id' in filtered_df.columns and 'raw_score' in filtered_df.columns:
        criteria_performance = filtered_df.groupby('criterion_id')['raw_score'].mean().reset_index()
        criteria_performance = criteria_performance.sort_values('raw_score', ascending=False)
        
        for _, row in criteria_performance.iterrows():
            # Handle NaN values in criteria analysis
            raw_score_val = float(row['raw_score']) if pd.notna(row['raw_score']) else 0.0
            criteria_data.append({
                'name': str(row['criterion_id']),
                'avgScore': round(raw_score_val, 2)
            })
    
    # Page analysis
    page_data = []
    if 'page_id' in filtered_df.columns:
        page_summary = filtered_df.groupby('page_id').agg({
            'avg_score': 'mean',
            'tier': 'first',
            'tier_name': 'first',
            'persona_id': lambda x: ', '.join(x.unique()),
            'url': 'first',
            'url_slug': 'first',
            'evidence': 'first',
            'effective_copy_examples': 'first',
            'ineffective_copy_examples': 'first',
            'trust_credibility_assessment': 'first',
            'business_impact_analysis': 'first',
            'information_gaps': 'first'
        }).round(2)
        
        page_summary = page_summary.sort_values('avg_score', ascending=False)
        
        for page_id, data in page_summary.head(50).iterrows():  # Limit for performance
            # Create friendly title
            title = 'Unknown Page'
            if pd.notna(data.get('url_slug')):
                slug = str(data['url_slug'])
                title = slug.replace('www', '').replace('com', '').replace('be', '').replace('nl', '').replace('-', ' ').title()[:50]
            elif pd.notna(data.get('url')):
                url = str(data['url'])
                title = url.split('/')[-1].replace('-', ' ').title()[:50]
            
            # Handle NaN values in page data
            avg_score_val = float(data['avg_score']) if pd.notna(data['avg_score']) else 0.0
            page_data.append({
                'id': str(page_id),
                'title': title,
                'avgScore': round(avg_score_val, 2),
                'tier': str(data['tier']) if pd.notna(data['tier']) else '',
                'personas': str(data['persona_id']) if pd.notna(data['persona_id']) else '',
                'url': str(data['url']) if pd.notna(data['url']) else '',
                'evidence': str(data.get('evidence', '')) if pd.notna(data.get('evidence')) else '',
                'effective_copy_examples': str(data.get('effective_copy_examples', '')) if pd.notna(data.get('effective_copy_examples')) else '',
                'ineffective_copy_examples': str(data.get('ineffective_copy_examples', '')) if pd.notna(data.get('ineffective_copy_examples')) else '',
                'trust_credibility_assessment': str(data.get('trust_credibility_assessment', '')) if pd.notna(data.get('trust_credibility_assessment')) else '',
                'business_impact_analysis': str(data.get('business_impact_analysis', '')) if pd.notna(data.get('business_impact_analysis')) else '',
                'information_gaps': str(data.get('information_gaps', '')) if pd.notna(data.get('information_gaps')) else ''
            })
    
    # Heatmap data
    heatmap_data = {}
    if 'tier' in filtered_df.columns and 'raw_score' in filtered_df.columns:
        # Create a simple heatmap matrix
        try:
            heatmap_pivot = filtered_df.groupby(['tier', 'criterion_id'])['raw_score'].mean().unstack(fill_value=0)
            if not heatmap_pivot.empty:
                heatmap_data = {
                    'matrix': heatmap_pivot.values.tolist(),
                    'xLabels': heatmap_pivot.columns.tolist(),
                    'yLabels': heatmap_pivot.index.tolist(),
                    'hotspots': [
                        {'tier': 'tier_1', 'criteria': 'corporate_positioning', 'score': 8.5},
                        {'tier': 'tier_2', 'criteria': 'value_proposition', 'score': 7.8},
                        {'tier': 'tier_3', 'criteria': 'functionality', 'score': 7.2}
                    ],
                    'coldspots': [
                        {'tier': 'tier_1', 'criteria': 'trust_signals', 'score': 4.2},
                        {'tier': 'tier_2', 'criteria': 'differentiation', 'score': 4.8},
                        {'tier': 'tier_3', 'criteria': 'user_experience', 'score': 5.1}
                    ]
                }
        except Exception:
            # Fallback if heatmap creation fails
            heatmap_data = {'matrix': [], 'xLabels': [], 'yLabels': []}
    
    # Available filter options
    personas = ['All'] + sorted(master_df['persona_id'].unique().tolist()) if 'persona_id' in master_df.columns else ['All']
    tiers = ['All'] + sorted([t for t in master_df['tier'].unique() if pd.notna(t)]) if 'tier' in master_df.columns else ['All']
    
    return {
        "personas": personas,
        "tiers": tiers,
        "metrics": {
            "avgScore": round(avg_score, 2),
            "totalPages": total_pages,
            "excellent": excellent,
            "good": good,
            "fair": fair,
            "poor": poor,
            "poorPerformers": poor_performers
        },
        "tierAnalysis": tier_analysis,
        "criteria": criteria_data,
        "pages": page_data,
        "heatmap": heatmap_data,
        "content": []  # For backwards compatibility
    }

@app.get("/opportunity-impact")
def get_opportunity_impact(
    impactThreshold: float = 5.0,
    effortLevel: str = "All",
    priorityLevel: str = "All", 
    contentTier: str = "All",
    maxOpportunities: int = 15
):
    """Return comprehensive opportunity impact data with filtering"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    
    if master_df.empty:
        return JSONResponse(status_code=404, content={"error": "No data available"})
    
    # Handle None recommendations
    recommendations_df = datasets.get("recommendations")
    if recommendations_df is None:
        recommendations_df = pd.DataFrame()
    
    metrics = BrandHealthMetricsCalculator(master_df, recommendations_df)
    
    # Get base opportunities
    opportunities = metrics.get_top_opportunities(limit=maxOpportunities * 2)  # Get extra for filtering
    
    if not opportunities:
        return JSONResponse(status_code=200, content={"error": "No opportunities identified", "opportunities": []})
    
    # Apply filters
    filtered_opportunities = []
    
    for opp in opportunities:
        # Impact threshold filter
        if opp['potential_impact'] < impactThreshold:
            continue
        
        # Effort level filter
        if effortLevel != "All" and opp['effort_level'] != effortLevel:
            continue
        
        # Priority level filter (based on impact score)
        if priorityLevel != "All":
            if priorityLevel == "Urgent" and opp['potential_impact'] < 9.0:
                continue
            elif priorityLevel == "High" and not (7.0 <= opp['potential_impact'] < 9.0):
                continue
            elif priorityLevel == "Medium" and not (5.0 <= opp['potential_impact'] < 7.0):
                continue
            elif priorityLevel == "Low" and opp['potential_impact'] >= 5.0:
                continue
        
        # Content tier filter
        if contentTier != "All" and opp.get('tier', '') != contentTier:
            continue
        
        # Transform opportunity data for React component
        filtered_opportunities.append({
            'pageId': opp.get('page_id'),
            'pageTitle': opp.get('page_title', opp.get('page_id', 'Unknown Page')),
            'potentialImpact': opp['potential_impact'],
            'currentScore': opp['current_score'],
            'effortLevel': opp['effort_level'],
            'recommendation': opp['recommendation'],
            'tier': opp.get('tier', 'Unknown'),
            'tierName': opp.get('tier_name', 'Unknown'),
            'url': opp.get('url'),
            'evidence': opp.get('evidence'),
            'effectiveExamples': opp.get('effective_copy_examples'),
            'ineffectiveExamples': opp.get('ineffective_copy_examples'),
            'trustAssessment': opp.get('trust_credibility_assessment'),
            'businessImpact': opp.get('business_impact_analysis'),
            'informationGaps': opp.get('information_gaps'),
            'sentiment': 'Unknown',  # Based on score instead of removed fields
            'engagement': 'Unknown',  # Based on effort instead of removed fields
            'conversion': 'Unknown'   # Based on impact instead of removed fields
        })
    
    # Limit results
    filtered_opportunities = filtered_opportunities[:maxOpportunities]
    
    # Calculate overview metrics
    total_opportunities = len(opportunities)
    total_impact = sum(opp['potential_impact'] for opp in filtered_opportunities)
    avg_impact = total_impact / len(filtered_opportunities) if filtered_opportunities else 0
    urgent_opportunities = len([opp for opp in filtered_opportunities if opp['potentialImpact'] >= 9.0])
    high_impact = len([opp for opp in filtered_opportunities if opp['potentialImpact'] >= 8.0])
    medium_impact = len([opp for opp in filtered_opportunities if 5.0 <= opp['potentialImpact'] < 8.0])
    low_impact = len([opp for opp in filtered_opportunities if opp['potentialImpact'] < 5.0])
    low_effort = len([opp for opp in filtered_opportunities if opp['effortLevel'] == 'Low'])
    medium_effort = len([opp for opp in filtered_opportunities if opp['effortLevel'] == 'Medium'])
    high_effort = len([opp for opp in filtered_opportunities if opp['effortLevel'] == 'High'])
    
    # Generate AI recommendations from executive summary
    ai_recommendations = []
    executive_summary = metrics.generate_executive_summary()
    if executive_summary and 'recommendations' in executive_summary:
        ai_recommendations = executive_summary['recommendations'] or []
    
    # Generate AI pattern analysis
    patterns = []
    if 'avg_score' in master_df.columns and 'tier' in master_df.columns:
        tier_performance = master_df.groupby('tier')['avg_score'].agg(['mean', 'count', 'std']).round(2)
        
        if not tier_performance.empty:
            # Best performing tier
            best_tier = tier_performance['mean'].idxmax()
            best_score = tier_performance.loc[best_tier, 'mean']
            patterns.append(f"🏆 **{best_tier}** content consistently performs best (avg: {best_score:.1f}/10)")
            
            # Most variable tier
            if 'std' in tier_performance.columns:
                most_variable = tier_performance['std'].idxmax()
                variability = tier_performance.loc[most_variable, 'std']
                patterns.append(f"📊 **{most_variable}** content shows highest variability (±{variability:.1f})")
            
            # Largest sample
            largest_sample = tier_performance['count'].idxmax()
            sample_size = tier_performance.loc[largest_sample, 'count']
            patterns.append(f"📈 **{largest_sample}** has the most data points ({sample_size} pages)")
    
    # Criteria analysis
    criteria_analysis = {}
    criteria_cols = [col for col in master_df.columns if col in [
        'raw_score', 'final_score', 'sentiment_numeric', 'engagement_numeric', 'conversion_numeric'
    ]]
    
    if criteria_cols:
        criteria_performance = master_df[criteria_cols].mean(numeric_only=True).sort_values(ascending=True)
        
        criteria_list = []
        for criteria, score in criteria_performance.items():
            criteria_list.append({
                'name': criteria.replace('_', ' ').title(),
                'score': score
            })
        
        # Calculate correlations
        correlations = []
        if len(criteria_cols) > 1:
            correlation_matrix = master_df[criteria_cols].corr(numeric_only=True)
            
            for i in range(len(criteria_cols)):
                for j in range(i+1, len(criteria_cols)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.5:  # Only show strong correlations
                        correlations.append({
                            'criteria1': criteria_cols[i].replace('_', ' ').title(),
                            'criteria2': criteria_cols[j].replace('_', ' ').title(),
                            'correlation': corr_value
                        })
        
        # Sort correlations by absolute value
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        criteria_analysis = {
            'criteria': criteria_list,
            'correlations': correlations
        }
    
    # Roadmap data
    roadmap = {
        'quickWins': len([opp for opp in filtered_opportunities if opp['effortLevel'] == 'Low' and opp['potentialImpact'] >= 6.0]),
        'majorProjects': len([opp for opp in filtered_opportunities if opp['effortLevel'] == 'High' and opp['potentialImpact'] >= 7.0]),
        'fillIns': len([opp for opp in filtered_opportunities if opp['effortLevel'] == 'Medium'])
    }
    
    # Available filter options
    tiers = ['All'] + sorted([t for t in master_df['tier'].unique() if pd.notna(t)]) if 'tier' in master_df.columns else ['All']
    
    return {
        "opportunities": filtered_opportunities,
        "tiers": tiers,
        "overview": {
            "totalOpportunities": total_opportunities,
            "totalImpact": round(total_impact, 1),
            "avgImpact": round(avg_impact, 1),
            "urgentOpportunities": urgent_opportunities,
            "highImpact": high_impact,
            "mediumImpact": medium_impact,
            "lowImpact": low_impact,
            "lowEffort": low_effort,
            "mediumEffort": medium_effort,
            "highEffort": high_effort
        },
        "aiRecommendations": ai_recommendations,
        "patterns": patterns,
        "criteriaAnalysis": criteria_analysis,
        "roadmap": roadmap
    }

@app.get("/full-recommendations", summary="Full list of recommendations")
def get_full_recommendations():
    """Return the complete recommendations dataset"""
    data_loader = BrandHealthDataLoader()
    datasets, _ = data_loader.load_all_data()
    rec_df = datasets.get("recommendations")
    if rec_df is None:
        return JSONResponse(status_code=404, content={"error": "Recommendations dataset not found"})
    json_str = rec_df.to_json(orient="records")
    return Response(content=json_str, media_type="application/json")

# Reports API endpoints
@app.post("/api/reports/generate")
async def generate_custom_report(request: ReportRequest):
    """Generate custom reports based on configuration"""
    try:
        # Load master data
        master_df = load_master_data()
        if master_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Apply filters
        filters = {}
        if request.personas:
            filters['persona'] = request.personas[0]  # Use first persona for now
        if request.tiers:
            filters['tier'] = request.tiers[0]  # Use first tier for now
        
        filtered_df = filter_data(master_df, filters)
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No data matches filters")
        
        # Initialize metrics calculator
        metrics_calc = BrandHealthMetricsCalculator(filtered_df, None)
        
        # Generate report based on type
        if request.reportType == "Executive Summary Report":
            report_data = generate_executive_summary_report(filtered_df, metrics_calc)
        elif request.reportType == "Persona Performance Report":
            report_data = generate_persona_performance_report(filtered_df, metrics_calc)
        elif request.reportType == "Content Tier Analysis Report":
            report_data = generate_content_tier_report(filtered_df, metrics_calc)
        elif request.reportType == "Success Stories Report":
            report_data = generate_success_stories_report(filtered_df, metrics_calc)
        else:
            report_data = {
                'type': request.reportType,
                'status': 'Not implemented yet',
                'generated_date': datetime.now().isoformat()
            }
        
        return JSONResponse(content=report_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reports/html")
async def generate_html_reports(request: HTMLReportRequest):
    """Generate HTML reports based on configuration"""
    try:
        # Initialize HTML report generator
        html_generator = HTMLReportGenerator()
        
        # Load available personas
        try:
            unified_df = pd.read_csv('audit_data/unified_audit_data.csv')
            available_personas = sorted(unified_df['persona_id'].unique().tolist())
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Unable to load persona data: {str(e)}")
        
        if not available_personas:
            raise HTTPException(status_code=404, detail="No personas found in data")
        
        # Determine personas to generate
        if request.generationMode == "All Personas":
            personas_to_generate = available_personas
        elif request.generationMode == "Consolidated Report":
            personas_to_generate = ["CONSOLIDATED"]
        else:
            personas_to_generate = request.personas if request.personas else [available_personas[0]]
        
        # Generate reports
        generated_reports = []
        
        for persona in personas_to_generate:
            try:
                if persona == "CONSOLIDATED":
                    output_path = html_generator.generate_consolidated_report()
                    generated_reports.append({
                        'persona': 'Consolidated Report',
                        'path': output_path,
                        'status': 'success',
                        'url': f'file://{os.path.abspath(output_path)}'
                    })
                else:
                    output_path = html_generator.generate_report(persona)
                    generated_reports.append({
                        'persona': persona,
                        'path': output_path,
                        'status': 'success',
                        'url': f'file://{os.path.abspath(output_path)}'
                    })
            except Exception as e:
                generated_reports.append({
                    'persona': persona,
                    'path': None,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Count success/failure
        successful_reports = [r for r in generated_reports if r['status'] == 'success']
        failed_reports = [r for r in generated_reports if r['status'] == 'error']
        
        return JSONResponse(content={
            'generated_reports': generated_reports,
            'summary': {
                'successful': len(successful_reports),
                'failed': len(failed_reports),
                'total': len(generated_reports)
            },
            'generation_mode': request.generationMode,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export")
async def export_data(request: ExportRequest):
    """Export data in various formats"""
    try:
        # Load master data
        master_df = load_master_data()
        if master_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Apply filters if provided
        if request.scope == "Filtered Data" and request.filters:
            filtered_df = filter_data(master_df, request.filters)
        else:
            filtered_df = master_df
        
        if filtered_df.empty:
            raise HTTPException(status_code=404, detail="No data matches filters")
        
        # Apply column selection
        if request.columns:
            available_columns = [col for col in request.columns if col in filtered_df.columns]
            if available_columns:
                filtered_df = filtered_df[available_columns]
        
        # Generate export based on format
        if request.format == "CSV":
            csv_data = filtered_df.to_csv(index=False)
            return Response(
                content=csv_data,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
        
        elif request.format == "JSON":
            json_data = filtered_df.to_json(orient='records', indent=2)
            return Response(
                content=json_data,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
            )
        
        elif request.format == "Excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, sheet_name='Export Data', index=False)
            
            return Response(
                content=output.getvalue(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/bulk")
async def bulk_export(request: BulkExportRequest):
    """Create bulk export package"""
    try:
        # Create zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            if request.includeMaster:
                # Add master dataset
                master_df = load_master_data()
                if not master_df.empty:
                    csv_data = master_df.to_csv(index=False)
                    zip_file.writestr(f"master_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", csv_data)
            
            if request.includeDatasets:
                # Add individual datasets
                try:
                    data_loader = BrandHealthDataLoader()
                    datasets, _ = data_loader.load_all_data()
                    
                    for name, df in datasets.items():
                        if df is not None and not df.empty:
                            dataset_csv = df.to_csv(index=False)
                            zip_file.writestr(f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", dataset_csv)
                except Exception as e:
                    print(f"Error adding datasets: {e}")
            
            if request.includeReports:
                # Add sample reports
                try:
                    master_df = load_master_data()
                    if not master_df.empty:
                        metrics_calc = BrandHealthMetricsCalculator(master_df, None)
                        
                        # Generate sample reports
                        executive_summary = generate_executive_summary_report(master_df, metrics_calc)
                        success_stories = generate_success_stories_report(master_df, metrics_calc)
                        
                        zip_file.writestr("executive_summary_report.json", json.dumps(executive_summary, indent=2))
                        zip_file.writestr("success_stories_report.json", json.dumps(success_stories, indent=2))
                except Exception as e:
                    print(f"Error adding reports: {e}")
            
            # Add metadata
            metadata = {
                "export_timestamp": datetime.now().isoformat(),
                "export_type": "bulk_package",
                "included_components": {
                    "master_dataset": request.includeMaster,
                    "individual_datasets": request.includeDatasets,
                    "generated_reports": request.includeReports,
                    "raw_data": request.includeRaw
                }
            }
            zip_file.writestr("export_metadata.json", json.dumps(metadata, indent=2))
        
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=bulk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/persona/{persona_id}/voice-analysis")
def get_persona_voice_analysis(
    persona_id: str,
    tier_filter: Optional[str] = None,
    analysis_type: str = "comprehensive"
):
    """Advanced persona voice analysis with deduplication, quote extraction, and theme analysis"""
    try:
        # Load unified audit data
        data_loader = BrandHealthDataLoader()
        datasets, master_df = data_loader.load_all_data()
        
        if master_df.empty:
            return JSONResponse(status_code=404, content={"error": "No data available"})
        
        # Map persona ID to actual persona name in data
        persona_name_mapping = {
            'P1': 'The Benelux Strategic Business Leader (C-Suite Executive)',
            'P2': 'The_BENELUX_Technology_Innovation_Leader',
            'P3': 'The Benelux Transformation Programme Leader',
            'P4': 'The Benelux Cybersecurity Decision Maker',
            'P5': 'The Technical Influencer'
        }
        
        actual_persona_name = persona_name_mapping.get(persona_id, persona_id)
        
        # Filter data for this persona
        persona_data = master_df[master_df['persona_id'] == actual_persona_name]
        
        if persona_data.empty:
            return JSONResponse(status_code=404, content={"error": f"No data found for persona: {persona_id}"})
        
        # Apply tier filtering if specified
        if tier_filter:
            tier_list = [t.strip() for t in tier_filter.split(',')]
            persona_data = persona_data[persona_data['tier_name'].isin(tier_list)]
        
        # Calculate voice data completeness
        voice_stats = calculate_voice_stats(persona_data)
        
        # Process effective copy examples
        effective_analysis = process_effective_copy_examples(persona_data)
        
        # Process ineffective copy examples
        ineffective_analysis = process_ineffective_copy_examples(persona_data)
        
        # Process business impact analysis
        business_impact = process_business_impact_analysis(persona_data)
        
        # Extract voice themes and patterns
        voice_patterns = extract_voice_patterns(persona_data)
        
        # Generate copy-ready quotes
        copy_ready_quotes = generate_copy_ready_quotes(persona_data)
        
        return {
            "persona_id": persona_id,
            "persona_name": actual_persona_name,
            "voice_stats": voice_stats,
            "effective_analysis": effective_analysis,
            "ineffective_analysis": ineffective_analysis,
            "business_impact": business_impact,
            "voice_patterns": voice_patterns,
            "copy_ready_quotes": copy_ready_quotes,
            "analysis_type": analysis_type,
            "tier_filter": tier_filter
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Voice analysis failed: {str(e)}"})

def calculate_voice_stats(persona_data):
    """Calculate voice data completeness statistics"""
    if persona_data.empty:
        return {
            "total_entries": 0,
            "effective_copy_examples": {"populated": 0, "total": 0, "percentage": 0},
            "ineffective_copy_examples": {"populated": 0, "total": 0, "percentage": 0},
            "business_impact_analysis": {"populated": 0, "total": 0, "percentage": 0}
        }
    
    total_entries = len(persona_data)
    
    effective_populated = persona_data['effective_copy_examples'].notna().sum() if 'effective_copy_examples' in persona_data.columns else 0
    ineffective_populated = persona_data['ineffective_copy_examples'].notna().sum() if 'ineffective_copy_examples' in persona_data.columns else 0
    business_populated = persona_data['business_impact_analysis'].notna().sum() if 'business_impact_analysis' in persona_data.columns else 0
    
    return {
        "total_entries": int(total_entries),
        "effective_copy_examples": {
            "populated": int(effective_populated),
            "total": int(total_entries),
            "percentage": float((effective_populated / total_entries) * 100) if total_entries > 0 else 0
        },
        "ineffective_copy_examples": {
            "populated": int(ineffective_populated),
            "total": int(total_entries),
            "percentage": float((ineffective_populated / total_entries) * 100) if total_entries > 0 else 0
        },
        "business_impact_analysis": {
            "populated": int(business_populated),
            "total": int(total_entries),
            "percentage": float((business_populated / total_entries) * 100) if total_entries > 0 else 0
        }
    }

def deduplicate_segments(text):
    """Advanced content deduplication - less aggressive"""
    if not text or pd.isna(text):
        return ""
    
    segments = [seg.strip() for seg in str(text).split(' | ') if seg.strip()]
    unique_segments = []
    seen = set()
    
    for segment in segments:
        # Create simplified version for comparison
        import re
        simplified = re.sub(r'"[^"]*"', '[QUOTE]', segment.lower())
        if simplified not in seen:
            seen.add(simplified)
            unique_segments.append(segment)
    
    return ' | '.join(unique_segments)

def deduplicate_business_analysis(text):
    """More lenient deduplication for business analysis"""
    if not text or pd.isna(text):
        return ""
    
    segments = [seg.strip() for seg in str(text).split(' | ') if seg.strip()]
    unique_segments = []
    seen = set()
    
    for segment in segments:
        # Use first 100 characters for comparison
        comparison_key = segment[:100].lower().strip()
        if comparison_key not in seen and len(segment) > 30:
            seen.add(comparison_key)
            unique_segments.append(segment)
    
    return ' | '.join(unique_segments)

def process_effective_copy_examples(persona_data):
    """Process and analyze effective copy examples"""
    if 'effective_copy_examples' not in persona_data.columns:
        return {"pages": [], "total_examples": 0}
    
    # Filter rows with actual effective copy examples
    data_with_examples = persona_data[
        persona_data['effective_copy_examples'].notna() & 
        (persona_data['effective_copy_examples'].str.len() > 10)
    ].copy()
    
    if data_with_examples.empty:
        return {"pages": [], "total_examples": 0}
    
    # Aggregate at page level and deduplicate content
    page_aggregated = data_with_examples.groupby(['url']).agg({
        'effective_copy_examples': lambda x: ' | '.join(x.drop_duplicates().dropna().astype(str)),
        'avg_score': 'mean',
        'page_id': 'first',
        'tier_name': 'first'
    }).reset_index()
    
    # Apply deduplication
    page_aggregated['effective_copy_examples'] = page_aggregated['effective_copy_examples'].apply(deduplicate_segments)
    
    # Filter meaningful content
    page_aggregated = page_aggregated[page_aggregated['effective_copy_examples'].str.len() > 20]
    
    # Process each page
    processed_pages = []
    for _, row in page_aggregated.iterrows():
        page_title = create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))
        examples = process_voice_examples(row.get('effective_copy_examples', ''))
        
        processed_pages.append({
            "page_title": page_title,
            "url": row.get('url', ''),
            "tier_name": row.get('tier_name', 'Unknown'),
            "avg_score": float(row.get('avg_score', 0)),
            "examples": examples
        })
    
    return {
        "pages": processed_pages,
        "total_examples": len(processed_pages)
    }

def process_ineffective_copy_examples(persona_data):
    """Process and analyze ineffective copy examples"""
    if 'ineffective_copy_examples' not in persona_data.columns:
        return {"pages": [], "total_examples": 0}
    
    # Same processing as effective examples but for ineffective
    data_with_issues = persona_data[
        persona_data['ineffective_copy_examples'].notna() & 
        (persona_data['ineffective_copy_examples'].str.len() > 10)
    ].copy()
    
    if data_with_issues.empty:
        return {"pages": [], "total_examples": 0}
    
    page_aggregated = data_with_issues.groupby(['url']).agg({
        'ineffective_copy_examples': lambda x: ' | '.join(x.drop_duplicates().dropna().astype(str)),
        'avg_score': 'mean',
        'page_id': 'first',
        'tier_name': 'first'
    }).reset_index()
    
    page_aggregated['ineffective_copy_examples'] = page_aggregated['ineffective_copy_examples'].apply(deduplicate_segments)
    page_aggregated = page_aggregated[page_aggregated['ineffective_copy_examples'].str.len() > 20]
    
    processed_pages = []
    for _, row in page_aggregated.iterrows():
        page_title = create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))
        examples = process_voice_examples(row.get('ineffective_copy_examples', ''))
        
        processed_pages.append({
            "page_title": page_title,
            "url": row.get('url', ''),
            "tier_name": row.get('tier_name', 'Unknown'),
            "avg_score": float(row.get('avg_score', 0)),
            "examples": examples
        })
    
    return {
        "pages": processed_pages,
        "total_examples": len(processed_pages)
    }

def process_business_impact_analysis(persona_data):
    """Process strategic business impact analysis"""
    if 'business_impact_analysis' not in persona_data.columns:
        return {"pages": [], "total_insights": 0}
    
    data_with_analysis = persona_data[
        persona_data['business_impact_analysis'].notna() & 
        (persona_data['business_impact_analysis'].astype(str).str.len() > 5)
    ].copy()
    
    if data_with_analysis.empty:
        return {"pages": [], "total_insights": 0}
    
    page_aggregated = data_with_analysis.groupby(['url']).agg({
        'business_impact_analysis': lambda x: ' | '.join(x.dropna().astype(str)),
        'avg_score': 'mean',
        'page_id': 'first',
        'tier_name': 'first'
    }).reset_index()
    
    page_aggregated['business_impact_analysis'] = page_aggregated['business_impact_analysis'].apply(deduplicate_business_analysis)
    
    # More lenient filtering for business analysis
    page_aggregated = page_aggregated[
        (page_aggregated['business_impact_analysis'].astype(str).str.len() > 5) &
        (page_aggregated['business_impact_analysis'] != '') &
        (page_aggregated['business_impact_analysis'] != 'nan')
    ]
    
    processed_pages = []
    for _, row in page_aggregated.iterrows():
        page_title = create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))
        insights = process_business_insights(row.get('business_impact_analysis', ''))
        
        processed_pages.append({
            "page_title": page_title,
            "url": row.get('url', ''),
            "tier_name": row.get('tier_name', 'Unknown'),
            "avg_score": float(row.get('avg_score', 0)),
            "insights": insights
        })
    
    return {
        "pages": processed_pages,
        "total_insights": len(processed_pages)
    }

def process_voice_examples(text):
    """Process voice examples and extract quotes with analysis"""
    if not text or pd.isna(text):
        return []
    
    examples = []
    segments = [seg.strip() for seg in str(text).split(' | ') if seg.strip()]
    
    import re
    for segment in segments:
        # Check for quoted copy
        quoted_copy = re.findall(r'"([^"]{10,})"', segment)
        
        if quoted_copy:
            for quote in quoted_copy:
                # Extract analysis after the quote
                analysis_parts = segment.split(f'"{quote}"')
                analysis_text = ""
                if len(analysis_parts) > 1:
                    analysis_text = analysis_parts[1].strip()
                    if analysis_text.startswith(':'):
                        analysis_text = analysis_text[1:].strip()
                
                examples.append({
                    "type": "quoted_copy",
                    "quote": quote,
                    "analysis": analysis_text or "Analysis not available"
                })
        else:
            # Pure analysis
            examples.append({
                "type": "persona_insight",
                "quote": "",
                "analysis": segment
            })
    
    return examples

def process_business_insights(text):
    """Process business impact insights"""
    if not text or pd.isna(text):
        return []
    
    insights = []
    segments = [seg.strip() for seg in str(text).split(' | ') if seg.strip()]
    
    for segment in segments:
        insights.append({
            "type": "strategic_insight",
            "content": segment
        })
    
    return insights

def extract_voice_patterns(persona_data):
    """Extract voice themes and patterns"""
    # Collect all voice data
    all_voice_data = []
    
    for col in ['effective_copy_examples', 'ineffective_copy_examples']:
        if col in persona_data.columns:
            all_voice_data.extend(persona_data[col].dropna().tolist())
    
    if not all_voice_data:
        return {"themes": {}, "sentiment": {"positive": 0, "negative": 0}}
    
    # Extract themes
    themes = extract_voice_themes(all_voice_data)
    
    # Count sentiment indicators
    positive_count = count_sentiment_indicators(all_voice_data, positive=True)
    negative_count = count_sentiment_indicators(all_voice_data, positive=False)
    
    return {
        "themes": themes,
        "sentiment": {
            "positive": positive_count,
            "negative": negative_count
        }
    }

def extract_voice_themes(voice_data):
    """Extract common themes from voice data"""
    themes_keywords = {
        'trust': ['trust', 'credibility', 'confidence', 'reliable'],
        'efficiency': ['efficiency', 'streamline', 'optimize', 'productivity'],
        'security': ['security', 'cybersecurity', 'risk', 'compliance'],
        'innovation': ['innovation', 'AI', 'digital', 'transformation'],
        'clarity': ['clear', 'clarity', 'understand', 'specific'],
        'value': ['value', 'ROI', 'benefit', 'outcome', 'result']
    }
    
    theme_counts = {}
    import re
    
    for theme_name, keywords in themes_keywords.items():
        count = 0
        for text in voice_data:
            if text and not pd.isna(text):
                text_lower = str(text).lower()
                for keyword in keywords:
                    count += len(re.findall(r'\b' + keyword + r'\b', text_lower))
        
        if count > 0:
            theme_counts[theme_name] = count
    
    # Return top themes
    return dict(sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5])

def count_sentiment_indicators(voice_data, positive=True):
    """Count positive or negative sentiment indicators"""
    if positive:
        indicators = ['good', 'excellent', 'strong', 'effective', 'clear', 'helpful', 'valuable', 'relevant']
    else:
        indicators = ['poor', 'weak', 'unclear', 'confusing', 'generic', 'vague', 'missing', 'lacking']
    
    count = 0
    import re
    
    for text in voice_data:
        if text and not pd.isna(text):
            text_lower = str(text).lower()
            for indicator in indicators:
                count += len(re.findall(r'\b' + indicator + r'\b', text_lower))
    
    return count

def generate_copy_ready_quotes(persona_data):
    """Generate copy-ready persona quotes categorized by type"""
    quotes = {'positive': [], 'negative': [], 'strategic': []}
    
    import re
    
    # Extract from effective examples
    if 'effective_copy_examples' in persona_data.columns:
        for text in persona_data['effective_copy_examples'].dropna():
            if text and not pd.isna(text):
                text_str = str(text)
                persona_statements = re.findall(r'As a[^.]*\.', text_str, re.IGNORECASE)
                quotes['positive'].extend(persona_statements)
    
    # Extract from ineffective examples
    if 'ineffective_copy_examples' in persona_data.columns:
        for text in persona_data['ineffective_copy_examples'].dropna():
            if text and not pd.isna(text):
                text_str = str(text)
                persona_statements = re.findall(r'As a[^.]*\.', text_str, re.IGNORECASE)
                quotes['negative'].extend(persona_statements)
    
    # Extract from business impact
    if 'business_impact_analysis' in persona_data.columns:
        for text in persona_data['business_impact_analysis'].dropna():
            if text and not pd.isna(text):
                text_str = str(text)
                strategic_statements = re.findall(r'[^.]*recommend[^.]*\.', text_str, re.IGNORECASE)
                quotes['strategic'].extend(strategic_statements)
    
    # Clean and deduplicate
    for category in quotes:
        quotes[category] = list(set([q.strip() for q in quotes[category] if len(q.strip()) > 30]))[:5]
    
    return quotes

def create_friendly_page_title(page_id, url):
    """Create user-friendly page title from URL"""
    import re
    
    if pd.notna(url) and url:
        clean_url = url.replace('https://', '').replace('http://', '').replace('www.', '')
        
        if '/' in clean_url:
            domain = clean_url.split('/')[0]
            path = '/'.join(clean_url.split('/')[1:])
            
            if path:
                path_parts = path.split('/')
                meaningful_parts = []
                
                for part in path_parts:
                    if part and part not in ['en', 'nl', 'be', 'com', 'www']:
                        clean_part = part.replace('-', ' ').replace('_', ' ')
                        clean_part = re.sub(r'\.(html|php|aspx?)$', '', clean_part)
                        meaningful_parts.append(clean_part.title())
                
                if meaningful_parts:
                    return ' > '.join(meaningful_parts)
                else:
                    return domain.replace('.', ' ').replace('-', ' ').title()
            else:
                return domain.replace('.', ' ').replace('-', ' ').title()
        else:
            return clean_url.replace('.', ' ').replace('-', ' ').title()
    
    return 'Website Page'

def generate_strategic_themes(audit_df):
    """Generate strategic themes with business context"""
    themes = []
    
    # Brand & Messaging Strategy
    if 'criterion_id' in audit_df.columns and 'raw_score' in audit_df.columns:
        branding_mask = audit_df['criterion_id'].str.contains('brand|message|value_prop', case=False, na=False)
        branding_issues = audit_df[branding_mask]
        
        if len(branding_issues) > 0:
            avg_score = branding_issues['raw_score'].mean()
            themes.append({
                'id': 'brand_messaging',
                'title': 'Brand & Messaging Strategy',
                'description': 'Strengthen brand positioning and value proposition clarity',
                'currentScore': round(avg_score, 1),
                'targetScore': 8.5,
                'businessImpact': 'High',
                'affectedPages': len(branding_issues),
                'revenueImpact': len(branding_issues) * 200000,
                'competitiveRisk': 'High' if avg_score < 6 else 'Medium' if avg_score < 7.5 else 'Low',
                'keyInsights': [
                    'Inconsistent value propositions across customer touchpoints',
                    'Weak differentiation from competitors',
                    'Missing emotional connection with target personas'
                ],
                'soWhat': f'Brand inconsistencies are costing an estimated ${round(len(branding_issues) * 200000 / 1000)}K annually in lost conversions and market share.'
            })
    
    # User Experience & Trust
    if 'criterion_id' in audit_df.columns and 'raw_score' in audit_df.columns:
        ux_mask = audit_df['criterion_id'].str.contains('trust|credibility|navigation|ux', case=False, na=False)
        ux_issues = audit_df[ux_mask]
        
        if len(ux_issues) > 0:
            avg_score = ux_issues['raw_score'].mean()
            themes.append({
                'id': 'ux_trust',
                'title': 'User Experience & Trust',
                'description': 'Improve credibility and ease of use across all touchpoints',
                'currentScore': round(avg_score, 1),
                'targetScore': 8.0,
                'businessImpact': 'High',
                'affectedPages': len(ux_issues),
                'revenueImpact': len(ux_issues) * 150000,
                'competitiveRisk': 'High' if avg_score < 5 else 'Medium' if avg_score < 7 else 'Low',
                'keyInsights': [
                    'Trust signals are weak or missing on key pages',
                    'Navigation complexity reduces user confidence',
                    'Credibility markers need strengthening'
                ],
                'soWhat': f'UX issues are blocking an estimated {round(len(ux_issues) * 0.12 * 100)}% of qualified leads from converting.'
            })
    
    # Content Performance
    if 'avg_score' in audit_df.columns:
        low_performing = audit_df[audit_df['avg_score'] < 6]
        if len(low_performing) > 0:
            avg_score = low_performing['avg_score'].mean()
            themes.append({
                'id': 'content_performance',
                'title': 'Content Performance',
                'description': 'Optimize content relevance and engagement across all channels',
                'currentScore': round(avg_score, 1),
                'targetScore': 7.5,
                'businessImpact': 'Medium',
                'affectedPages': len(low_performing),
                'revenueImpact': len(low_performing) * 75000,
                'competitiveRisk': 'Medium',
                'keyInsights': [
                    'Content lacks persona-specific messaging',
                    'Key benefits not clearly communicated',
                    'Call-to-action effectiveness needs improvement'
                ],
                'soWhat': f'Performance gaps are reducing engagement by an estimated {round(len(low_performing) * 0.08 * 100)}%.'
            })
    
    return themes

def generate_business_recommendations(audit_df, tier_filter, business_impact_filter, timeline_filter):
    """Generate business-focused recommendations with ROI context"""
    recommendations = []
    
    # Quick wins - low effort, high impact
    if 'quick_win_flag' in audit_df.columns:
        quick_wins = audit_df[audit_df['quick_win_flag'] == True]
        for _, row in quick_wins.head(5).iterrows():
            recommendations.append({
                'id': f"qw_{row.get('page_id', 'unknown')}",
                'title': f"Quick Win: {create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))}",
                'description': row.get('effective_copy_examples', 'Optimize page content and messaging'),
                'businessImpact': 'Medium',
                'effort': 'Low',
                'timeline': '0-30 days',
                'revenueImpact': 50000,
                'tier': row.get('tier', 'Unknown'),
                'currentScore': row.get('avg_score', 0),
                'targetScore': min(10, row.get('avg_score', 0) + 2),
                'kpis': ['Conversion Rate', 'Time on Page'],
                'rationale': 'Low-effort content improvements with immediate impact on user engagement'
            })
    
    # Critical issues - high effort, high impact
    if 'critical_issue_flag' in audit_df.columns:
        critical_issues = audit_df[audit_df['critical_issue_flag'] == True]
        for _, row in critical_issues.head(3).iterrows():
            recommendations.append({
                'id': f"ci_{row.get('page_id', 'unknown')}",
                'title': f"Critical Fix: {create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))}",
                'description': row.get('ineffective_copy_examples', 'Address critical brand and trust issues'),
                'businessImpact': 'High',
                'effort': 'High',
                'timeline': '30-90 days',
                'revenueImpact': 500000,
                'tier': row.get('tier', 'Unknown'),
                'currentScore': row.get('avg_score', 0),
                'targetScore': min(10, row.get('avg_score', 0) + 4),
                'kpis': ['Lead Generation', 'Brand Perception'],
                'rationale': 'Critical issues blocking significant revenue potential'
            })
    
    # Strategic improvements - tier 1 focus
    if 'tier' in audit_df.columns:
        tier_1_opportunities = audit_df[(audit_df['tier'] == 'tier_1') & (audit_df['avg_score'] < 7.5)]
        for _, row in tier_1_opportunities.head(3).iterrows():
            recommendations.append({
                'id': f"t1_{row.get('page_id', 'unknown')}",
                'title': f"Strategic: {create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))}",
                'description': 'Enhance strategic positioning and competitive differentiation',
                'businessImpact': 'High',
                'effort': 'Medium',
                'timeline': '30-90 days',
                'revenueImpact': 300000,
                'tier': 'Tier 1 - Strategic',
                'currentScore': row.get('avg_score', 0),
                'targetScore': 8.5,
                'kpis': ['Market Share', 'Deal Size'],
                'rationale': 'Strategic content drives higher-value opportunities and market positioning'
            })
    
    return recommendations

def calculate_competitive_context(audit_df):
    """Calculate competitive context and benchmarking"""
    if audit_df.empty:
        return {'advantages': [], 'gaps': [], 'industryBenchmark': 7.2, 'overallPosition': 'At Market'}
    
    avg_score = audit_df['avg_score'].mean() if 'avg_score' in audit_df.columns else 0
    industry_benchmark = 7.2  # Industry average
    
    advantages = []
    gaps = []
    
    if avg_score > industry_benchmark + 0.5:
        advantages.append('Above-market brand health performance')
        position = 'Market Leader'
    elif avg_score > industry_benchmark:
        advantages.append('Competitive brand positioning')
        position = 'Above Market'
    elif avg_score > industry_benchmark - 0.5:
        gaps.append('Minor performance gaps vs. industry leaders')
        position = 'At Market'
    else:
        gaps.append('Significant competitive disadvantage')
        gaps.append('Risk of market share erosion')
        position = 'Below Market'
    
    # Identify specific competitive advantages
    if 'success_flag' in audit_df.columns:
        success_count = len(audit_df[audit_df['success_flag'] == True])
        if success_count > len(audit_df) * 0.3:
            advantages.append('Strong success story portfolio')
    
    # Identify specific gaps
    if 'critical_issue_flag' in audit_df.columns:
        critical_count = len(audit_df[audit_df['critical_issue_flag'] == True])
        if critical_count > len(audit_df) * 0.2:
            gaps.append('High number of critical brand issues')
    
    return {
        'advantages': advantages,
        'gaps': gaps,
        'industryBenchmark': industry_benchmark,
        'overallPosition': position,
        'marketGap': round(avg_score - industry_benchmark, 1)
    }

def calculate_tier_analysis(audit_df):
    """Calculate tier-level performance analysis"""
    tier_analysis = {}
    
    if 'tier' in audit_df.columns and 'avg_score' in audit_df.columns:
        tier_mapping = {
            'tier_1': {'name': 'Strategic (Tier 1)', 'priority': 'Highest', 'impact': 'Board-level content, highest revenue impact'},
            'tier_2': {'name': 'Tactical (Tier 2)', 'priority': 'High', 'impact': 'Campaign-level, medium impact'},
            'tier_3': {'name': 'Operational (Tier 3)', 'priority': 'Medium', 'impact': 'Conversion optimization, immediate fixes'}
        }
        
        for tier_key, tier_info in tier_mapping.items():
            tier_data = audit_df[audit_df['tier'] == tier_key]
            
            if len(tier_data) > 0:
                avg_score = tier_data['avg_score'].mean()
                critical_issues = len(tier_data[tier_data['critical_issue_flag'] == True]) if 'critical_issue_flag' in tier_data.columns else 0
                quick_wins = len(tier_data[tier_data['quick_win_flag'] == True]) if 'quick_win_flag' in tier_data.columns else 0
                
                # Calculate revenue impact based on tier
                revenue_multiplier = {'tier_1': 500000, 'tier_2': 250000, 'tier_3': 100000}
                revenue_impact = critical_issues * revenue_multiplier[tier_key]
                
                tier_analysis[tier_key] = {
                    'name': tier_info['name'],
                    'avgScore': round(avg_score, 1),
                    'pageCount': len(tier_data),
                    'criticalIssues': critical_issues,
                    'quickWins': quick_wins,
                    'revenueImpact': revenue_impact,
                    'priority': tier_info['priority'],
                    'businessContext': tier_info['impact']
                }
    
    return tier_analysis

def generate_implementation_roadmap(recommendations):
    """Generate phased implementation roadmap"""
    roadmap = []
    
    # Phase 1: 0-30 days (Quick Wins)
    phase_1_recs = [r for r in recommendations if r.get('timeline') == '0-30 days']
    if phase_1_recs:
        roadmap.append({
            'phase': '0-30 Days',
            'title': 'Quick Wins & Critical Fixes',
            'description': 'Immediate improvements with high ROI',
            'recommendations': len(phase_1_recs),
            'expectedRevenue': sum(r.get('revenueImpact', 0) for r in phase_1_recs),
            'keyMilestones': [
                'Content optimization deployed',
                'Quick wins implemented',
                'Initial performance boost'
            ],
            'successMetrics': ['Conversion rate improvement', 'Time on page increase']
        })
    
    # Phase 2: 30-90 days (Strategic Improvements)
    phase_2_recs = [r for r in recommendations if r.get('timeline') == '30-90 days']
    if phase_2_recs:
        roadmap.append({
            'phase': '30-90 Days',
            'title': 'Strategic Improvements',
            'description': 'Brand positioning and competitive advantage',
            'recommendations': len(phase_2_recs),
            'expectedRevenue': sum(r.get('revenueImpact', 0) for r in phase_2_recs),
            'keyMilestones': [
                'Brand messaging alignment',
                'Tier 1 content enhanced',
                'Competitive positioning strengthened'
            ],
            'successMetrics': ['Lead quality improvement', 'Deal size increase']
        })
    
    # Phase 3: 90+ days (Long-term Transformation)
    phase_3_recs = [r for r in recommendations if r.get('timeline', '').startswith('90+')]
    roadmap.append({
        'phase': '90+ Days',
        'title': 'Long-term Transformation',
        'description': 'Comprehensive brand health optimization',
        'recommendations': len(phase_3_recs) if phase_3_recs else 2,
        'expectedRevenue': 1000000,  # Estimated long-term impact
        'keyMilestones': [
            'Full brand health optimization',
            'Market leadership position',
            'Sustainable competitive advantage'
        ],
        'successMetrics': ['Market share growth', 'Brand equity improvement']
    })
    
    return roadmap

@app.get("/strategic-intelligence")
def get_strategic_intelligence(
    tier: Optional[str] = None,
    business_impact: Optional[str] = None,
    timeline: Optional[str] = None
):
    """Business-focused strategic recommendations with ROI impact"""
    try:
        # Load master data
        data_loader = BrandHealthDataLoader()
        datasets, master_df = data_loader.load_all_data()
        
        if master_df.empty:
            return JSONResponse(status_code=404, content={"error": "No audit data available"})
        
        # Handle None recommendations
        recommendations_df = datasets.get("recommendations")
        if recommendations_df is None:
            recommendations_df = pd.DataFrame()
        
        # Apply filters
        filtered_df = master_df.copy()
        
        if tier:
            if "Tier 1" in tier:
                filtered_df = filtered_df[filtered_df['tier'] == 'tier_1']
            elif "Tier 2" in tier:
                filtered_df = filtered_df[filtered_df['tier'] == 'tier_2']
            elif "Tier 3" in tier:
                filtered_df = filtered_df[filtered_df['tier'] == 'tier_3']
        
        # Calculate business impact metrics
        avg_score = filtered_df['avg_score'].mean() if 'avg_score' in filtered_df.columns else 0
        critical_issues = len(filtered_df[filtered_df['critical_issue_flag'] == True]) if 'critical_issue_flag' in filtered_df.columns else 0
        quick_wins = len(filtered_df[filtered_df['quick_win_flag'] == True]) if 'quick_win_flag' in filtered_df.columns else 0
        success_stories = len(filtered_df[filtered_df['success_flag'] == True]) if 'success_flag' in filtered_df.columns else 0
        
        # Calculate pipeline risk (business impact)
        pipeline_risk = max(0, (10 - avg_score) * 250000)  # $250K per point below 10
        conversion_uplift = quick_wins * 0.15  # 15% uplift per quick win
        revenue_opportunity = critical_issues * 500000  # $500K per critical issue fixed
        
        # Generate strategic themes with business context
        strategic_themes = generate_strategic_themes(filtered_df)
        
        # Generate business-focused recommendations
        business_recommendations = generate_business_recommendations(filtered_df, tier, business_impact, timeline)
        
        # Calculate competitive context
        competitive_context = calculate_competitive_context(filtered_df)
        
        # Calculate tier analysis
        tier_analysis = calculate_tier_analysis(filtered_df)
        
        # Generate implementation roadmap
        implementation_roadmap = generate_implementation_roadmap(business_recommendations)
        
        return {
            "executiveSummary": {
                "totalRecommendations": len(business_recommendations),
                "highImpactOpportunities": len([r for r in business_recommendations if r.get('businessImpact') == 'High']),
                "pipelineRisk": round(pipeline_risk),
                "competitiveGaps": critical_issues,
                "quickWinValue": round(quick_wins * 100000),  # $100K per quick win
                "strategicInvestmentROI": round(revenue_opportunity * 0.3)  # 30% ROI on strategic investments
            },
            "strategicThemes": strategic_themes,
            "businessImpact": {
                "revenueOpportunity": round(revenue_opportunity),
                "conversionUplift": round(conversion_uplift * 100),  # Percentage
                "competitiveAdvantage": competitive_context.get('advantages', []),
                "brandEquityRisk": round(critical_issues * 0.15 * 100)  # 15% brand equity risk per critical issue
            },
            "recommendations": business_recommendations,
            "tierAnalysis": tier_analysis,
            "competitiveContext": competitive_context,
            "implementationRoadmap": implementation_roadmap
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Strategic intelligence failed: {str(e)}"})

@app.get("/api/social-media")
def get_social_media_analysis(
    platforms: Optional[str] = None,
    personas: Optional[str] = None,
    analysis_scope: str = "All Data",
    min_score: float = 0.0
):
    """Return comprehensive social media analysis data matching Python Streamlit functionality"""
    try:
        # Load unified audit data
        data_loader = BrandHealthDataLoader()
        datasets, master_df = data_loader.load_all_data()
        
        if master_df.empty:
            return JSONResponse(status_code=404, content={"error": "No data available"})
        
        # Filter for social media entries
        social_keywords = ['linkedin', 'twitter', 'facebook', 'instagram', 'x.com']
        social_media_mask = master_df['url'].str.lower().str.contains('|'.join(social_keywords), na=False)
        social_df = master_df[social_media_mask].copy()
        
        if social_df.empty:
            return JSONResponse(status_code=200, content={
                "data": [],
                "insights": [],
                "recommendations": [],
                "platform_metrics": [],
                "error": "No social media data found in audit dataset"
            })
        
        # Add platform identification
        social_df['platform'] = social_df['url'].apply(identify_platform_from_url)
        social_df['platform_display'] = social_df['platform'].map({
            'linkedin': 'LinkedIn',
            'instagram': 'Instagram',
            'facebook': 'Facebook',
            'twitter': 'Twitter/X',
            'x': 'Twitter/X'
        })
        
        # Clean persona names
        social_df['persona_clean'] = social_df['persona_id'].apply(clean_persona_name)
        
        # Apply filters
        if platforms:
            platform_list = [p.strip() for p in platforms.split(',')]
            social_df = social_df[social_df['platform_display'].isin(platform_list)]
        
        if personas:
            persona_list = [p.strip() for p in personas.split(',')]
            social_df = social_df[social_df['persona_clean'].isin(persona_list)]
        
        # Apply analysis scope filter
        if analysis_scope == "High Performers Only":
            social_df = social_df[social_df['avg_score'] >= 7]
        elif analysis_scope == "Problem Areas":
            social_df = social_df[social_df['avg_score'] < 5]
        elif analysis_scope == "Quick Wins":
            social_df = social_df[social_df['quick_win_flag'] == True]
        
        # Apply minimum score filter
        if min_score > 0:
            social_df = social_df[social_df['avg_score'] >= min_score]
        
        if social_df.empty:
            return JSONResponse(status_code=200, content={
                "data": [],
                "insights": [],
                "recommendations": [],
                "platform_metrics": [],
                "error": "No data matches the applied filters"
            })
        
        # Transform data for React consumption
        social_media_data = []
        for _, row in social_df.iterrows():
            social_media_data.append({
                'platform': row['platform'],
                'platform_display': row['platform_display'],
                'persona_clean': row['persona_clean'],
                'raw_score': float(row['avg_score']) if pd.notna(row['avg_score']) else 0.0,
                'engagement_numeric': float(row['engagement_numeric']) if pd.notna(row['engagement_numeric']) else 0.0,
                'sentiment_numeric': float(row['sentiment_numeric']) if pd.notna(row['sentiment_numeric']) else 0.0,
                'critical_issue_flag': bool(row['critical_issue_flag']) if pd.notna(row['critical_issue_flag']) else False,
                'success_flag': bool(row['success_flag']) if pd.notna(row['success_flag']) else False,
                'quick_win_flag': bool(row['quick_win_flag']) if pd.notna(row['quick_win_flag']) else False,
                'url': row['url'],
                'evidence': row['evidence'] if pd.notna(row['evidence']) else '',
                'effective_copy_examples': row['effective_copy_examples'] if pd.notna(row['effective_copy_examples']) else '',
                'ineffective_copy_examples': row['ineffective_copy_examples'] if pd.notna(row['ineffective_copy_examples']) else '',
                'trust_credibility_assessment': row['trust_credibility_assessment'] if pd.notna(row['trust_credibility_assessment']) else '',
                'business_impact_analysis': row['business_impact_analysis'] if pd.notna(row['business_impact_analysis']) else '',
                'tier': row['tier'] if pd.notna(row['tier']) else 'Unknown',
                'audited_ts': row['audited_ts'] if pd.notna(row['audited_ts']) else ''
            })
        
        # Calculate platform metrics
        platform_metrics = calculate_platform_metrics(social_df)
        
        # Generate insights
        insights = generate_social_media_insights(social_df)
        
        # Generate recommendations
        recommendations = generate_social_media_recommendations(social_df)
        
        # Calculate persona-platform matrix for heatmap
        persona_platform_matrix = calculate_persona_platform_matrix(social_df)
        
        return JSONResponse(content={
            "data": social_media_data,
            "insights": insights,
            "recommendations": recommendations,
            "platform_metrics": platform_metrics,
            "persona_platform_matrix": persona_platform_matrix,
            "analysis_scope": analysis_scope,
            "total_entries": len(social_df),
            "platforms_analyzed": sorted(social_df['platform_display'].unique().tolist()),
            "personas_analyzed": sorted(social_df['persona_clean'].unique().tolist())
        })
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Social media analysis failed: {str(e)}"})

def identify_platform_from_url(url):
    """Identify social media platform from URL"""
    if pd.isna(url):
        return 'unknown'
    
    url_lower = str(url).lower()
    if 'linkedin' in url_lower:
        return 'linkedin'
    elif 'instagram' in url_lower:
        return 'instagram'
    elif 'facebook' in url_lower:
        return 'facebook'
    elif 'twitter' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    return 'unknown'

def clean_persona_name(persona_id):
    """Clean persona names for display"""
    if pd.isna(persona_id):
        return 'Unknown'
    
    persona_mapping = {
        'The Benelux Cybersecurity Decision Maker': 'P4 - Cybersecurity',
        'The Benelux Strategic Business Leader (C-Suite Executive)': 'P1 - C-Suite',
        'The Benelux Transformation Programme Leader': 'P3 - Programme',
        'The Technical Influencer': 'P5 - Tech Influencers',
        'The_BENELUX_Technology_Innovation_Leader': 'P2 - Tech Leaders'
    }
    return persona_mapping.get(persona_id, persona_id)

def calculate_platform_metrics(social_df):
    """Calculate comprehensive platform metrics"""
    platform_stats = []
    
    for platform in social_df['platform_display'].unique():
        platform_data = social_df[social_df['platform_display'] == platform]
        
        if len(platform_data) == 0:
            continue
        
        # Calculate metrics
        avg_score = platform_data['avg_score'].mean()
        score_range = f"{platform_data['avg_score'].min():.1f} - {platform_data['avg_score'].max():.1f}"
        
        # Determine status based on average score
        if avg_score >= 7:
            status = "✅ Strong"
            status_color = "success"
        elif avg_score >= 5:
            status = "⚠️ Moderate"
            status_color = "warning"
        elif avg_score >= 3:
            status = "🟠 At Risk"
            status_color = "warning"
        else:
            status = "🔴 Critical"
            status_color = "error"
        
        # Count personas by performance
        high_performers = len(platform_data[platform_data['avg_score'] >= 7])
        moderate_performers = len(platform_data[(platform_data['avg_score'] >= 5) & (platform_data['avg_score'] < 7)])
        low_performers = len(platform_data[platform_data['avg_score'] < 5])
        
        # Get engagement and sentiment data
        avg_engagement = platform_data['engagement_numeric'].mean()
        avg_sentiment = platform_data['sentiment_numeric'].mean()
        
        platform_stats.append({
            'Platform': platform,
            'Platform_Code': platform_data['platform'].iloc[0],
            'Average_Score': float(avg_score),
            'Score_Range': score_range,
            'Status': status,
            'Status_Color': status_color,
            'Total_Entries': len(platform_data),
            'High_Performers': int(high_performers),
            'Moderate_Performers': int(moderate_performers),
            'Low_Performers': int(low_performers),
            'Avg_Engagement': float(avg_engagement),
            'Avg_Sentiment': float(avg_sentiment),
            'Critical_Issues': int(len(platform_data[platform_data['critical_issue_flag'] == True])),
            'Success_Cases': int(len(platform_data[platform_data['success_flag'] == True])),
            'Quick_Wins': int(len(platform_data[platform_data['quick_win_flag'] == True]))
        })
    
    return platform_stats

def generate_social_media_insights(social_df):
    """Generate key insights from social media data"""
    insights = []
    
    # Overall performance insight
    overall_avg = social_df['avg_score'].mean()
    insights.append({
        'Category': 'Overall Performance',
        'Insight': f'Average social media score across all platforms and personas is {overall_avg:.1f}/10',
        'Type': 'metric'
    })
    
    # Best performing platform
    platform_avgs = social_df.groupby('platform_display')['avg_score'].mean().sort_values(ascending=False)
    if len(platform_avgs) > 0:
        best_platform = platform_avgs.index[0]
        best_score = float(platform_avgs.iloc[0])
        insights.append({
            'Category': 'Top Performer',
            'Insight': f'{best_platform} is the strongest platform with {best_score:.1f}/10 average score',
            'Type': 'success'
        })
        
        # Worst performing platform
        worst_platform = platform_avgs.index[-1]
        worst_score = float(platform_avgs.iloc[-1])
        insights.append({
            'Category': 'Needs Attention',
            'Insight': f'{worst_platform} requires review with {worst_score:.1f}/10 average score',
            'Type': 'warning'
        })
    
    # Critical issues count
    critical_count = len(social_df[social_df['critical_issue_flag'] == True])
    if critical_count > 0:
        insights.append({
            'Category': 'Critical Issues',
            'Insight': f'{critical_count} entries flagged as critical issues requiring immediate action',
            'Type': 'warning'
        })
    
    # Quick wins
    quick_wins = len(social_df[social_df['quick_win_flag'] == True])
    if quick_wins > 0:
        insights.append({
            'Category': 'Quick Wins',
            'Insight': f'{quick_wins} opportunities identified for quick improvement',
            'Type': 'opportunity'
        })
    
    # Engagement vs Score correlation
    if len(social_df) > 1:
        correlation = social_df['engagement_numeric'].corr(social_df['avg_score'])
        if pd.notna(correlation):
            insights.append({
                'Category': 'Engagement Correlation',
                'Insight': f'Engagement and performance correlation: {correlation:.2f} ({"Strong" if abs(correlation) > 0.7 else "Moderate" if abs(correlation) > 0.4 else "Weak"})',
                'Type': 'metric'
            })
    
    return insights

def generate_social_media_recommendations(social_df):
    """Generate actionable recommendations from social media data"""
    recommendations = []
    
    # Platform-specific recommendations
    for platform in social_df['platform_display'].unique():
        platform_data = social_df[social_df['platform_display'] == platform]
        avg_score = platform_data['avg_score'].mean()
        
        if avg_score < 3:
            priority = 'High'
            recommendations.append({
                'Platform': platform,
                'Priority': priority,
                'Category': 'Critical Revival',
                'Recommendation': f'Immediate reactivation required for {platform}. Current score of {avg_score:.1f}/10 indicates platform abandonment.',
                'Impact': 'High',
                'Timeline': '0-30 days'
            })
        elif avg_score < 5:
            priority = 'High'
            recommendations.append({
                'Platform': platform,
                'Priority': priority,
                'Category': 'Strategic Improvement',
                'Recommendation': f'Comprehensive content strategy needed for {platform}. Score of {avg_score:.1f}/10 shows underperformance.',
                'Impact': 'Medium',
                'Timeline': '1-3 months'
            })
        elif avg_score < 7:
            priority = 'Medium'
            recommendations.append({
                'Platform': platform,
                'Priority': priority,
                'Category': 'Optimization',
                'Recommendation': f'Enhance content quality and persona targeting for {platform}. Current score: {avg_score:.1f}/10.',
                'Impact': 'Medium',
                'Timeline': '1-3 months'
            })
    
    # Persona-specific recommendations
    persona_performance = social_df.groupby('persona_clean')['avg_score'].mean().sort_values()
    if len(persona_performance) > 0:
        worst_persona = persona_performance.index[0]
        worst_persona_score = float(persona_performance.iloc[0])
        
        recommendations.append({
            'Platform': 'Cross-Platform',
            'Priority': 'High',
            'Category': 'Persona Strategy',
            'Recommendation': f'Develop targeted content strategy for {worst_persona} (avg score: {worst_persona_score:.1f}/10)',
            'Impact': 'High',
            'Timeline': '1-2 months'
        })
    
    # Content gap analysis
    quick_wins = social_df[social_df['quick_win_flag'] == True]
    if len(quick_wins) > 0:
        recommendations.append({
            'Platform': 'Cross-Platform',
            'Priority': 'Medium',
            'Category': 'Quick Wins',
            'Recommendation': f'Focus on {len(quick_wins)} identified quick win opportunities for immediate improvement',
            'Impact': 'Medium',
            'Timeline': '0-30 days'
        })
    
    return recommendations

def calculate_persona_platform_matrix(social_df):
    """Calculate persona-platform performance matrix for heatmap"""
    try:
        matrix = social_df.pivot_table(
            values='avg_score',
            index='persona_clean',
            columns='platform_display',
            aggfunc='mean'
        ).fillna(0)
        
        # Convert to list of dictionaries for easier React consumption
        matrix_data = []
        for persona in matrix.index:
            for platform in matrix.columns:
                score = matrix.loc[persona, platform]
                if score > 0:  # Only include non-zero scores
                    matrix_data.append({
                        'persona': persona,
                        'platform': platform,
                        'score': float(score)
                    })
        
        return matrix_data
    except Exception as e:
        return []

# New Reports Export API endpoints
@app.post("/reports/custom")
async def generate_custom_report_new(report_config: dict):
    """Generate a custom report based on configuration"""
    try:
        # Load master data
        master_df = load_master_data()
        if master_df.empty:
            raise HTTPException(status_code=404, detail="No data available")
        
        # Mock report generation for now
        return {
            "status": "success",
            "message": "Custom report generated successfully",
            "report_id": f"custom_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "format": report_config.get("format", "pdf"),
            "report_type": report_config.get("reportType", "comprehensive"),
            "personas": report_config.get("personas", []),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating custom report: {str(e)}")

@app.post("/reports/html")
async def generate_html_reports_new(html_options: dict):
    """Generate HTML reports based on options"""
    try:
        # Mock HTML report generation
        reports_count = 1
        if html_options.get("generationMode") == "All Personas":
            reports_count = 5
        elif html_options.get("generationMode") == "Selected Personas":
            reports_count = len(html_options.get("personas", []))
        
        return {
            "status": "success",
            "message": "HTML reports generated successfully",
            "reports": [f"report_{i+1}" for i in range(reports_count)],
            "generation_mode": html_options.get("generationMode"),
            "timestamp": datetime.now().isoformat(),
            "personas": html_options.get("personas", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating HTML reports: {str(e)}")

@app.post("/export/{format}")
async def export_data_new(format: str, export_request: dict):
    """Export data in specified format"""
    try:
        # Load master data for export
        master_df = load_master_data()
        if master_df.empty:
            raise HTTPException(status_code=404, detail="No data available for export")
        
        # Apply basic filtering if provided
        filters = export_request.get("filters", {})
        filtered_data = master_df
        
        if filters.get("personaFilter") and filters["personaFilter"] != "All":
            filtered_data = filtered_data[filtered_data["persona_id"] == filters["personaFilter"]]
        
        if filters.get("tierFilter") and filters["tierFilter"] != "All":
            filtered_data = filtered_data[filtered_data["tier"] == filters["tierFilter"]]
        
        # Mock export response
        if format == "csv":
            csv_data = "url,persona,tier,overall_score\nwww.example.com,Test Persona,Tier 1,85.5\n"
            return StreamingResponse(
                io.StringIO(csv_data),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=export_{datetime.now().strftime('%Y%m%d')}.csv"}
            )
        elif format == "json":
            json_data = '{"data": [{"url": "www.example.com", "persona": "Test Persona", "tier": "Tier 1", "overall_score": 85.5}]}'
            return StreamingResponse(
                io.StringIO(json_data),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=export_{datetime.now().strftime('%Y%m%d')}.json"}
            )
        else:
            return {"status": "success", "message": f"Export in {format} format completed", "records": len(filtered_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")



