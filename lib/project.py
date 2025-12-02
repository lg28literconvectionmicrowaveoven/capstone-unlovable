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

    summary: str = ""
    with yaspin(color="yellow", text="Generating site...") as spinner:
        spinner.write("Drafting plan...")
        try:
            plan: Plan = planner.invoke({})
        except Exception as e:
            logging.error(f"Planner failed with: {str(e)}")
            spinner.fail("❌")
            raise RuntimeError("Planner failed")

        spinner.write("Executing tasks...")
        try:
            for common_task in plan.common_tasks:
                summary = task.invoke(
                    {"messages": [HumanMessage(common_task)], "carry": summary}
                )["carry"]
            for backend_task in plan.backend_tasks:
                summary = task.invoke(
                    {"messages": [HumanMessage(backend_task)], "carry": summary}
                )["carry"]
            for frontend_task in plan.frontend_tasks:
                summary = task.invoke(
                    {"messages": [HumanMessage(frontend_task)], "carry": summary}
                )["carry"]
            spinner.ok("✅")
        except Exception as e:
            logging.error(f"Task failed with: {str(e)}")
            spinner.fail("❌")
            raise RuntimeError("Task failed")

    with yaspin(color="red", text="Testing build...") as spinner:
        max_tries = 3
        tries = 0

        while tries < max_tries:
            try:
                subprocess.run(
                    "npm run build",
                    capture_output=True,
                    text=True,
                    cwd=app_state.current_project,
                    shell=True,
                    check=True,
                )
                spinner.ok("✅")
                logging.info("Build succeeded")
                return summary

            except subprocess.CalledProcessError as e:
                tries += 1
                error_msg = e.stderr or e.stdout or "Unknown error"

                spinner.write(f"Build failed (attempt {tries}/{max_tries})")
                logging.error(f"Build error: {error_msg}")

                if tries >= max_tries:
                    spinner.fail("❌")
                    logging.error("Could not produce working build after all retries")
                    raise RuntimeError(
                        f"Could not produce working build after {max_tries} attempts. Last error: {error_msg}"
                    )

                spinner.write("Analyzing build errors and applying fixes...")
                try:
                    heal_result = healer.invoke(
                        {
                            "messages": [
                                HumanMessage(
                                    f"Build failed with the following error. Analyze the error, identify the problematic files, and fix them:\n\n{error_msg}\n\nPrevious summary: {summary}"
                                )
                            ],
                            "carry": summary,
                            "project_path": app_state.current_project,
                        }
                    )

                    summary = heal_result.get("carry", summary)

                    spinner.write(
                        f"Applied fixes. Retrying build ({max_tries - tries} attempts remaining)..."
                    )

                except Exception as heal_error:
                    logging.error(f"Healer failed: {str(heal_error)}")
                    spinner.write(
                        f"Warning: Auto-fix attempt failed: {str(heal_error)}"
                    )

        spinner.fail("❌")
        raise RuntimeError("Build healing loop exited unexpectedly")


def revert_project():
    logging.info(f"Reverting project {app_state.current_project} to original state...")
    try:
        for item in os.listdir(app_state.current_project):
            if not item == "prompts":
                path = f"{app_state.current_project}/{item}"
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

        for item in os.listdir(f"{app_state.current_project}/prompts"):
            shutil.move(
                f"{app_state.current_project}/prompts/{item}",
                f"{app_state.current_project}",
            )
    except FileNotFoundError as e:
        logging.error(f"Project directory not found: {e}")
        return f"Project directory not found: {e}"
    except PermissionError as e:
        logging.error(f"Permission denied: {e}")
        return f"Permission denied: {e}"
    except Exception as e:
        logging.error(f"Unexpected error during project revert: {e}")
        return f"Unexpected error: {e}"


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
