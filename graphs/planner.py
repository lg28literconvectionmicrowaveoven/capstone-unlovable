from langchain.messages import (
    SystemMessage,
    HumanMessage,
    AnyMessage,
)
from langgraph.graph import StateGraph, START, END
from graphs.tools import search_internet
from graphs import commons
from globals import app_state
from pydantic import BaseModel, Field
from typing import TypedDict
import os

PLANNER_SYSTEM_MESSAGE = """
You are an expert NextJS project architect and planner. Your role is to analyze project requirements and create a comprehensive, actionable development plan. Assume that the project has TailwindCSS and ESLint preconfigured.

## Your Responsibilities:
1. **Analyze Requirements**: Carefully review all route prompts and understand the full scope of the project
2. **Identify Dependencies**: Determine which npm packages (both regular and dev dependencies) are needed
3. **Plan Component Architecture**: Identify reusable components that should be shared across multiple pages
4. **Create Task Breakdown**: Generate detailed, sequential tasks for building the application

## Planning Guidelines:
- **Common Tasks First**: Identify shared components, utilities, and configurations that multiple pages will use
- **Dependency Management**: Install all necessary packages upfront (UI libraries, state management, styling tools, etc.)
- **Atomic Tasks**: Each task should be focused and completable independently
- **Clear Instructions**: Provide specific implementation details for each component and page
- **Modern Best Practices**: Use Next.js 14+ features (App Router, Server Components, etc.) when appropriate

## Output Format:
You MUST respond with a list of: -
- Common tasks: tasks for shared components, layouts, utilities, and configurations
- Backend tasks: tasks for backend components and routes using resources only specified by the user
- Frontend Tasks: tasks for individual pages and route-specific components

Ensure tasks are ordered in such a way that every subsequent task has all it's prerequisite shared code already available. Common tasks will be executed first, then backend tasks, and then frontend tasks.

Each task should include:
- What to build (component/page name and purpose)
- Where to place it (file path)
- Key functionality and features
- Any dependencies on other tasks
- Any dependencies on external resources specified to be located in specific folders inside the project prompt.
"""
TOOLS_MAP = {"search_internet": search_internet}


class Plan(BaseModel):
    """Structured output for the planner containing common tasks and page-specific tasks"""

    common_tasks: list[str] = Field(
        description="List of tasks for shared components, utilities, layouts, and configurations that will be used across multiple pages"
    )
    backend_tasks: list[str] = Field(
        description="List of tasks for building server components and routes"
    )
    frontend_tasks: list[str] = Field(
        description="List of tasks for building individual pages and route-specific components"
    )


class PlannerState(TypedDict):
    """State for the planner graph"""

    messages: list[AnyMessage]
    common_tasks: list[str]
    backend_tasks: list[str]
    frontend_tasks: list[str]


def read_prompts_node(state: PlannerState) -> dict[str, list[AnyMessage]]:
    """First node that reads prompts from the project path and initializes state"""
    messages: list[AnyMessage] = [SystemMessage(PLANNER_SYSTEM_MESSAGE)]

    with open(f"{app_state.current_project}/prompts/index.txt", "r") as root_prompt:
        messages.append(HumanMessage(f"/: -\n\n{root_prompt.read()}"))

    def recursive_read_prompts(prompt_path: str) -> None:
        for entry in os.listdir(prompt_path):
            full_path = os.path.join(prompt_path, entry)
            if os.path.isdir(full_path):
                recursive_read_prompts(full_path)
            elif entry == "index.txt":
                with open(full_path, "r") as prompt:
                    relative_path = prompt_path.replace(
                        f"{app_state.current_project}/prompts", ""
                    ).strip("/")
                    messages.append(
                        HumanMessage(f"{relative_path or '/'}: -\n\n{prompt.read()}")
                    )

    recursive_read_prompts(f"{app_state.current_project}/prompts/")

    return {"messages": messages}


def planner_node(state: PlannerState) -> dict[str, list[AnyMessage]]:
    """Planner node that uses tools"""
    return commons.get_tool_llm_node(TOOLS_MAP)(state["messages"])


def tools_node(state: PlannerState) -> dict[str, list[AnyMessage]]:
    """Tools execution node"""
    return commons.get_tool_executor(TOOLS_MAP)(state["messages"])


def structure_output(state: PlannerState) -> dict[str, list[str]]:
    """Extract and structure the final output into Plan format"""
    structured_llm = app_state.model.with_structured_output(Plan)

    final_messages = state["messages"] + [
        HumanMessage(
            "Based on all the information gathered and dependencies installed, "
            "now provide your final plan in the required JSON format with 'common_tasks' and 'tasks' arrays."
        )
    ]

    plan: Plan = structured_llm.invoke(final_messages)

    return {
        "common_tasks": plan.common_tasks,
        "backend_tasks": plan.backend_tasks,
        "frontend_tasks": plan.frontend_tasks,
    }


def tools_edge_wrapper(state: PlannerState) -> str:
    """Wrapper for tools_edge that works with PlannerState"""
    return commons.tools_edge(state["messages"])


builder = StateGraph(state_schema=PlannerState, output=Plan)

builder.add_node("read_prompts", read_prompts_node)
builder.add_node("planner", planner_node)
builder.add_node("tools", tools_node)
builder.add_node("structure_output", structure_output)

builder.add_edge(START, "read_prompts")
builder.add_edge("read_prompts", "planner")
builder.add_conditional_edges(
    "planner", tools_edge_wrapper, {"tools": "tools", "continue": "structure_output"}
)
builder.add_edge("tools", "planner")
builder.add_edge("structure_output", END)

planner = builder.compile()
