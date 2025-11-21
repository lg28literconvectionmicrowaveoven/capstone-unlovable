import logging
import os
import shutil
import subprocess
from yaspin import yaspin
from yaspin.spinners import Spinners


# NOTE: make sure it is user-expanded
def open_project(path: str):
    logging.info(f"Opening project {path}")

    if "prompts" not in os.listdir(path):
        generate_project(path)


# TODO: handle exceptions
# TODO: ignore hidden folders
def generate_project(path: str):
    subroutes: list[str] = os.listdir(path)
    os.mkdir(f"{path}/prompts")
    shutil.move(f"{path}/index.txt", f"{path}/prompts")

    for subroute in subroutes:
        shutil.move(f"{path}/{subroute}", f"{path}/prompts/{subroute}")

    with yaspin(
        Spinners.earth, text="Creating Next.js project with default config..."
    ) as spinner:
        n_create_output = subprocess.run(
            ["npm", "create-next-app@latest", path.split("/")[-1], "yes"],
            capture_output=True,
            text=True,
            cwd="./frontend",
        )

        if n_create_output.returncode != 0:
            logging.error(f"Project creation failed: {n_create_output.stderr}")
            spinner.write(
                f"npx create-next-app@latest {path.split('/')[-1]} --yes exited with code {n_create_output.returncode}"
            )
            spinner.fail("❌️")
