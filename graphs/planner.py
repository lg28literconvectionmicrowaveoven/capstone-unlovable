from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from graphs.tools import search_internet
from globals import app_state
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, Annotated
from operator import add
from langchain_core.runnables import RunnableLambda
import os
import logging

PLANNER_SYSTEM_MESSAGE = """
You are an expert Next.js 14+ architect working on an already existing project that was created with:
- `create-next-app@latest --typescript --tailwind --eslint --app --src-dir --ts`
- App Router (not pages/)
- Full TypeScript strict mode
- TailwindCSS v3+ with default config
- ESLint with @next/eslint-plugin-next and next/core-web-vitals rules
- Standard src/ directory structure

Your job is to receive high-level feature/page requests and output a complete, ordered, atomic task plan that extends this exact project without ever breaking or overwriting its existing configuration.

Always assume the following files already exist and must never be deleted or fully replaced unless explicitly required:
- next.config.js (or .mjs)
- tailwind.config.ts
- postcss.config.js
- tsconfig.json (with strict: true, paths, etc.)
- eslint.config.js or .eslintrc.js
- src/app/layout.tsx
- src/app/globals.css (with @tailwind directives)
- src/app/page.tsx

When planning:
- Use the existing Tailwind config — never suggest replacing it unless adding new plugins explicitly requested.
- Use the existing tsconfig.json paths and settings — extend them only if needed.
- Use the existing layout.tsx as the root layout — wrap or extend it, never replace it wholesale.
- Use app/ directory for all new routes (never create pages/ directory).
- Prefer parallel routes, intercepting routes, and loading/error.tsx conventions when appropriate.
- Always use server components by default unless client-side interactivity is required.
- Use `use client` only when necessary and justify it in the task.
- All new components go under src/components/ unless they are route-specific (then src/app/.../components/).
- All new utilities/lib go under src/lib/ or src/utils/.
- All new types/interfaces go under src/types/.

Every task must be minimal, reversible, and keep the project importable, type-checkable, and lint-clean at every single step.
Never assume the Executor will "clean up later" — your plan must be perfect from step 1.

Output only the exhaustive, numbered task list with exact file paths and precise instructions. Ask clarifying questions if the request is ambiguous. Otherwise deliver the full plan in one go.
"""

TOOLS_MAP = {"search_internet": search_internet}


class Plan(BaseModel):
    common_tasks: list[str] = Field(
        description="""
        Atomic, ordered tasks that affect shared configuration or global files and must be done first 
        so that every subsequent task can succeed without breaking the build at any point.
        Examples:
        - Add necessary dependencies to package.json (e.g., zod, react-hook-form, @tanstack/react-query)
        - Add or extend environment variables in .env.example and tsconfig.json paths
        - Extend tailwind.config.ts with new plugins, themes, or content paths
        - Update next.config.js (images, redirects, headers, experimental flags)
        - Add global providers or context in src/app/layout.tsx or src/providers/
        - Create shared types in src/types/
        - Create reusable utilities in src/lib/ or src/utils/
        - Configure middleware.ts, route handlers, or API routes that other tasks depend on
        These tasks are executed exactly once at the beginning and never touch page-specific UI.
        Remember that the project has already been created, bootstrapped with TailwindCSS, ESLint, and TypeScript, and that you are already in the project directory, so do not add project creation to the list of tasks.
        Remember to give the site a proper title for each route.
        """
    )

    backend_tasks: list[str] = Field(
        description="""
        Pure backend / data-layer tasks that do not affect visible UI directly.
        Must use app router conventions (route.ts, server actions, server components).
        Examples:
        - Create src/app/api/auth/[...nextauth]/route.ts with NextAuth.js
        - Create src/app/api/trpc/[trpc]/route.ts and initialize tRPC
        - Create server-only utilities in src/server/
        - Implement database seeding script in src/lib/seed.ts
        - Add rate-limiting middleware or edge functions
        - Create server actions in src/actions/
        These tasks may create or modify files under src/app/api/, src/server/, src/lib/, 
        but never add 'use client' or UI components.
        """
    )

    frontend_tasks: list[str] = Field(
        description="""
        Purely frontend / route-specific UI tasks that implement pages, layouts, and client components.
        Executed only after all common_tasks and backend_tasks are complete.
        Must follow exact file locations:
        - New pages → src/app/[route]/page.tsx (server component by default)
        - Client components → src/components/ or src/app/[route]/components/ with 'use client'
        - Route groups → src/app/(group)/...
        - loading.tsx, error.tsx, layout.tsx inside route segments when needed
        Examples:
        These tasks are allowed to use 'use client', hooks, and Tailwind, but must never 
        modify global config files or add dependencies.
        """
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
                            if relative_path.endswith("/index.txt"):
                                relative_path = relative_path[:-10]
                            elif relative_path == "index.txt":
                                relative_path = "/"
                            else:
                                relative_path = "/" + relative_path

                            if not relative_path.startswith("/"):
                                relative_path = "/" + relative_path

                            messages.append(
                                HumanMessage(content=f"{relative_path}: -\n\n{content}")
                            )
        except Exception as e:
            logging.error(f"Error while reading prompts: {str(e)}")

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
                "OUTPUT EXACTLY AS PER THE SCHEMA\n"
                "Each entry must be a single short sentence describing WHAT to do. "
                "Do NOT include prefixes like 'description:', 'name:'"
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

planner = RunnableLambda(
    lambda input_dict: planner_graph.invoke({"messages": [], "plan": None})["plan"]
).with_types(input_type=dict, output_type=Plan)
