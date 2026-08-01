# MCP (Model Context Protocol) Usage Guide

This guide covers how to run and test the MCP calculator server and client in this project.

## Table of Contents

- [What is MCP?](#what-is-mcp)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the MCP Server](#running-the-mcp-server)
- [Running the MCP Client](#running-the-mcp-client)
- [Using MCP Inspector](#using-mcp-inspector)
- [Available Tools](#available-tools)
- [Troubleshooting](#troubleshooting)

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol for communication between AI applications and external tools/services. It allows:

- Tool discovery and execution
- Resource management
- Prompt templates
- Standardized communication between clients and servers

## Project Structure

```
src/agentic_ai_crash_course_agentspan/mcp/
├── mcp-server.py    # MCP server with calculator tools
└── mcp-client.py    # MCP client that connects to the server
```

## Prerequisites

- Python 3.13 or higher
- `uv` package manager installed
- MCP library with CLI tools

## Installation

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Verify MCP installation:**

   ```bash
   uv run python -c "import mcp; print('MCP installed successfully')"
   ```

   **Note:** Always use `uv run` to execute Python commands in this project to ensure the correct virtual environment is used.

## Running the MCP Server

The MCP server exposes calculator tools via stdio transport.

### Method 1: Direct Execution

```bash
uv run src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py
```

The server will start and wait for connections on stdin/stdout.

### Method 2: Using Python Module

```bash
uv run python src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py
```

**Note:** The server runs in the foreground and communicates via stdio. You won't see any output until a client connects.

## Running the MCP Client

The client connects to the server, lists available tools, and executes sample operations.

### Run the Client

```bash
uv run src/agentic_ai_crash_course_agentspan/mcp/mcp-client.py
```

### Expected Output

```
Available tools: ['add', 'subtract', 'multiply', 'divide']

Addition Result: [TextContent(type='text', text='8.0')]
Multiplication Result: [TextContent(type='text', text='28.0')]
```

### How It Works

1. Client spawns the server as a subprocess using `uv run`
2. Communicates with the server via stdio
3. Initializes the session
4. Lists available tools
5. Calls the `add` tool with arguments `{num1: 5, num2: 3}`
6. Calls the `multiply` tool with arguments `{num1: 4, num2: 7}`
7. Displays results

## Using MCP Inspector

The **MCP Inspector** is an interactive web-based debugging tool for testing MCP servers without writing client code.

### Installation

The inspector is included with `mcp[cli]` which is already in your dependencies.

### Start the Inspector

```bash
npx @modelcontextprotocol/inspector uv run src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py
```

Or using the Python CLI:

```bash
mcp dev src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py
```

### Using the Inspector Web Interface

1. **Open the web interface:**
   - The inspector typically starts at `http://localhost:5173`
   - Your browser should open automatically

2. **Explore available tools:**
   - View all registered tools: `add`, `subtract`, `multiply`, `divide`
   - See tool descriptions and parameter schemas
   - Review input/output types

3. **Test tools interactively:**
   - Select a tool from the list
   - Fill in parameter values
   - Click "Execute" to call the tool
   - View the JSON request/response

4. **Debug tool behavior:**
   - Inspect request payloads
   - Validate response formats
   - Test edge cases (e.g., division by zero)
   - View error messages

### Inspector Features

- **Tool Discovery:** Lists all available tools with descriptions
- **Interactive Testing:** Call tools with custom parameters
- **Request/Response Inspection:** View full JSON protocol messages
- **Schema Validation:** Verify tool parameter schemas
- **Real-time Debugging:** Test tools without writing client code

### Example Inspector Session

1. Start inspector: `npx @modelcontextprotocol/inspector uv run src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py`
2. Open browser at `http://localhost:5173`
3. Select "add" tool
4. Enter parameters: `num1: 10, num2: 5`
5. Click "Execute"
6. View result: `15.0`

## Available Tools

### 1. `add`

**Description:** Adds two numbers.

**Parameters:**

- `num1` (float): First number
- `num2` (float): Second number

**Returns:** float - Sum of num1 and num2

**Example:**

```python
result = await session.call_tool("add", {"num1": 5, "num2": 3})
# Returns: 8.0
```

### 2. `subtract`

**Description:** Subtracts the second number from the first.

**Parameters:**

- `num1` (float): First number
- `num2` (float): Second number to subtract

**Returns:** float - Result of num1 - num2

**Example:**

```python
result = await session.call_tool("subtract", {"num1": 10, "num2": 3})
# Returns: 7.0
```

### 3. `multiply`

**Description:** Multiplies two numbers.

**Parameters:**

- `num1` (float): First number
- `num2` (float): Second number

**Returns:** float - Product of num1 and num2

**Example:**

```python
result = await session.call_tool("multiply", {"num1": 4, "num2": 7})
# Returns: 28.0
```

### 4. `divide`

**Description:** Divides the first number by the second.

**Parameters:**

- `num1` (float): Numerator
- `num2` (float): Denominator

**Returns:** float - Result of num1 / num2

**Raises:** ValueError if num2 is 0

**Example:**

```python
result = await session.call_tool("divide", {"num1": 20, "num2": 4})
# Returns: 5.0
```

## Troubleshooting

### Issue: "Module 'mcp' not found"

**Solution:**

```bash
uv sync
# or
uv pip install "mcp[cli]>=1.29.0"
```

### Issue: Client hangs or doesn't connect

**Causes:**

- Server path is incorrect in client code
- Server failed to start
- Stdio communication issue

**Solution:**

1. Test server directly: `uv run src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py`
2. Check server path in [mcp-client.py](src/agentic_ai_crash_course_agentspan/mcp/mcp-client.py) line 8:

   ```python
   args=["run", "src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py"],
   ```

3. Ensure you're running from the project root directory

### Issue: Division by zero error

**Expected behavior:** The divide tool raises a ValueError when num2 is 0.

**Example:**

```python
try:
    result = await session.call_tool("divide", {"num1": 10, "num2": 0})
except Exception as e:
    print(f"Error: {e}")  # ValueError: Cannot divide by zero.
```

### Issue: Inspector won't start

**Solution:**

1. Check if port 5173 is available:

   ```bash
   lsof -i :5173
   ```

2. Install npx if missing:

   ```bash
   npm install -g npx
   ```

3. Try alternative command:

   ```bash
   mcp dev src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py
   ```

4. Start the MCP server with streamable HTTP transport:

   ```bash
   uv run src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py streamable-http
   ```

> Kill process

```
lsof -ti:<PORT> | xargs kill -9 2>/dev/null || echo "No process found on port <PORT>"
```

### Issue: Wrong working directory

The client expects to be run from the project root. If you get path errors:

```bash
cd /Users/kishorbankar/Documents/Practies/ai-courses-projects/ai-agentic-courses-projects/agentic-ai-crash-course-agentspan
uv run src/agentic_ai_crash_course_agentspan/mcp/mcp-client.py
```

## Advanced Usage

### Creating Custom Tools

Add new tools to [mcp-server.py](src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py):

```python
@mcp.tool(description="Calculates the power of a number")
def power(base: float, exponent: float) -> float:
    """Raises base to the power of exponent."""
    return base ** exponent
```

### Using the Client Programmatically

```python
import asyncio
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

async def calculate(operation: str, num1: float, num2: float):
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(operation, {"num1": num1, "num2": num2})
            return result.content

# Usage
result = asyncio.run(calculate("multiply", 6, 7))
print(result)  # 42.0
```

### Integrating with AI Agents

This MCP server can be integrated with AI agents (like those in the main project) to provide calculation capabilities:

```python
from agentspan import Agent
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect AI agent to MCP calculator tools
# (Implementation depends on your agent framework)
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk/tree/main/src/mcp/server)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)

## Next Steps

1. **Test all tools** using the MCP Inspector
2. **Add more calculator functions** (square root, modulo, etc.)
3. **Integrate with AI agents** in the main project
4. **Explore MCP resources** for serving files and data
5. **Add prompt templates** for guided interactions
6. **Implement error handling** for edge cases
7. **Add logging** for debugging and monitoring

## Contributing

When adding new tools:

1. Use clear, descriptive names
2. Add comprehensive docstrings
3. Specify parameter types
4. Handle edge cases and errors
5. Test with both client and inspector
6. Update this documentation
