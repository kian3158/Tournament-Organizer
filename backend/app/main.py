from fastapi import FastAPI

app = FastAPI(title="Tournament Organizer Backend")

@app.get("/")
def read_root():
    return {"message": "Backend is alive"}