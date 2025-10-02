from fastapi import APIRouter

from app.schemas import Paper

router = APIRouter(prefix="/papers")


@router.post("/")
def create_info(paper: Paper):
    return {"message": "Info created"}
