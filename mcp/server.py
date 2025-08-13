from mcp.server.fastmcp import FastMCP

# Basic MCP server that can add, subtract, and multiply two numbers(no third party API calls/DB Calls)
mcp = FastMCP("Math-Server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers together
    Args:
        a (int): The first number
        b (int): The second number

    Returns:
        int: The sum of the two numbers
    """
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    return a - b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers together
    Args:
        a (int): The first number
        b (int): The second number

    Returns:
        int: The product of the two numbers
    """
    return a * b


if __name__ == "__main__":
    # Use the standard input/output (stdin/stdout) to receive and respond to tool function calls
    mcp.run(transport="stdio")
