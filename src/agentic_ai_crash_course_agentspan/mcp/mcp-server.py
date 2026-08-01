from mcp.server import FastMCP

mcp = FastMCP(
    "calculator-agent",
    instructions="Calculator tools from the calculator-agent MCP server",
    host="localhost",
    port=8000,
    stateless_http=True,
)


@mcp.tool(
    description="Adds two numbers.",
)
def add(num1: float, num2: float) -> float:
    """Adds two numbers."""
    return num1 + num2


@mcp.tool(description="Subtracts the second number from the first.")
def subtract(num1: float, num2: float) -> float:
    """Subtracts the second number from the first."""
    return num1 - num2


@mcp.tool(
    description="Multiplies two numbers.",
)
def multiply(num1: float, num2: float) -> float:
    """Multiplies two numbers."""
    return num1 * num2


@mcp.tool(
    description="Divides the first number by the second.",
)
def divide(num1: float, num2: float) -> float:
    """Divides the first number by the second."""
    if num2 == 0:
        raise ValueError("Cannot divide by zero.")
    return num1 / num2


if __name__ == "__main__":
    import sys

    transport = sys.argv[1] if len(sys.argv) > 1 else "streamable-http"
    mcp.run(transport=transport)
