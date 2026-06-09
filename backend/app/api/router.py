from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.books import router as books_router
from app.api.routes.clubs import router as clubs_router
from app.api.routes.meetings import router as meetings_router
from app.api.routes.root import router as root_router
from app.api.routes.users import router as users_router


api_router = APIRouter()
api_router.include_router(root_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(clubs_router)
api_router.include_router(books_router)
api_router.include_router(meetings_router)
