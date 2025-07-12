from fastapi import APIRouter
from app.api.v1.endpoints import auth, losses

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(losses.router, prefix="/losses", tags=["losses"]) 