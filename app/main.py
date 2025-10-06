import logfire
from fastapi import FastAPI

from app import mongo
from app.routes import users, papers

app = FastAPI()

logfire.configure()
logfire.instrument_fastapi(app)


@app.get("/")
async def root():
    logfire.info("Stable")
    return {"message": "Hello World"}


app.include_router(users.router)
app.include_router(papers.router)
