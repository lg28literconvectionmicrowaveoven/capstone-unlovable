# graphs/commons.py — FINAL, BULLETPROOF VERSION (Dec 2025)
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import tools_condition
from operator import add
from globals import app_state


# This is the OFFICIAL LangGraph state schema for message graphs
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add]  # appends messages automatically
    carry: str


def build_simple_tool_graph(
    system_prompt: str, tool_map: dict[str, BaseTool], name: str = "agent"
):
    """
    Returns a compiled LangGraph agent.
    Invoke ONLY with:
        .invoke({"messages": [HumanMessage(content="your task here")]})
    This is the ONLY pattern that works 100% with LangGraph 0.2+.

    state["carry"] maintains a brief compounding summary of tasks performed.
    """

    def agent(state: AgentState):
        # Ensure system prompt is always first
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + messages
        model_with_tools = app_state.model.bind_tools(list(tool_map.values()))
        response = model_with_tools.invoke(messages)

        # Generate compounding summary of what the agent just did
        current_carry = state.get("carry", "")

        # Build context for summary generation
        latest_action = ""
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_names = [tc["name"] for tc in response.tool_calls]
            latest_action = f"Called tools: {', '.join(tool_names)}"
        elif hasattr(response, "content") and response.content:
            latest_action = "Responded to user"

        # Generate updated summary using LLM
        if latest_action:
            summary_prompt = f"""Previous summary: {current_carry if current_carry else "None"}

Latest action: {latest_action}

Generate a brief, compounding summary (max 2 sentences) of all tasks performed so far. Be concise and cumulative."""

            summary_response = app_state.model.invoke(
                [HumanMessage(content=summary_prompt)]
            )
            new_carry = summary_response.content.strip()
        else:
            new_carry = current_carry

        return {"messages": [response], "carry": new_carry}

    def tools(state: AgentState):
        last_msg = state["messages"][-1]
        if not getattr(last_msg, "tool_calls", None) or not last_msg.tool_calls:
            return {"messages": []}

        tool_messages = []
        for tc in last_msg.tool_calls:
            tool_name = tc["name"]
            tool_args = tc.get("args", {})
            tool_id = tc["id"]
            tool = tool_map.get(tool_name)
            try:
                result = (
                    tool.invoke(tool_args)
                    if tool
                    else f"Error: Tool '{tool_name}' not found"
                )
            except Exception as e:
                result = f"Tool '{tool_name}' crashed: {str(e)}"
            tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_id))

        return {"messages": tool_messages}

    # Build graph — EXACTLY as in LangGraph official docs
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent)
    graph.add_node("tools", tools)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)  # This is safe and correct
    graph.add_edge("tools", "agent")

    return graph.compile()
