from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from audit_tool.dashboard.components.data_loader import BrandHealthDataLoader
from audit_tool.dashboard.components.metrics_calculator import (
    BrandHealthMetricsCalculator,
)

app = FastAPI(title="Sopra Steria Audit FastAPI")

@app.get("/hello")
def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/datasets")
def list_datasets():
    data_loader = BrandHealthDataLoader()
    datasets, _ = data_loader.load_all_data()
    return {"datasets": list(datasets.keys())}

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
    metrics = BrandHealthMetricsCalculator(master_df, datasets.get("recommendations"))
    opportunities = metrics.get_top_opportunities(limit=limit)
    return {"opportunities": opportunities}


@app.get("/executive-summary")
def get_executive_summary():
    """Return executive summary metrics"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    metrics = BrandHealthMetricsCalculator(
        master_df, datasets.get("recommendations")
    )
    summary = metrics.generate_executive_summary()
    return summary


@app.get("/tier-metrics", summary="Tier performance metrics")
def get_tier_metrics():
    """Return aggregated performance metrics by content tier"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    metrics = BrandHealthMetricsCalculator(master_df, datasets.get("recommendations"))
    tier_df = metrics.calculate_tier_performance()
    json_str = tier_df.to_json(orient="records")
    return Response(content=json_str, media_type="application/json")


@app.get("/persona-comparison", summary="Persona comparison metrics")
def get_persona_comparison():
    """Return metrics comparing performance across personas"""
    data_loader = BrandHealthDataLoader()
    datasets, master_df = data_loader.load_all_data()
    metrics = BrandHealthMetricsCalculator(master_df, datasets.get("recommendations"))
    persona_df = metrics.calculate_persona_comparison()
    json_str = persona_df.to_json(orient="records")
    return Response(content=json_str, media_type="application/json")


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

