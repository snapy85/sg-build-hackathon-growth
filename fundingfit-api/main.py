import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import database
from routers import business, goals, history, match, plan, schemes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    logger.info("FundingFit API running — visit /docs for the interactive spec")
    yield


app = FastAPI(title="FundingFit API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(business.router, prefix="/api")
app.include_router(schemes.router, prefix="/api")
app.include_router(match.router, prefix="/api")
app.include_router(plan.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(goals.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
