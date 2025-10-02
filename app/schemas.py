from pydantic import BaseModel


class Citation(BaseModel):
    title: str
    year: int
    authors: list[str]


class Paper(BaseModel):
    name: str
    authors: list[str]
    abstract: str
    citations: list[Citation]
    paper_url: str
