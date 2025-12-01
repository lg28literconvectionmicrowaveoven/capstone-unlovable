from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from graphs.tools import search_internet
from globals import app_state
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, Annotated
from operator import add
from langchain_core.runnables import RunnableLambda
import os

# TODO: fix prompt
PLANNER_SYSTEM_MESSAGE = """
You are the PLANNER agent in a multi-agent system.
Your responsibility is to transform a sequence of route prompts into a complete, logically ordered development plan for a Next.js application.
## PROJECT CONTEXT
All work will be executed inside a Next.js project that is already set up with:
- TypeScript
- TailwindCSS
- ESLint configured for modern best practices
- The App Router (`app/` directory) following the latest Next.js standards
The planner DOES NOT write code.
The planner ONLY produces tasks.
Implementation agents will execute these tasks in order.
## INPUT
You will receive multiple prompts describing:
- Pages, routes, and their UI/UX behavior
- Shared or local components
- State handling, context, hooks, and utilities
- API routes, server actions, or backend logic
- Data needs and interactions between frontend and backend
- Any required integrations (auth, payments, persistence)
## OUTPUT STRUCTURE
Your output must consist of **three main categories**, each containing a strictly ordered list of tasks.
These tasks will be executed sequentially in the order given.
---
# 1. **Common Tasks**
A sequential list of tasks for everything used across multiple parts of the app, including:
- Shared UI components (e.g., Navbar, Footer, Buttons)
- Reusable component primitives (Card, Badge, Skeleton, etc.)
- Layouts and sub-layouts using `app/layout.tsx`
- Global context providers and client-side state where necessary
- Hooks, utilities, validators, schemas, formatter modules
- Theme configuration or TailwindCSS customizations
- Any fundamental building block required before backend or frontend work
These tasks must follow:
- Component-driven development principles
- Modern React best practices
- Server Components by default, unless client interactivity is required
- Well-organized folder structure (`components/`, `lib/`, `hooks/`, etc.)
Common tasks must appear **before any backend or frontend tasks that depend on them**.
---
# 2. **Backend Tasks**
A sequential list of tasks covering all backend logic, including:
- Next.js App Router API routes (`app/api/.../route.ts`)
- Server Actions using modern `export async function actionName()` patterns
- Data access layers (repositories/services) following separation of concerns
- Schema definitions for validation (e.g., Zod)
- Integration with external services (Auth, DB, Supabase, Stripe, etc.)
- Error handling and input validation aligned with modern guidelines
- Any infrastructure-like utilities needed for data fetching
Backend tasks must follow modern standards:
- Use Server Actions when appropriate instead of API routes for form submission
- Follow Next.js recommended conventions for edge runtime, caching, revalidation
- Explicit typing with TypeScript interfaces and type inference
- Treat backend logic as layered and testable
Backend tasks must appear **after all Common Tasks they rely on** but **before any Frontend Tasks** that use backend output.
---
# 3. **Frontend Tasks**
A sequential list of tasks covering all UI implementation, including:
- Pages under `app/.../page.tsx`
- Route structure, layouts, and segment routing
- Data fetching using Server Components (`async` components)
- Interactive components requiring `"use client"`
- Form UIs, modals, sheets, navigation, and user flows
- Composition using previously defined Common and Backend tasks
Frontend tasks must follow modern Next.js best practices:
- Use Server Components by default for rendering and data fetching
- Use Client Components only when interactivity or browser APIs are required
- Ensure all UI is accessible, responsive via TailwindCSS, and componentized
- Leverage Suspense, Streaming, and async/await patterns where beneficial
- Avoid prop drilling by using context providers defined in Common Tasks
Frontend tasks must appear **after all Common and Backend tasks they depend on**.
---
## GENERAL PLANNING RULES
### Modern Programming Guidelines
You must ensure:
- Separation of concerns:
  - UI components do not handle data-access logic
  - Backend logic is isolated into reusable modules
- Strong TypeScript typing throughout
- Predictable and consistent folder structure
- Clear dependency sequencing
### Next.js Standards You Must Follow
- Use App Router conventions (`app/` directory)
- Prefer Server Components and Server Actions
- Use `fetch()` with Next.js caching/revalidation rules
- Keep client components lightweight and minimal
- Avoid global state unless absolutely necessary
- Co-locate components and logic when it improves clarity
### Completeness
You must convert **every described feature** into one or more tasks.
If a requirement implicitly depends on something (e.g., a validation schema, helper, layout), you must create tasks for it.
If the requirements does not explicitly require advanced functionality, assume a basic static approach for it.
---
## GOAL
Produce a complete, dependency-aware roadmap that ensures implementation agents can build the entire application from start to finish—using modern programming best practices and the latest Next.js standards.
"""

TOOLS_MAP = {"search_internet": search_internet}


class Plan(BaseModel):
    common_tasks: list[str] = Field(
        description="One single string per task. Only the task description, nothing else. No 'name:', no 'description:' prefixes."
    )
    backend_tasks: list[str] = Field(
        description="One single string per task. Only the task description, nothing else."
    )
    frontend_tasks: list[str] = Field(
        description="One single string per task. Only the task description, nothing else."
    )

    class Config:
        extra = "forbid"
        str_strip_whitespace = True


class PlannerState(TypedDict):
    messages: Annotated[list[AnyMessage], add]
    plan: Plan | None


def read_prompts_node(state: PlannerState) -> dict:
    """First node that reads prompts from the project path and initializes messages."""
    messages: list[AnyMessage] = [SystemMessage(content=PLANNER_SYSTEM_MESSAGE)]
    root_path = f"{app_state.current_project}/prompts/index.txt"
    if os.path.exists(root_path):
        with open(root_path, "r", encoding="utf-8") as root_prompt:
            content = root_prompt.read().strip()
            if content:
                messages.append(HumanMessage(content=f"/: -\n\n{content}"))

    def recursive_read_prompts(prompt_path: str) -> None:
        if not os.path.exists(prompt_path):
            return
        try:
            for entry in os.listdir(prompt_path):
                full_path = os.path.join(prompt_path, entry)
                if os.path.isdir(full_path):
                    recursive_read_prompts(full_path)
                elif entry == "index.txt":
                    with open(full_path, "r", encoding="utf-8") as prompt:
                        content = prompt.read().strip()
                        if content:
                            relative_path = os.path.relpath(
                                full_path, f"{app_state.current_project}/prompts"
                            ).replace(os.sep, "/")
                            relative_path = (
                                "/" + relative_path if relative_path != "." else "/"
                            )
                            messages.append(
                                HumanMessage(content=f"{relative_path}: -\n\n{content}")
                            )
        except Exception as e:
            # Graceful fallback if directory issues
            pass

    recursive_read_prompts(f"{app_state.current_project}/prompts/")
    return {"messages": messages}


def planner_node(state: PlannerState) -> dict:
    """Planner node that calls LLM with tools bound."""
    messages = state["messages"]
    model_with_tools = app_state.model.bind_tools(list(TOOLS_MAP.values()))
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}


def tools_node(state: PlannerState) -> dict:
    """Tools execution node."""
    messages = state["messages"]
    last_message = messages[-1]
    tool_messages = []
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"messages": []}
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call.get("args", {})
        tool_id = tool_call["id"]
        if tool_name not in TOOLS_MAP:
            result = f"Error: Tool '{tool_name}' not found in tool_map"
        else:
            try:
                result = TOOLS_MAP[tool_name].invoke(tool_args)
            except Exception as e:
                result = f"Tool execution error: {str(e)}"
        tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_id))
    return {"messages": tool_messages}


def finalize_plan_node(state: PlannerState) -> dict:
    structured_llm = app_state.model.with_structured_output(Plan)
    final_messages = state["messages"] + [
        HumanMessage(
            content=(
                "OUTPUT EXACTLY THIS JSON (no explanations, no markdown, no extra fields):\n"
                "{\n"
                ' "common_tasks": ["First task only", "Second task only", "..."],\n'
                ' "backend_tasks": ["...", "..."],\n'
                ' "frontend_tasks": ["...", "..."]\n'
                "}\n"
                "Each entry must be a single short sentence describing WHAT to do. "
                "Do NOT include prefixes like 'description:', 'name:', file paths, or bullet points."
            )
        )
    ]
    plan: Plan = structured_llm.invoke(final_messages)
    return {"plan": plan}


def should_call_tools(state: PlannerState) -> Literal["tools", "continue"]:
    """Conditional edge: tools if needed, else continue."""
    last = state["messages"][-1]
    tc = getattr(last, "tool_calls", [])
    return "tools" if tc and len(tc) > 0 else "continue"


# Build the graph
workflow = StateGraph(state_schema=PlannerState)
workflow.add_node("read_prompts", read_prompts_node)
workflow.add_node("planner", planner_node)
workflow.add_node("tools", tools_node)
workflow.add_node("finalize_plan", finalize_plan_node)

workflow.add_edge(START, "read_prompts")
workflow.add_edge("read_prompts", "planner")
workflow.add_conditional_edges(
    "planner",
    should_call_tools,
    {"tools": "tools", "continue": "finalize_plan"},
)
workflow.add_edge("tools", "planner")
workflow.add_edge("finalize_plan", END)

planner_graph = workflow.compile()

# Wrapper for easy invocation (no input needed, reads from files)
planner = RunnableLambda(
    lambda input_dict: planner_graph.invoke({"messages": [], "plan": None})["plan"]
).with_types(input_type=dict, output_type=Plan)
