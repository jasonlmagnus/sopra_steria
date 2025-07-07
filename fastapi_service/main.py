from fastapi import FastAPI
from fastapi.responses import JSONResponse
from audit_tool.dashboard.components.data_loader import BrandHealthDataLoader

app = FastAPI(title="Sopra Steria Audit FastAPI")

data_loader = BrandHealthDataLoader()

@app.get("/hello")
def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/datasets")
def list_datasets():
    datasets, _ = data_loader.load_all_data()
    return {"datasets": list(datasets.keys())}

@app.get("/datasets/{name}")
def get_dataset(name: str):
    datasets, _ = data_loader.load_all_data()
    if name not in datasets:
        return JSONResponse(status_code=404, content={"error": "Dataset not found"})
    df = datasets[name]
    return df.to_dict(orient="records")

