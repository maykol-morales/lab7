from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.mongo import db
from app.sqlite import get_db
from app.schemas import Paper, PaperOut
from app.ormmodel import PaperORM
router = APIRouter(prefix="/papers")

@router.post("/", status_code=201)
def create_paper(paper: Paper, db2: Session = Depends(get_db)):
    sql_obj = PaperORM(name=paper.name)
    db2.add(sql_obj)
    try:
        db2.commit()
        db2.refresh(sql_obj)
    except Exception as e:
        db2.rollback()
        raise HTTPException(status_code=409, detail=f"Error al guardar en SQL: {e}")

    doc = paper.model_dump()
    doc["sql_id"] = sql_obj.id
    try:
        result = db.papers.insert_one(doc)
    except Exception as e:
        db2.delete(sql_obj)
        db2.commit()
        raise HTTPException(status_code=500, detail=f"Error al guardar en Mongo, SQL revertido: {e}")

    return {
        "message": "Paper creado en SQL y Mongo",
        "sql_id": sql_obj.id,
        "mongo_id": str(result.inserted_id),
        "name": sql_obj.name
    }


@router.get("/search/{paper_name}")
def search_paper(paper_name: str, db2: Session = Depends(get_db)):
    from fastapi import HTTPException

    sql_obj = db2.query(PaperORM).filter(PaperORM.name == paper_name).first()
    if not sql_obj:
        raise HTTPException(status_code=404, detail="Paper no encontrado en SQL")

    mongo_doc = db.papers.find_one({"sql_id": sql_obj.id}) or db.papers.find_one({"name": paper_name})

    if mongo_doc:
        mongo_doc = dict(mongo_doc)
        if "_id" in mongo_doc:
            mongo_doc["_id"] = str(mongo_doc["_id"])

    return {
        "sql": {"id": sql_obj.id, "name": sql_obj.name},
        "mongo": mongo_doc
    }
