from langchain.messages import AnyMessage, ToolMessage
from typing import Callable, Literal
from langchain_core.tools import BaseTool
from globals import app_state


def get_tool_llm_node(tool_map: dict[str, BaseTool]):
    def tool_llm(state: list[AnyMessage]) -> list[AnyMessage]:
        """Node that calls the LLM with tool binding"""
        return state + [
            app_state.model.bind_tools(list(tool_map.values())).invoke(state)
        ]

    return tool_llm


def get_tool_executor(
    tool_map: dict[str, BaseTool],
) -> Callable[[list[AnyMessage]], list[AnyMessage]]:
    def tool_executor(state: list[AnyMessage]) -> list[AnyMessage]:
        """Node that executes tools based on the last AI message"""
        last_message = state[-1]
        tool_messages: list[ToolMessage] = []
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name: str = tool_call["name"]
                tool_args: dict = tool_call["args"]
                tool_id: str = tool_call["id"]
                if tool_name in tool_map:
                    result = tool_map[tool_name].invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"
                tool_messages.append(
                    ToolMessage(content=str(result), tool_call_id=tool_id)
                )
        return state + tool_messages

    return tool_executor


def tools_edge(state: list[AnyMessage]) -> Literal["tools", "continue"]:
    """Conditional edge that determines if we should call tools or structure output"""
    last_message = state[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "continue"
