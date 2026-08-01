# Agentic AI Crash Course Setup Guide

This document describes how to install dependencies, configure environment variables, run the calculator MCP server, start the chatbot agent, and stop running services.

## Prerequisites

- Python 3.13 or newer
- `uv` installed and available in your PATH
- OpenAI API key
- Tavily API key

## Install dependencies

From the project root:

```bash
uv sync
```

This installs the project dependencies declared in `pyproject.toml`.

## Environment configuration

Create a `.env` file in the project root with the following values:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
CALCULATOR_MCP_URL=http://localhost:8000/mcp
```

- `OPENAI_API_KEY` is required for the agent model.
- `TAVILY_API_KEY` is required for the internet search tool.
- `CALCULATOR_MCP_URL` is optional; it defaults to `http://localhost:8000/mcp`.

## Calculator MCP server

The calculator MCP server is defined in:

- `src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py`

It exposes the following tools:

- `add(num1: float, num2: float) -> float`
- `subtract(num1: float, num2: float) -> float`
- `multiply(num1: float, num2: float) -> float`
- `divide(num1: float, num2: float) -> float`

### Start the MCP server manually

From the project root:

```bash
uv run src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py streamable-http
```

### Stop the MCP server

If the server is running on port `8000`, stop it with:

```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No process found on port 8000"
```

## Chatbot agent

The chatbot agent lives in:

- `src/agentic_ai_crash_course_agentspan/agents/chatbot_agent.py`

It uses:

- `agentic_ai_crash_course_agentspan.agents.tools.internet_search_tool`
- `agentic_ai_crash_course_agentspan.agents.tools.calculator_tools`
- `agentic_ai_crash_course_agentspan.mcp.server_manager.mcp_server_context`

### Run the chatbot agent

From the project root:

```bash
uv run src/agentic_ai_crash_course_agentspan/agents/chatbot_agent.py
```

This script automatically starts the MCP server if it is not already running, then runs the interactive chatbot loop.

### Use the chatbot

Enter any query at the prompt. To exit, type:

```bash
q
quit
exit
/quit
/q
```

## Project files

- `pyproject.toml` - dependency and package metadata
- `README.md` - high-level project overview
- `SETUP.md` - installation and run instructions
- `src/agentic_ai_crash_course_agentspan/config.py` - centralized configuration loader
- `src/agentic_ai_crash_course_agentspan/agents/tools.py` - tool definitions and MCP tool integration
- `src/agentic_ai_crash_course_agentspan/mcp/server_manager.py` - MCP server lifecycle manager
- `src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py` - calculator MCP server
- `src/agentic_ai_crash_course_agentspan/agents/chatbot_agent.py` - chatbot entry point

## Troubleshooting

- If `uv sync` fails, confirm `uv` is installed and active in the current shell.
- If the server fails to start, ensure port `8000` is available or set `CALCULATOR_MCP_URL` to a different port.
- If environment variables are missing, confirm `.env` exists in the project root and contains the required values.
