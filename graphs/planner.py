from langchain.messages import (
    SystemMessage,
    HumanMessage,
    AnyMessage,
    AIMessage,
    ToolMessage,
)
from langgraph.graph import StateGraph, START, END
from globals import model, current_project
from langchain.tools import tool
from typing import TypedDict, Literal
from graphs.commons import search_internet
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
    try:
        npm_i_out = subprocess.run(
            ["npm", "i", *package_names],
            capture_output=True,
            text=True,
            cwd=current_project,
            check=True,
        )
        return f"Successfully installed packages: {', '.join(package_names)}\n{npm_i_out.stdout}"
    except subprocess.CalledProcessError as e:
        return (
            f"Error installing packages: {', '.join(package_names)}\nError: {e.stderr}"
        )
    except Exception as e:
        return f"Unexpected error installing packages: {str(e)}"


@tool
def install_dev_dependencies(package_names: list[str]):
    """
    Installs npm development packages to the current NextJS project given npm package names and project path.
    """
    try:
        npm_i_d_out = subprocess.run(
            ["npm", "i", "-D", *package_names],
            capture_output=True,
            text=True,
            cwd=current_project,
            check=True,
        )
        return f"Successfully installed dev packages: {', '.join(package_names)}\n{npm_i_d_out.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Error installing dev packages: {', '.join(package_names)}\nError: {e.stderr}"
    except Exception as e:
        return f"Unexpected error installing dev packages: {str(e)}"


tools_map = {
    "search_internet": search_internet,
    "install_dependencies": install_dependencies,
    "install_dev_dependencies": install_dev_dependencies,
}


def read_prompts_node(path: str) -> PlannerState:
    """First node that reads prompts from the project path and initializes state"""
    messages: list[AnyMessage] = [SystemMessage(PLANNER_SYSTEM_MESSAGE)]

    with open(f"{path}/prompts/index.txt", "r") as root_prompt:
        messages.append(HumanMessage(f"/: -\n\n{root_prompt.read()}"))

    def recursive_read_prompts(prompt_path: str):
        for entry in os.listdir(prompt_path):
            full_path = os.path.join(prompt_path, entry)
            if os.path.isdir(full_path):
                recursive_read_prompts(full_path)
            elif entry == "index.txt":
                with open(full_path, "r") as prompt:
                    relative_path = prompt_path.replace(f"{path}/prompts", "").strip(
                        "/"
                    )
                    messages.append(
                        HumanMessage(f"{relative_path or '/'}: -\n\n{prompt.read()}")
                    )

    recursive_read_prompts(f"{path}/prompts/")

    return {"project_path": path, "messages": messages}


def planner_llm_node(state: PlannerState) -> PlannerState:
    """Node that calls the LLM with tool binding"""
    tool_llm = model.bind_tools(
        [search_internet, install_dependencies, install_dev_dependencies]
    )

    response = tool_llm.invoke(state["messages"])
    return {
        "project_path": state["project_path"],
        "messages": state["messages"] + [response],
    }


def tool_executor_node(state: PlannerState) -> PlannerState:
    """Node that executes tools based on the last AI message"""
    messages = state["messages"]
    last_message = messages[-1]

    tool_messages = []

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            if tool_name in tools_map:
                result = tools_map[tool_name].invoke(tool_args)
            else:
                result = f"Unknown tool: {tool_name}"

            tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_id))

    return {"project_path": state["project_path"], "messages": messages + tool_messages}


def should_continue(state: PlannerState) -> Literal["tools", "end"]:
    """Conditional edge that determines if we should call tools or end"""
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "end"


def extract_final_output(state: PlannerState) -> str:
    """Extract the final text content from the last AI message"""
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage):
        return last_message.content

    for message in reversed(state["messages"]):
        if isinstance(message, AIMessage) and message.content:
            return message.content

    return "No plan generated"


builder = StateGraph(state_schema=PlannerState, input=str, output=str)

builder.add_node("read_prompts", read_prompts_node)
builder.add_node("planner", planner_llm_node)
builder.add_node("tools", tool_executor_node)
builder.add_node("extract_output", extract_final_output)

builder.add_edge(START, "read_prompts")
builder.add_edge("read_prompts", "planner")
builder.add_conditional_edges(
    "planner", should_continue, {"tools": "tools", "end": "extract_output"}
)
builder.add_edge("tools", "planner")
builder.add_edge("extract_output", END)

planner = builder.compile()
