import logging
import uvicorn
import signal
import globals
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lib.landing import build_app, launch_app
from lib.project import generate_project
from contextlib import asynccontextmanager

logging.basicConfig(
    handlers=[
        RotatingFileHandler("./unlovable.log", maxBytes=100_000_000, backupCount=3),
        logging.StreamHandler(),
    ],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting unlovable...")

    launch_app()

    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

build_app()


@app.post("/api/generate_project", status_code=200)
def post_generate_project(path: str):
    globals.current_project = path
    generate_project()


def interrupt_handler(sig, handler):
    logging.info("Exiting unlovable...")
    exit(0)


def serve():
    signal.signal(signal.SIGINT, interrupt_handler)

    uvicorn.run(
        "lib.server:app",
        host="127.0.0.1",
        port=8000,
        log_level="critical",
        access_log=False,
    )
