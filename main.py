import os
import typer
import subprocess
import logging
import starlette.status as status
import webbrowser
import uvicorn
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from yaspin import yaspin
from yaspin.spinners import Spinners
from sys import exit


LANDING_URL = "http://localhost:8000"

app = typer.Typer()
fast_app = FastAPI()

handler = RotatingFileHandler("./unlovable.log", maxBytes=1_000_000, backupCount=3)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
)


# TODO: handle KeyboardInterrupt
@app.command()
def main():
    if "dist" not in os.listdir("./frontend"):
        LANDING_BUILD_MSG = "Landing page build not found. Building..."

        with yaspin(Spinners.earth, text=LANDING_BUILD_MSG) as spinner:
            logging.info(LANDING_BUILD_MSG)
            spinner.write("> cd frontend; npm run build")
            build_output = subprocess.run(
                ["npm", "run", "build"],
                capture_output=True,
                text=True,
                cwd="./frontend",
            )

            if build_output.returncode != 1:
                logging.error(f"Landing build failed: {build_output.stderr}")
                spinner.write("npm run build exited with non-zero code")
                spinner.fail("❌️")
                exit(1)

            spinner.ok("✅️")

    fast_app.mount("/app", StaticFiles(directory="./frontend/dist"), name="app")
    webbrowser.open(LANDING_URL)


@fast_app.get("/")
def get_root():
    main()

    return RedirectResponse(url="/app", status_code=status.HTTP_200_OK)


if __name__ == "__main__":
    app()
    uvicorn.run("main:fast_app", host="127.0.0.1", port=8000, reload=True)
