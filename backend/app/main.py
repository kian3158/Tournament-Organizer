from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="Tournament Organizer Backend")

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Backend is alive"}
