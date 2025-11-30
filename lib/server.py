import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lib.project import generate_project, project_dev_server
from contextlib import asynccontextmanager
from globals import app_state
from concurrent.futures import ThreadPoolExecutor, wait

thread_executor: ThreadPoolExecutor


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting unlovable...")

    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/generate_project", status_code=200)
def post_generate_project(path: str):
    global thread_executor

    with app_state._lock:
        app_state.current_project = path

    wait([thread_executor.submit(generate_project)])
    project_dev_server()


def serve(executor: ThreadPoolExecutor):
    global thread_executor
    thread_executor = executor
    uvicorn.run(
        "lib.server:app",
        host="127.0.0.1",
        port=8000,
        log_level="critical",
        access_log=False,
    )
