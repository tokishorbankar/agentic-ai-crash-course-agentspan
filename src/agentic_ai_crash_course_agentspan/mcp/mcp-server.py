import logging
import sys
from mcp.server import FastMCP

logger = logging.getLogger(__name__)

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
    logger.info(f"Adding {num1} and {num2}")
    """Adds two numbers."""
    return num1 + num2


@mcp.tool(description="Subtracts the second number from the first.")
def subtract(num1: float, num2: float) -> float:
    logger.info(f"Subtracting {num2} from {num1}")
    """Subtracts the second number from the first."""
    return num1 - num2


@mcp.tool(
    description="Multiplies two numbers.",
)
def multiply(num1: float, num2: float) -> float:
    logger.info(f"Multiplying {num1} and {num2}")
    """Multiplies two numbers."""
    return num1 * num2


@mcp.tool(
    description="Divides the first number by the second.",
)
def divide(num1: float, num2: float) -> float:
    logger.info(f"Dividing {num1} by {num2}")
    """Divides the first number by the second."""
    if num2 == 0:
        raise ValueError("Cannot divide by zero.")
    return num1 / num2


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if argv is None:
        argv = sys.argv[1:]

    transport = argv[0] if argv else "streamable-http"
    logger.info("Starting calculator-agent MCP server using transport: %s", transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
