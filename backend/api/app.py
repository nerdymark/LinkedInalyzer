from collections.abc import Generator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database import get_session_factory, init_db


def create_app() -> FastAPI:
    init_db()

    app = FastAPI(title="LinkedInalyzer", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from backend.api.routes import authors, posts, stats

    app.include_router(authors.router, prefix="/api")
    app.include_router(posts.router, prefix="/api")
    app.include_router(stats.router, prefix="/api")

    return app
