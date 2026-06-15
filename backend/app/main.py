from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title="Tournament Organizer API",
    version="0.1.0",
    description=(
        "Backend for a tournament organizer supporting single- and "
        "double-elimination, round-robin, and swiss formats, with JWT auth "
        "and live bracket updates over WebSockets."
    ),
    openapi_tags=[
        {"name": "auth", "description": "Register, log in, current user."},
        {"name": "tournaments", "description": "Create, list, generate brackets."},
        {"name": "participants", "description": "Manage tournament entrants."},
        {"name": "matches", "description": "Report match results."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Backend is alive"}
