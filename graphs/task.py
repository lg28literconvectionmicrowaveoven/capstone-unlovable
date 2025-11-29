from langchain.tools import tool
from langchain.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from globals import current_project, model
from json import load as json_load
from typing import Literal
from graphs.commons import search_internet
import logging
import subprocess
import os

TASK_SYSTEM_PROMPT = """
You are an expert Next.js 14+ full-stack **implementation agent**. You take one task at a time from the Planner and use your available tools to perform the exact file operations, dependency installations, and searches required to complete that task.

Your responsibility is to precisely execute tasks — not design new architecture, not refactor, not guess.

You have the following capabilities:
- Create, overwrite, and modify project files through tool calls.
- Install dependencies and devDependencies when the Planner explicitly allows them.
- Perform web searches to retrieve information needed for correct implementation.
- Read existing project files when required.
Only use these capabilities when necessary and when in direct service of the active task.

## Your Core Responsibilities

### 1. Interpret the Task Exactly
- Understand what component, API route, page, layout, config, or utility must be implemented.
- Identify exactly which files need to be created, updated, or replaced.
- Never perform work beyond the scope of the task.

### 2. Use Tools to Implement the Task
- Create or modify files using the appropriate file-operation tools.
- Install dependencies ONLY when the Planner's task instructions require them.
- Use internet search ONLY when needed for factual correctness (syntax, API references, library usage).
- Every tool call must be atomic, purposeful, and relevant to the task.

### 3. Follow Project Conventions
- Use the Next.js App Router (app/ directory structure).
- Correctly choose Server vs Client Components.
- Maintain existing code style and folder layout.
- Use ONLY the dependencies and devDependencies approved or listed by the Planner.
- Never introduce unapproved libraries.

### 4. Deterministic, Minimal, and Safe Execution
- Only change files that the task explicitly requires.
- Do not create unrequested components, hooks, routes, utilities, or configuration.
- Do not modify unrelated parts of existing files.
- Ask for clarification when the task is ambiguous or contradictory.

### 5. High-Quality Code Output
- Generate complete, functional file contents.
- Include accurate imports and exports.
- Follow Next.js 14+ and React best practices.
- Ensure the feature works as described by the Planner.

## Output Requirements (NO EXCEPTIONS)

You MUST respond in this format:

### 1. Tool Calls
Use tool calls to:
- Create or update files
- Install dependencies
- Perform searches if needed

Each tool call must contain only the minimal operations required for the current task.

### 2. No Extra Commentary
Do NOT include design opinions, architectural suggestions, or additional ideas in the code that you write.

Any and all standard output will be discarded since this is a non-interactive environment so ensure that all the code you write is to the best of your ability.

## Rules (Hard)
- Do NOT change ANYTHING not directly requested by the task.
- Do NOT install dependencies unless the Planner explicitly indicated they are allowed.
- Do NOT create extra files or abstractions. Simply use the existing ones.
- Do NOT perform Planner responsibilities such as designing architecture.

You exist solely to **execute** the Planner’s tasks with perfect accuracy using the provided tools.
"""


@tool
def list_dependencies() -> str:
    """
    Lists npm dependencies and devDependencies installed on the current NextJS project.
    """
    package_json = json_load(f"{current_project}/package.json")
    return {
        "dependencies": package_json.dependencies,
        "devDependencies": package_json.devDependencies,
    }


@tool
def install_dependencies(package_names: list[str]):
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
def install_dev_dependencies(package_names: list[str]) -> str:
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
        return (
            f"Error installing packages: {', '.join(package_names)}\nError: {error_msg}"
        )
    except Exception as e:
        return f"Unexpected error installing dev packages: {str(e)}"


@tool
def read_project_file(rel_path: str) -> str:
    """
    Reads any file in the project given a file path where / is the project root (e.g., /src, /tsconfig.json).
    """
    if rel_path == "/package.json" or rel_path == "/package-lock.json":
        return "Wrong tool"

    try:
        full_path = os.path.join(current_project, rel_path)

        if not os.path.exists():
            return "File does not exist"

        with open(full_path, "r") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Reading from file {full_path} failed with: {str(e)}")
        return f"Reading from file {full_path} failed with: {str(e)}"


@tool
def write_project_file(rel_path: str, content: str) -> str:
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


def init_node(task: str) -> list[AnyMessage]:
    return [SystemMessage(TASK_SYSTEM_PROMPT), HumanMessage(task)]


TOOLS_MAP = {
    "search_internet": search_internet,
    "install_dependencies": install_dependencies,
    "install_dev_dependencies": install_dev_dependencies,
    "read_project_file": read_project_file,
    "write_project_file": write_project_file,
}

tool_llm = model.bind_tools(list(TOOLS_MAP.values()))


def task_llm(state: list[AnyMessage]) -> list[AnyMessage]:
    return state + [tool_llm.invoke(state)]


def tool_executor(state: list[AnyMessage]) -> list[AnyMessage]:
    """Node that executes tools based on the last AI message"""
    last_message = state[-1]

    tool_messages = []

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            if tool_name in TOOLS_MAP:
                result = TOOLS_MAP[tool_name].invoke(tool_args)
            else:
                result = f"Unknown tool: {tool_name}"

            tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_id))

    return state + tool_messages


def should_continue(state: list[AnyMessage]) -> Literal["tools", END]:
    last_message = state[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return END


builder = StateGraph(input_schema=str, state_schema=list[AnyMessage])

builder.add_node("init", init_node)
builder.add_node("task", task_llm)
builder.add_node("tools", tool_executor)

builder.add_edge(START, "init")
builder.add_edge("init", "task")
builder.add_conditional_edges("task", should_continue)
builder.add_edge("tools", "planner")

task = builder.compile()
