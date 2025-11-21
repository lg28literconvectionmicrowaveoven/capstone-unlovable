import os
import logging
import subprocess
from yaspin import yaspin
from yaspin.spinners import Spinners


# TODO: fix logging not working
def build_landing():
    if "dist" not in os.listdir("./frontend"):
        LANDING_BUILD_MSG = "Building landing page..."

        with yaspin(Spinners.earth, text=LANDING_BUILD_MSG) as spinner:
            logging.info(LANDING_BUILD_MSG)

            logging.info("Installing dependencies...")
            spinner.write("> npm i")
            dep_output = subprocess.run(
                ["npm", "i"], capture_output=True, text=True, cwd="./frontend"
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
                ["npm", "i", "-D"], capture_output=True, text=True, cwd="./frontend"
            )

            if dev_dep_out.returncode != 0:
                logging.error(
                    f"Landing build failed during dev dependency install: {dev_dep_out.stderr}"
                )
                spinner.write(f"npm i -D exited with code {dev_dep_out.returncode}")
                spinner.fail("❌️")
                exit(1)

            spinner.write("> npm run build")
            build_output = subprocess.run(
                ["npm", "run", "build"],
                capture_output=True,
                text=True,
                cwd="./frontend",
            )

            if build_output.returncode != 0:
                logging.error(f"Landing build failed: {build_output.stderr}")
                spinner.write(
                    f"npm run build exited with code {build_output.returncode}"
                )
                spinner.fail("❌️")
                exit(1)

            spinner.ok("✅️")
