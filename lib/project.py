import logging
import os
import shutil
import subprocess
from yaspin import yaspin
from globals import current_project
from graphs.planner import planner, Plan
from graphs.task import task


def generate_project():
    logging.info(f"Opening project {current_project}")

    if "prompts" not in os.listdir(current_project):
        create_project()

    plan: Plan = planner.invoke(current_project)

    for common_task in plan.common_tasks:
        task.invoke(current_project)

    for backend_task in plan.backend_tasks:
        task.invoke(current_project)

    for frontend_task in plan.frontend_tasks:
        task.invoke(current_project)

    with yaspin(color="red", text="Testing build...") as spinner:
        try:
            subprocess.run(
                "npm run build",
                capture_output=True,
                text=True,
                cwd=current_project,
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout or "Unknown error"
            spinner.write("Test build failed.")


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
        color="yellow", text="Creating Next.js project with default config..."
    ) as spinner:
        try:
            subprocess.run(
                f"npx create-next-app@latest {current_project.split('/')[-1]} --yes",
                capture_output=True,
                text=True,
                cwd=current_project,
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout or "Unknown error"
            logging.error(f"Project creation failed: {error_msg}")
            spinner.write(f"npm i exited with code {e.returncode}")
            spinner.fail("❌️")
            return str(e)
