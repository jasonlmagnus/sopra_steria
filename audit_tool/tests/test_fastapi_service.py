import pytest
from fastapi.testclient import TestClient
from fastapi_service.main import app

client = TestClient(app)

def test_hello_endpoint():
    resp = client.get('/hello')
    assert resp.status_code == 200
    assert resp.json() == {'message': 'Hello from FastAPI'}


def test_datasets_endpoint():
    resp = client.get('/datasets')
    assert resp.status_code == 200
    assert 'datasets' in resp.json()


def test_executive_summary_endpoint():
    resp = client.get('/executive-summary')
    assert resp.status_code == 200
    assert 'brand_health' in resp.json()
