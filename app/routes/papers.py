from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.mongo import db
from app.sqlite import get_db
from app.schemas import Paper, PaperOut
from app.ormmodel import PaperORM
router = APIRouter(prefix="/papers")

@router.post("/", response_model=PaperOut, status_code=200)
def create_paper(payload: Paper, db2: Session = Depends(get_db)):
    paper = PaperORM(name=payload.name)
    db2.add(paper)
    db2.commit()
    db2.refresh(paper)
    return paper

@router.post("/info")
def create_info(paper: Paper):
    document = paper.model_dump()
    result = db.papers.insert_one(document)

    return {"message": "Paper created successfully", "id": str(result.inserted_id)}
