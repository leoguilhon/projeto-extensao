from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import API_TITLE, CORS_ORIGINS
from app.services.seed import seed_data


def create_app() -> FastAPI:
    application = FastAPI(title=API_TITLE)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)
    return application


seed_data()
app = create_app()
