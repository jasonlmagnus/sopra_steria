from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from audit_tool.dashboard.components.data_loader import BrandHealthDataLoader

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

