from fastapi import APIRouter
from app.api.v1.endpoints import user, wallet_info

api_router = APIRouter()

api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(wallet_info.router, prefix="/chk_wallet_info", tags=["wallet_info"]) 