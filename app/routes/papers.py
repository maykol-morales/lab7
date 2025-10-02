from fastapi import APIRouter

from app.mongo import db
from app.schemas import Paper

router = APIRouter(prefix="/papers")


@router.post("/")
def create_info(paper: Paper):
    document = paper.model_dump()
    result = db.papers.insert_one(document)

    return {"message": "Paper created successfully", "id": str(result.inserted_id)}
