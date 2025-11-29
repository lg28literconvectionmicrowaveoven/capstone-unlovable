import os
import logging
import subprocess
import platform
from yaspin import yaspin


def launch_app():
    os_flavor = platform.system()
    launch_cmd = []
    if os_flavor == "Linux":
        launch_cmd = [
            "env",
            "__NV_DISABLE_EXPLICIT_SYNC=1",
            "./tauri/src-tauri/target/release/frontend",
        ]
    elif os_flavor == "Windows":
        launch_cmd = ["./tauri/src-tauri/target/release/frontend.exe"]
    else:
        logging.error("Unsupported OS")
        exit(1)

    # FIX: return code 3 when GUI exits
    try:
        subprocess.run(launch_cmd, check=True)
        logging.info("Exiting unlovable...")
        exit(0)
    except subprocess.CalledProcessError as e:
        logging.error(f"Application failed with exit code: {e.returncode}")
    except FileNotFoundError:
        logging.error(f"Executable not found: {launch_cmd[0]}")


def build_app():
    if "target" not in os.listdir("./tauri/src-tauri"):
        BUILD_MSG = "Building application... (this could take a bit)"
        with yaspin(text=BUILD_MSG, color="green") as spinner:
            logging.info(BUILD_MSG)

            logging.info("Installing dependencies...")
            spinner.write("> npm i")
            try:
                subprocess.run(
                    "npm i",
                    capture_output=True,
                    text=True,
                    cwd="./tauri",
                    shell=True,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr or e.stdout or "Unknown error"
                logging.error(
                    f"Application build failed during dependency install: {error_msg}"
                )
                spinner.write(f"npm i exited with code {e.returncode}")
                spinner.fail("❌️")
                exit(1)

            logging.info("Installing dev dependencies...")
            spinner.write("> npm i -D")
            try:
                subprocess.run(
                    "npm i -D",
                    capture_output=True,
                    text=True,
                    cwd="./tauri",
                    shell=True,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr or e.stdout or "Unknown error"
                logging.error(
                    f"Application build failed during dev dependency install: {error_msg}"
                )
                spinner.write(f"npm i -D exited with code {e.returncode}")
                spinner.fail("❌️")
                exit(1)

            spinner.write("> npm run tauri build")
            try:
                subprocess.run(
                    "npm run tauri build",
                    capture_output=True,
                    text=True,
                    cwd="./tauri",
                    shell=True,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr or e.stdout or "Unknown error"
                logging.error(f"Application build failed: {error_msg}")
                spinner.write(f"npm run tauri build exited with code {e.returncode}")
                spinner.fail("❌️")
                exit(1)

            spinner.ok("✅️")
