import logging
import os
import shutil
import subprocess
from yaspin import yaspin
from globals import current_project
from graphs.planner import planner, Plan
from graphs.task import task
from graphs.self_heal import healer


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
                check=True,
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr or e.stdout or "Unknown error"
            logging.error(f"Project creation failed: {error_msg}")
            spinner.write(f"npm i exited with code {e.returncode}")
            spinner.fail("❌️")
            return str(e)


def generate_project():
    logging.info(f"Opening project {current_project}")

    if "prompts" not in os.listdir(current_project):
        create_project()

    plan: Plan = planner.invoke()

    for common_task in plan.common_tasks:
        task.invoke(common_task)

    for backend_task in plan.backend_tasks:
        task.invoke(backend_task)

    for frontend_task in plan.frontend_tasks:
        task.invoke(frontend_task)

    with yaspin(color="red", text="Testing build...") as spinner:
        tries = 3
        build_fail = True
        while tries > 0 and build_fail:
            try:
                subprocess.run(
                    "npm run build",
                    capture_output=True,
                    text=True,
                    cwd=current_project,
                    shell=True,
                    check=True,
                )
                build_fail = False
            except subprocess.CalledProcessError as e:
                build_fail = True
                error_msg = e.stderr or e.stdout or "Unknown error"
                spinner.write("Test build failed.")
                spinner.write("Trying to fix the bug.")
                healer.invoke(error_msg)
                tries -= 1
                spinner.write(f"Retrying build, {tries} tries left.")

        if build_fail:
            spinner.write("Could not produce working build.")
            raise RuntimeError("Could not produce working build.")


def project_dev_server():
    logging.info(f"Running project {current_project.split('/')[-1]} dev server")

    subprocess.run(
        "npm run dev",
        text=True,
        cwd=current_project,
        shell=True,
        check=True,
    )
