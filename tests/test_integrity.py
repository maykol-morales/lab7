from fastapi.testclient import TestClient

from app.main import app
from app.mongo import db

client = TestClient(app)


def test_create_paper_integrity():
    payload = {
        "name": "AI Research Paper",
        "authors": ["John Doe"],
        "abstract": "A test paper",
        "citations": [{"title": "Prev Work", "year": 2022, "authors": ["Jane"]}],
        "paper_url": "http://example.com/paper.pdf"
    }

    response = client.post("/papers/", json=payload)
    assert response.status_code == 201
    data = response.json()

    # Verifica SQL id creado
    assert "sql_id" in data
    assert data["name"] == "AI Research Paper"

    # Verifica Mongo doc creado
    mongo_doc = db.papers.find_one({"sql_id": data["sql_id"]})
    assert mongo_doc is not None
    assert mongo_doc["name"] == "AI Research Paper"
