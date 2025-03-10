from fastapi import APIRouter
from app.api.v1.endpoints import user, game, game_log


api_router = APIRouter(prefix="/v1")
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(game.router, prefix="/games", tags=["games"])
api_router.include_router(game_log.router, prefix="/game_logs", tags=["game_logs"])
