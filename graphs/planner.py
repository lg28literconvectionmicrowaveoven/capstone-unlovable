from langchain.messages import SystemMessage, HumanMessage, AnyMessage
from langgraph.graph import StateGraph
from main import model
from langchain.tools import tool
from typing import TypedDict
from globals import state
import os
import subprocess

PLANNER_SYSTEM_MESSAGE = "You are an assistant whose purpose is to plan and bootstrap a basic NextJS project based on the requirements given. You may choose to install third-party libraries to enhance the resulting website if necessary. You will be given the prompts for the various routes. Using this information, create a detailed schematic in text of the various components in each page, their design particulars, scripting, and any common components."


class PlannerState(TypedDict):
    project_path: str
    messages: list[AnyMessage]


@tool
def install_dependencies(package_names: list[str]):
    """
    Installs npm packages to the current NextJS project given npm package names and project path.
    """
    npm_i_out = subprocess.run(
        ["npm", "i", *package_names],
        capture_output=True,
        text=True,
        cwd=state["current_project"],
    )


def install_dev_dependencies(package_names: list[str]):
    """
    Installs npm development packages to the current NextJS project given npm package names and project path.
    """
    npm_i_d_out = subprocess.run(
        ["npm", "i", "-D", *package_names],
        capture_output=True,
        text=True,
        cwd=state["current_project"],
    )


def read_prompts(path: str) -> list[AnyMessage]:
    messages: list[AnyMessage] = [SystemMessage(PLANNER_SYSTEM_MESSAGE)]

    with open(f"{path}/prompts/index.txt", "r") as root_prompt:
        messages.append(HumanMessage(f"/: -\n\n{root_prompt.read()}"))

    def recursive_read_prompts(path: str):
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                recursive_read_prompts(full_path)
            else:
                with open("index.txt", "r") as prompt:
                    messages.append(
                        HumanMessage(
                            f"{path.split('/')[path.index('prompts') + 1 :]}: -\n\n{prompt.read()}"
                        )
                    )

    recursive_read_prompts(f"{path}/prompts/")

    return messages

def planner_llm(messages: list[AnyMessage]) -> list[AnyMessage]:
    


builder = StateGraph(input_schema=str, state_schema=list[AnyMessage], output_schema=str)
