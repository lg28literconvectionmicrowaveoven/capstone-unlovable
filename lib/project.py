import logging
import os
import shutil
import subprocess
from yaspin import yaspin
from globals import app_state
from graphs.planner import planner, Plan
from graphs.task import task
from graphs.self_heal import healer
from langchain.messages import HumanMessage


# TODO: generate a README using the planner's output
# TODO: properly handle project generation failure/error
def generate_project():
    logging.info(f"Opening project {app_state.current_project}")

    if "prompts" not in os.listdir(app_state.current_project):
        try:
            prompts_dir = f"{app_state.current_project}/prompts"
            os.makedirs(prompts_dir, exist_ok=True)

            root_index = f"{app_state.current_project}/index.txt"
            if os.path.exists(root_index):
                try:
                    shutil.move(root_index, prompts_dir)
                except (PermissionError, OSError) as e:
                    logging.error(f"Failed to move index.txt: {e}")
                    return f"Failed to move index.txt: {e}"

            for item in os.listdir(app_state.current_project):
                try:
                    if item.startswith("."):
                        continue
                    item_path = f"{app_state.current_project}/{item}"

                    if not os.path.isdir(item_path):
                        continue
                    if item == "prompts":
                        continue
                    if os.path.exists(f"{item_path}/index.txt"):
                        shutil.move(item_path, f"{prompts_dir}/{item}")
                except (PermissionError, OSError, shutil.Error) as e:
                    logging.error(f"Failed to move folder '{item}': {e}")
                    continue

            with yaspin(
                color="yellow", text="Creating Next.js project with default config..."
            ) as spinner:
                try:
                    env = os.environ.copy()
                    env["CI"] = "1"
                    subprocess.run(
                        f"npx create-next-app@latest {app_state.current_project.split('/')[-1]} --yes --tailwind --eslint --src-dir --app --ts",
                        capture_output=True,
                        text=True,
                        cwd=app_state.current_project,
                        shell=True,
                        check=True,
                        env=env,
                    )
                    for item in os.listdir(
                        f"{app_state.current_project}/{app_state.current_project.split('/')[-1]}"
                    ):
                        shutil.move(
                            f"{app_state.current_project}/{app_state.current_project.split('/')[-1]}/{item}",
                            app_state.current_project,
                        )
                    os.rmdir(
                        f"{app_state.current_project}/{app_state.current_project.split('/')[-1]}"
                    )
                    spinner.ok("✅")
                except subprocess.CalledProcessError as e:
                    error_msg = e.stderr or e.stdout or "Unknown error"
                    logging.error(f"Project creation failed: {error_msg}")
                    spinner.write(f"create-next-app exited with code {e.returncode}")
                    spinner.fail("❌")
                    return f"Project creation failed: {error_msg}"

        except FileNotFoundError as e:
            logging.error(f"Project directory not found: {e}")
            return f"Project directory not found: {e}"
        except PermissionError as e:
            logging.error(f"Permission denied: {e}")
            return f"Permission denied: {e}"
        except Exception as e:
            logging.error(f"Unexpected error during project creation: {e}")
            return f"Unexpected error: {e}"

    try:
        plan: Plan = planner.invoke({})

        print()
        print(plan)
        print()

        for common_task in plan.common_tasks:
            task.invoke({"messages": [HumanMessage(common_task)]})
            # task.invoke(common_task)
        for backend_task in plan.backend_tasks:
            task.invoke({"messages": [HumanMessage(backend_task)]})
            # task.invoke(backend_task)
        for frontend_task in plan.frontend_tasks:
            task.invoke({"messages": [HumanMessage(frontend_task)]})
            # task.invoke(frontend_task)

        with yaspin(color="red", text="Testing build...") as spinner:
            tries = 3
            build_fail = True
            while tries > 0 and build_fail:
                try:
                    subprocess.run(
                        "npm run build",
                        capture_output=True,
                        text=True,
                        cwd=app_state.current_project,
                        shell=True,
                        check=True,
                    )
                    build_fail = False
                except subprocess.CalledProcessError as e:
                    build_fail = True
                    error_msg = e.stderr or e.stdout or "Unknown error"
                    spinner.write("Test build failed.")
                    spinner.write("Trying to fix the bug.")
                    healer.invoke({"messages": [HumanMessage(error_msg)]})
                    # healer.invoke(error_msg)
                    tries -= 1
                    spinner.write(f"Retrying build, {tries} tries left.")

            if build_fail:
                spinner.write("Could not produce working build.")
                raise RuntimeError("Could not produce working build.")
    except Exception as e:
        print(str(e))


def project_dev_server():
    logging.info(
        f"Running project {app_state.current_project.split('/')[-1]} dev server"
    )

    subprocess.run(
        "npm run dev",
        text=True,
        cwd=app_state.current_project,
        shell=True,
        check=True,
    )
