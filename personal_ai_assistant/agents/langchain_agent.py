import ast
import operator
from datetime import datetime

from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from personal_ai_assistant.utils.config import settings
from personal_ai_assistant.utils.logger import get_logger

logger = get_logger(__name__)


# --- Tools ---

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _safe_eval(node):
    """Safely evaluate a basic arithmetic expression (no eval() — avoids code execution risk)."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _SAFE_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _SAFE_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression (e.g. '25 * 48', '(10 + 5) / 3'). Use this for any math question."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        logger.info(f"Calculator: {expression} = {result}")
        return str(result)
    except Exception as e:
        logger.error(f"Calculator failed for '{expression}': {e}")
        return f"Error: could not evaluate '{expression}'"


@tool
def get_current_datetime() -> str:
    """Return the current date and time. Use this whenever the user asks what the date or time is."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"get_current_datetime: {now}")
    return now


TOOLS = [calculator, get_current_datetime]

# --- Tool-bound model ---

_base_model = ChatOllama(base_url=settings.ollama_base_url, model=settings.ollama_model)
model_with_tools = _base_model.bind_tools(TOOLS)