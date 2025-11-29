import os
import logging
import subprocess
import platform
from yaspin import yaspin
from yaspin.spinners import Spinners
from globals import sigint


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

    # FIX: return code pollution
    app_output = subprocess.run(
        launch_cmd,
        capture_output=True,
        text=True,
    )

    # FIX: does not need to log error when exiting via SIGINT
    if app_output.returncode != 0 and not sigint:
        logging.error(f"Error when running tauri app: {app_output.stderr}")
        exit(1)
    else:
        logging.info("Exiting unlovable...")
        exit(0)


def build_app():
    if "dist" not in os.listdir("./tauri"):
        LANDING_BUILD_MSG = "Building application..."

        with yaspin(Spinners.earth, text=LANDING_BUILD_MSG) as spinner:
            logging.info(LANDING_BUILD_MSG)

            logging.info("Installing dependencies...")
            spinner.write("> npm i")
            dep_output = subprocess.run(
                ["npm", "i"], capture_output=True, text=True, cwd="./tauri"
            )

            if dep_output.returncode != 0:
                logging.error(
                    f"Landing build failed during dependency install: {dep_output.stderr}"
                )
                spinner.write(f"npm i exited with code {dep_output.returncode}")
                spinner.fail("❌️")
                exit(1)

            logging.info("Installing dev dependencies...")
            spinner.write("> npm i -D")
            dev_dep_out = subprocess.run(
                ["npm", "i", "-D"], capture_output=True, text=True, cwd="./tauri"
            )

            if dev_dep_out.returncode != 0:
                logging.error(
                    f"Landing build failed during dev dependency install: {dev_dep_out.stderr}"
                )
                spinner.write(f"npm i -D exited with code {dev_dep_out.returncode}")
                spinner.fail("❌️")
                exit(1)

            spinner.write("> npm run tauri build")
            build_output = subprocess.run(
                ["npm", "run", "build"],
                capture_output=True,
                text=True,
                cwd="./tauri",
            )

            if build_output.returncode != 0:
                logging.error(f"Landing build failed: {build_output.stderr}")
                spinner.write(
                    f"npm run build exited with code {build_output.returncode}"
                )
                spinner.fail("❌️")
                exit(1)

            spinner.ok("✅️")
