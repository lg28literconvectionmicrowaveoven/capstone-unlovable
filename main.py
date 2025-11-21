import logging
import starlette.status as status
import uvicorn
import signal
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from lib.landing import build_landing
from lib.project import open_project
from contextlib import asynccontextmanager
from webbrowser import open as wb_open


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting unlovable... Press ^C to exit")
    wb_open("http://localhost:8000")

    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

build_landing()
app.mount("/app", StaticFiles(directory="frontend/dist", html=True), name="app")

logging.basicConfig(
    handlers=[
        RotatingFileHandler("./unlovable.log", maxBytes=100_000_000, backupCount=3),
        logging.StreamHandler(),
    ],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
)


@app.get("/")
def get_root():
    return RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)


@app.post("/api/open_project", status_code=200)
def post_open_proj(path: str):
    print(path)


def interrupt_handler(sig, frame):
    logging.info("Exiting unlovable...")
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupt_handler)

    uvicorn.run(
        "main:app", host="127.0.0.1", port=8000, log_level="critical", access_log=False
    )
