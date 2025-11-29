from langchain.tools import tool
from globals import current_project, serper
from json import load as json_load
import subprocess
import os
import logging


@tool
def search_internet(query: str) -> str:
    """
    Search the internet for any query and receive a string response.
    """
    return serper.run(query)


@tool
def list_dependencies() -> dict[str, list[str]] | str:
    """
    Lists npm dependencies and devDependencies installed on the current NextJS project. Returns error message if read fails.
    """

    try:
        with open(f"{current_project}/package.json") as file:
            package_json = json_load(file)
    except Exception as e:
        return f"Failed to read package.json with error: {str(e)}"

    return {
        "dependencies": package_json.dependencies,
        "devDependencies": package_json.devDependencies,
    }


@tool
def install_dependencies(package_names: list[str]) -> str | None:
    """
    Installs npm packages to the current NextJS project given npm package names.
    """
    try:
        npm_i_out = subprocess.run(
            f"npm i {' '.join(package_names)}",
            capture_output=True,
            text=True,
            cwd=current_project,
            check=True,
            shell=True,
        )
        return f"Successfully installed packages: {', '.join(package_names)}\n{npm_i_out.stdout}"
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or "Unknown error"
        return (
            f"Error installing packages: {', '.join(package_names)}\nError: {error_msg}"
        )
    except Exception as e:
        return f"Unexpected error installing packages: {str(e)}"


@tool
def install_dev_dependencies(package_names: list[str]) -> str | None:
    """
    Installs npm development packages to the current NextJS project given npm package names.
    """
    try:
        npm_i_d_out = subprocess.run(
            f"npm i -D {' '.join(package_names)}",
            capture_output=True,
            text=True,
            cwd=current_project,
            check=True,
            shell=True,
        )
        return f"Successfully installed dev packages: {', '.join(package_names)}\n{npm_i_d_out.stdout}"
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or "Unknown error"
        return f"Error installing dev packages: {', '.join(package_names)}\nError: {error_msg}"
    except Exception as e:
        return f"Unexpected error installing dev packages: {str(e)}"


@tool
def remove_dependencies(package_names: list[str]) -> str | None:
    """
    Removes npm packages currently installed on the NextJS project given npm package names.
    """
    try:
        npm_rm_out = subprocess.run(
            f"npm rm {' '.join(package_names)}",
            capture_output=True,
            text=True,
            cwd=current_project,
            check=True,
            shell=True,
        )
        return f"Successfully removed packages: {', '.join(package_names)}\n{npm_rm_out.stdout}"
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or "Unknown error"
        return (
            f"Error removing packages: {', '.join(package_names)}\nError: {error_msg}"
        )
    except Exception as e:
        return f"Unexpected error removing packages: {str(e)}"


@tool
def remove_dev_dependencies(package_names: list[str]) -> str | None:
    """
    Removes npm development packages currently installed on the NextJS project given npm package names.
    """
    try:
        npm_rm_d_out = subprocess.run(
            f"npm rm -D {' '.join(package_names)}",
            capture_output=True,
            text=True,
            cwd=current_project,
            check=True,
            shell=True,
        )
        return f"Successfully removed dev packages: {', '.join(package_names)}\n{npm_rm_d_out.stdout}"
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr or e.stdout or "Unknown error"
        return f"Error removing dev packages: {', '.join(package_names)}\nError: {error_msg}"
    except Exception as e:
        return f"Unexpected error removing dev packages: {str(e)}"


@tool
def read_project_file(rel_path: str) -> str:
    """
    Reads any file in the project given a file path where / is the project root (e.g., /src, /tsconfig.json).
    """
    if rel_path == "/package.json" or rel_path == "/package-lock.json":
        return "Wrong tool"

    try:
        full_path = os.path.join(current_project, rel_path)

        if not os.path.exists(full_path):
            return "File does not exist"

        with open(full_path, "r") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Reading from file {full_path} failed with: {str(e)}")
        return f"Reading from file {full_path} failed with: {str(e)}"


@tool
def write_project_file(rel_path: str, content: str) -> str | None:
    """
    Overwrites string to any project file given a file path in where / is the project root (e.g., /src, /tsconfig.json). Creates file if does not exist.
    """
    if rel_path == "/package.json" or rel_path == "/package-lock.json":
        return "Cannot modify npm packages directly"

    try:
        full_path = os.path.join(current_project, rel_path)

        os.makedirs(full_path)

        with open(full_path, "w") as file:
            file.write(content)

        return "Write successful"
    except Exception as e:
        logging.error(f"Writing to file {full_path} failed with: {str(e)}")
        return f"Writing to file {full_path} failed with: {str(e)}"
