from logfire import configure, instrument_fastapi
from fastapi import FastAPI

from mongomock import MongoClient
from app.routes import users, papers

app = FastAPI()

configure()
instrument_fastapi(app)

client = MongoClient()
db = client["paperly"]


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(users.router)
app.include_router(papers.router)
