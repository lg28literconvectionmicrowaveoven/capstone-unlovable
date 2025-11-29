import logging
import os
import shutil
import subprocess
from yaspin import yaspin
from yaspin.spinners import Spinners
from globals import current_project
from graphs.planner import planner, Plan


def generate_project():
    logging.info(f"Opening project {current_project}")

    if "prompts" not in os.listdir(current_project):
        create_project()

    plan: Plan = planner.invoke(current_project)

    for common_task in plan.common_tasks:
        task.invoke(current_project)


# TODO: handle exceptions
# TODO: ignore hidden folders
def create_project():
    subroutes: list[str] = os.listdir(current_project)
    os.mkdir(f"{current_project}/prompts")
    shutil.move(f"{current_project}/index.txt", f"{current_project}/prompts")

    for subroute in subroutes:
        shutil.move(
            f"{current_project}/{subroute}",
            f"{current_project}/prompts/{subroute}",
        )

    with yaspin(
        Spinners.earth, text="Creating Next.js project with default config..."
    ) as spinner:
        n_create_output = subprocess.run(
            [
                "npm",
                "create-next-app@latest",
                current_project.split("/")[-1],
                "yes",
            ],
            capture_output=True,
            text=True,
            cwd="./frontend",
        )

        if n_create_output.returncode != 0:
            logging.error(f"Project creation failed: {n_create_output.stderr}")
            spinner.write(
                f"npx create-next-app@latest {current_project.split('/')[-1]} --yes exited with code {n_create_output.returncode}"
            )
            spinner.fail("❌️")
