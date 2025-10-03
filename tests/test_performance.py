import pytest
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_search_paper_performance():
    paper_name = "PerformanceTest"
    payload = {
        "name": paper_name,
        "authors": ["Tester"],
        "abstract": "Benchmark paper",
        "citations": [],
        "paper_url": "http://example.com"
    }
    client.post("/papers/", json=payload)

    start = time.time()
    res = client.get(f"/papers/search/{paper_name}")
    elapsed = time.time() - start

    assert res.status_code == 200
    data = res.json()
    assert data["sql"]["name"] == paper_name
    assert data["mongo"]["name"] == paper_name

    # Performance threshold
    assert elapsed < 0.3, f"Search too slow: {elapsed}s"
