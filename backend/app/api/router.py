from fastapi import APIRouter

from .routes import auth, matches, participants, tournaments

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(tournaments.router)
api_router.include_router(participants.router)
api_router.include_router(matches.router)
