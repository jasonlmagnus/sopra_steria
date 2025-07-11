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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from audit_tool.dashboard.components.data_loader import BrandHealthDataLoader
from audit_tool.dashboard.components.metrics_calculator import (
    BrandHealthMetricsCalculator,
)
from audit_tool.html_report_generator import HTMLReportGenerator

app = FastAPI(title="Sopra Steria Audit FastAPI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/api/audit-data")
def get_audit_data():
    """Return the unified audit data for React components"""
    try:
        data_loader = BrandHealthDataLoader()
        datasets, master_df = data_loader.load_all_data()
        if master_df.empty:
            raise HTTPException(status_code=404, detail="No audit data available")
        
        # Handle NaN values that cause JSON serialization errors
        master_df = master_df.fillna('')  # Replace NaN with empty strings
        
        return master_df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading audit data: {str(e)}")

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
            report_data = metrics_calc.generate_executive_summary_report()
        elif request.reportType == "Persona Performance Report":
            report_data = metrics_calc.generate_persona_performance_report()
        elif request.reportType == "Content Tier Analysis Report":
            report_data = metrics_calc.generate_content_tier_report()
        elif request.reportType == "Success Stories Report":
            report_data = metrics_calc.generate_success_stories_report()
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
                        executive_summary = metrics_calc.generate_executive_summary_report()
                        success_stories = metrics_calc.generate_success_stories_report()
                        
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
        voice_stats = BrandHealthMetricsCalculator.calculate_voice_stats(persona_data)

        # Process effective copy examples
        effective_analysis = BrandHealthMetricsCalculator.process_effective_copy_examples(persona_data)

        # Process ineffective copy examples
        ineffective_analysis = BrandHealthMetricsCalculator.process_ineffective_copy_examples(persona_data)

        # Process business impact analysis
        business_impact = BrandHealthMetricsCalculator.process_business_impact_analysis(persona_data)
        
        # Extract voice themes and patterns
        voice_patterns = extract_voice_patterns(persona_data)
        
        # Generate copy-ready quotes
        copy_ready_quotes = BrandHealthMetricsCalculator.generate_copy_ready_quotes(persona_data)
        
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


def create_friendly_page_title(page_id, url):
    """Create user-friendly page title"""
    if not page_id:
        return "Unknown Page"
    
    # Basic cleaning
    title = page_id.replace('_', ' ').replace('-', ' ')
    title = ' '.join(word.capitalize() for word in title.split())
    
    # Add URL context if available
    if url:
        if 'newsroom' in url.lower():
            title = f"Newsroom > {title}"
        elif 'blog' in url.lower():
            title = f"Blog > {title}"
        elif 'about' in url.lower():
            title = f"About > {title}"
        elif 'services' in url.lower():
            title = f"Services > {title}"
        elif 'industries' in url.lower():
            title = f"Industries > {title}"
        elif 'company' in url.lower():
            title = f"Company > {title}"
    
    return title

@app.get("/strategic-intelligence")
def get_strategic_intelligence(
    tier: Optional[str] = None,
    business_impact: Optional[str] = None,
    timeline: Optional[str] = None
):
    """Business-focused strategic recommendations using metrics calculator"""
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
        
        # Use the metrics calculator for all strategic intelligence
        metrics_calc = BrandHealthMetricsCalculator(filtered_df, recommendations_df)
        
        # Helper function to handle NaN values
        def clean_nan_values(data):
            """Recursively clean NaN values from nested dictionaries and lists"""
            if isinstance(data, dict):
                return {k: clean_nan_values(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [clean_nan_values(item) for item in data]
            elif isinstance(data, float) and (pd.isna(data) or data == float('inf') or data == float('-inf')):
                return 0.0
            else:
                return data

        # Get strategic intelligence from metrics calculator
        strategic_intelligence = metrics_calc.calculate_strategic_intelligence(tier, business_impact, timeline)
        
        # Clean all NaN values from the response
        return clean_nan_values(strategic_intelligence)
        
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
        platform_metrics = BrandHealthMetricsCalculator.calculate_platform_metrics(social_df)

        # Generate insights
        insights = BrandHealthMetricsCalculator.generate_social_media_insights(social_df)

        # Generate recommendations
        recommendations = BrandHealthMetricsCalculator.generate_social_media_recommendations(social_df)

        # Calculate persona-platform matrix for heatmap
        persona_platform_matrix = BrandHealthMetricsCalculator.calculate_persona_platform_matrix(social_df)
        
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

# Start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



