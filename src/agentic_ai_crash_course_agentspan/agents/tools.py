from __future__ import annotations

import asyncio
import logging
from agentspan.agents import mcp_tool, tool
from tavily_agent_toolkit import search_and_format

from agentic_ai_crash_course_agentspan.config import load_config

logger = logging.getLogger(__name__)
config = load_config()


# Tool for internet search using Tavily API
@tool
def internet_search_tool(query: str) -> str:
    """Search the internet for up-to-date information.

    The search tool is synchronous because the agent runtime expects normal
    tool functions. Async execution is managed by asyncio.run().
    """

    return asyncio.run(
        search_and_format(
            queries=[query],
            api_key=config.tavily_api_key,
            search_depth="basic",
            max_results=0,
        )
    )


# Calculator tools from the calculator-agent MCP server
calculator_tools = mcp_tool(
    server_url=config.calculator_mcp_url,
    name="calculator-agent",
    description="Calculator tools from the calculator-agent MCP server",
    tool_names=["add", "subtract", "multiply", "divide"],
)
