"""
Add LangChain tools to a FastMCP server
Use to_fastmcp to convert LangChain tools to FastMCP, and then add them to the FastMCP server via the initializer:
"""

from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP


@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


fastmcp_tool = to_fastmcp(add)

mcp = FastMCP("Math", tools=[fastmcp_tool])
mcp.run(transport="stdio")