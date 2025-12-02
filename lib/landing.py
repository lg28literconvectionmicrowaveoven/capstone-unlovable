import os
import logging
import subprocess
import platform
import atexit
import signal
from yaspin import yaspin

child_proc = None


def cleanup():
    global child_proc
    if child_proc and child_proc.poll() is None:
        try:
            if platform.system() != "Windows":
                os.killpg(os.getpgid(child_proc.pid), signal.SIGTERM)
            else:
                child_proc.terminate()
        except Exception:
            pass


atexit.register(cleanup)


def launch_app():
    global child_proc

    if "target" not in os.listdir("./tauri/src-tauri"):
        BUILD_MSG = "Building application... (this could take a bit)"
        with yaspin(text=BUILD_MSG, color="green") as spinner:
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

    os_flavor = platform.system()
    env = os.environ.copy()
    env["__NV_DISABLE_EXPLICIT_SYNC"] = "1"

    if os_flavor == "Linux":
        launch_cmd = "./tauri/src-tauri/target/release/frontend"
    elif os_flavor == "Windows":
        launch_cmd = ".\\tauri\\src-tauri\\target\\release\\frontend.exe"
    else:
        logging.error("Unsupported OS")
        exit(1)

    try:
        logging.info("Launching tauri app")
        child_proc = subprocess.run(
            launch_cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or "Unknown error"
        logging.error(f"Application launch failed: {error_msg}")
        spinner.write(f"Application exited with code {e.returncode}")
        spinner.fail("❌️")
        exit(1)
    except FileNotFoundError:
        logging.error(f"Executable not found: {launch_cmd[0]}")
        exit(1)
