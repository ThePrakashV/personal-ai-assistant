from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def _make_model_client() -> OpenAIChatCompletionClient:
    """Points AutoGen at our local Ollama server via its OpenAI-compatible endpoint."""
    return OpenAIChatCompletionClient(
        model=settings.ollama_model,
        base_url=settings.autogen_openai_compat_url,
        api_key="ollama",
        model_info={
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "family": "unknown",
        },
    )


# --- Specialized Agents ---

researcher_agent = AssistantAgent(
    name="Researcher",
    model_client=_make_model_client(),
    system_message=(
        "You are a Research Agent. You explain concepts, facts, science, history, and "
        "provide analysis clearly and concisely. You do NOT write code — if the request "
        "needs code, say so and let the Coder agent handle it. When you have fully "
        "answered the user's question, end your message with TERMINATE."
    ),
)

coder_agent = AssistantAgent(
    name="Coder",
    model_client=_make_model_client(),
    system_message=(
        "You are a Coding Agent. You ONLY write code, debug code, or explain programming "
        "concepts. You do NOT handle general research/science/explanation topics unrelated "
        "to code — defer those to the Researcher agent. When you have fully answered the "
        "user's question, end your message with TERMINATE."
    ),
)

general_agent = AssistantAgent(
    name="General",
    model_client=_make_model_client(),
    system_message=(
        "You are a General Assistant and coordinator. You handle simple everyday "
        "greetings and small talk directly. For anything requiring deep research, "
        "science, or explanation, defer to the Researcher agent. For anything requiring "
        "code, defer to the Coder agent. When the conversation has fully answered the "
        "user's question, end your message with TERMINATE."
    ),
)

ALL_AGENTS = [general_agent, researcher_agent, coder_agent]

# --- Selector instructions (explicit routing guidance) ---

_SELECTOR_PROMPT = """You are selecting the next agent to speak in a conversation.

Available agents:
- General: handles simple greetings and small talk only (e.g. "hi", "how are you").
- Researcher: handles science, history, concepts, facts, and any explanation/analysis
  question that does NOT involve writing code (e.g. "explain photosynthesis", "who is Einstein").
- Coder: handles ONLY requests to write, debug, or explain code/programming
  (e.g. "write a Python function", "fix this bug").

Conversation so far:
{history}

Based on the user's most recent message, select the SINGLE most appropriate agent from
{participants} to respond next. Respond with ONLY the agent name, nothing else.
"""

# --- Team (Group Chat) ---

_termination = MaxMessageTermination(settings.autogen_max_turns) | TextMentionTermination("TERMINATE")

team = SelectorGroupChat(
    participants=ALL_AGENTS,
    model_client=_make_model_client(),
    termination_condition=_termination,
    selector_prompt=_SELECTOR_PROMPT,
)


async def run_multiagent(user_message: str) -> str:
    """Run the multi-agent team on a single user message and return the final reply text."""
    logger.info(f"Running multi-agent team for: {user_message[:50]}...")

    result = await team.run(task=user_message)

    for msg in result.messages:
        source = getattr(msg, "source", "unknown")
        content_preview = (getattr(msg, "content", "") or "")[:60]
        logger.info(f"  [{source}]: {content_preview}...")

    final_text = ""
    for msg in reversed(result.messages):
        content = getattr(msg, "content", "") or ""
        cleaned = content.replace("TERMINATE", "").strip()
        if cleaned:
            final_text = cleaned
            break

    logger.info("Multi-agent run completed")
    return final_text or "No response generated."