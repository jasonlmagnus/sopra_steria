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


def test_tier_metrics_endpoint():
    resp = client.get('/tier-metrics')
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_persona_comparison_endpoint():
    resp = client.get('/persona-comparison')
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_full_recommendations_endpoint():
    resp = client.get('/full-recommendations')
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
