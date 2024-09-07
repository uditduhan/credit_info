import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import settings
from app.api.routes import company, credit
from app.database import init_db, sessionmanager
from app.dummy_data import create_dummy_data

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


@asynccontextmanager
async def lifespan(app_: FastAPI):
    """
    Manages application lifecycle events for startup and shutdown.
    """
    await init_db()
    await create_dummy_data()
    setup_routes(app_)
    yield
    if sessionmanager.get_engine() is not None:
        await sessionmanager.close()


def setup_routes(app_: FastAPI) -> None:
    """
    Registers routers with the FastAPI application.
    """
    app_.include_router(company.router, prefix=settings.BASE_ROUTE, tags=["Company"])
    app_.include_router(credit.router, prefix=settings.BASE_ROUTE, tags=["Credit"])


app = FastAPI(lifespan=lifespan, docs_url="/api/docs")


@app.get("/")
def _health_check():
    return {"message": "Welcome to the Credit Information API"}
