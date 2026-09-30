from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from personal_ai_assistant.agents.langchain_agent import model_with_tools, TOOLS
from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def call_model(state: AgentState) -> dict:
    """Agent node — asks the LLM to respond, possibly requesting a tool call."""
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Decision node — if the last message requested a tool call, go run it; otherwise finish."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


# --- Build the graph ---

_workflow = StateGraph(AgentState)
_workflow.add_node("agent", call_model)
_workflow.add_node("tools", ToolNode(TOOLS))

_workflow.set_entry_point("agent")
_workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
_workflow.add_edge("tools", "agent")  # after a tool runs, go back to the agent for the final answer

agent_graph = _workflow.compile()


def run_agent(user_message: str) -> str:
    """Run the agent workflow for a single user message and return the final text reply."""
    logger.info(f"Running agent for: {user_message[:50]}...")

    result = agent_graph.invoke(
        {"messages": [HumanMessage(content=user_message)]},
        config={"recursion_limit": settings.agent_max_tool_loops * 2 + 2},
    )

    final_message = result["messages"][-1]
    logger.info("Agent run completed")
    return final_message.content