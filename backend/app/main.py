from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import API_TITLE, CORS_ORIGINS, ENABLE_SEED_DATA
from app.db.session import SessionLocal, init_db
from app.services.seed import seed_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    if ENABLE_SEED_DATA:
        db = SessionLocal()
        try:
            seed_data(db)
        finally:
            db.close()
    yield


def create_app() -> FastAPI:
    application = FastAPI(title=API_TITLE, lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)
    return application


app = create_app()
