import uvicorn
import logging
import os
import time
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from lib.project import generate_project, project_dev_server, revert_project
from contextlib import asynccontextmanager
from globals import app_state
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

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


@app.post("/api/generate_project")
def post_generate_project(path: str):
    global thread_executor

    with app_state._lock:
        app_state.current_project = path

    try:
        generate_project()
    except RuntimeError as e:
        thread_executor.submit(revert_project)
        return Response(
            content=f"Project generation failed with: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    thread_executor.submit(project_dev_server)
    return Response(status_code=status.HTTP_200_OK)


class Model(BaseModel):
    provider: str
    model_string: str


@app.post("/api/switch_model")
def post_switch_model(model: Model):
    new_model = None

    try:
        if model.provider == "Ollama":
            new_model = ChatOllama(model=model.model_string, temperature=0)
        elif model.provider == "Groq":
            new_model = ChatGroq(model=model.model_string, temperature=0)
        elif model.provider == "OpenAI":
            new_model = ChatOpenAI(model=model.model_string, temperature=0)
    except Exception as e:
        revert_project()
        return Response(
            content=f"Switching models failed with: {str(e)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    with app_state._lock:
        app_state.model = new_model

    return Response(status_code=status.HTTP_200_OK)


@app.post("/api/quit")
def post_quit():
    global thread_executor

    print()
    logging.info("Exiting unlovable...")

    def quit():
        time.sleep(0.1)
        os._exit(0)

    thread_executor.submit(quit)
    return Response(status_code=status.HTTP_200_OK)


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
