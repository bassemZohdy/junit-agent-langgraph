from typing import TypedDict
from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def search(query: str) -> str:
    """Search for information (placeholder)."""
    return f"Search results for: {query}"


tools = [calculator, search]
