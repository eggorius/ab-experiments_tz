from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import experiments_router, devices_router, stats_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="A/B Experiment API", lifespan=lifespan)


app.include_router(experiments_router)
app.include_router(devices_router)
app.include_router(stats_router)
