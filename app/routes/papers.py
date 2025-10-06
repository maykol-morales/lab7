import logfire
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.mongo import db
from app.ormmodel import PaperORM
from app.schemas import Paper
from app.sqlite import get_db

router = APIRouter(prefix="/papers")


@router.post("/", status_code=201)
def create_paper(paper: Paper, db2: Session = Depends(get_db)):
    logfire.info("Solicitud recibida para crear paper", name=paper.name)

    # Crear objeto en SQL
    sql_obj = PaperORM(name=paper.name)
    db2.add(sql_obj)
    try:
        db2.commit()
        db2.refresh(sql_obj)
        logfire.info("Paper guardado en SQL correctamente", sql_id=sql_obj.id, name=sql_obj.name)
    except Exception as e:
        db2.rollback()
        logfire.exception("Error al guardar paper en SQL", error=str(e), name=paper.name)
        raise HTTPException(status_code=409, detail=f"Error al guardar en SQL: {e}")

    # Insertar en Mongo
    doc = paper.model_dump()
    doc["sql_id"] = sql_obj.id
    try:
        result = db.papers.insert_one(doc)
        logfire.info(
            "Paper guardado en Mongo correctamente",
            mongo_id=str(result.inserted_id),
            sql_id=sql_obj.id,
            name=sql_obj.name
        )
    except Exception as e:
        db2.delete(sql_obj)
        db2.commit()
        logfire.exception(
            "Error al guardar en Mongo, revertido en SQL",
            error=str(e),
            sql_id=sql_obj.id,
            name=sql_obj.name
        )
        raise HTTPException(status_code=500, detail=f"Error al guardar en Mongo, SQL revertido: {e}")

    logfire.info("Paper creado exitosamente en ambas bases", sql_id=sql_obj.id, mongo_id=str(result.inserted_id))
    return {
        "message": "Paper creado en SQL y Mongo",
        "sql_id": sql_obj.id,
        "mongo_id": str(result.inserted_id),
        "name": sql_obj.name
    }


@router.get("/search/{paper_name}")
def search_paper(paper_name: str, db2: Session = Depends(get_db)):
    logfire.info("Búsqueda de paper iniciada", name=paper_name)

    # Buscar en SQL
    sql_obj = db2.query(PaperORM).filter(PaperORM.name == paper_name).first()
    if not sql_obj:
        logfire.warning("Paper no encontrado en SQL", name=paper_name)
        raise HTTPException(status_code=404, detail="Paper no encontrado en SQL")

    logfire.debug("Paper encontrado en SQL", sql_id=sql_obj.id, name=sql_obj.name)

    # Buscar en Mongo
    mongo_doc = db.papers.find_one({"sql_id": sql_obj.id}) or db.papers.find_one({"name": paper_name})
    if mongo_doc:
        logfire.debug("Documento encontrado en Mongo", sql_id=sql_obj.id)
        mongo_doc = dict(mongo_doc)
        if "_id" in mongo_doc:
            mongo_doc["_id"] = str(mongo_doc["_id"])
    else:
        logfire.warning("No se encontró documento en Mongo correspondiente", sql_id=sql_obj.id)

    logfire.info("Búsqueda completada exitosamente", sql_id=sql_obj.id)
    return {
        "sql": {"id": sql_obj.id, "name": sql_obj.name},
        "mongo": mongo_doc
    }
