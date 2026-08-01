from agentspan.agents import Agent, AgentRuntime, ConversationMemory, tool, mcp_tool
from dotenv import load_dotenv
import logging
import os
from tavily_agent_toolkit import search_and_format
import asyncio
import multiprocessing
import shutil
import socket
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

load_dotenv()

# Environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

# Validate required environment variables
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY is not set in the environment variables.")

# Initialize conversation memory and session ID for the chatbot agent
memory = ConversationMemory(max_messages=3)
session_id = "chatbot_session"

# MCP server configuration
CALCULATOR_MCP_URL = os.getenv("CALCULATOR_MCP_URL", "http://localhost:8000/mcp")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MCP_SERVER_SCRIPT = (
    PROJECT_ROOT / "src" / "agentic_ai_crash_course_agentspan" / "mcp" / "mcp-server.py"
)
MCP_SERVER_HOST = "localhost"
MCP_SERVER_PORT = 8000

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# Utility functions to manage the MCP server
def is_mcp_server_running(timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(
            (MCP_SERVER_HOST, MCP_SERVER_PORT), timeout=timeout
        ):
            return True
    except OSError:
        return False


# Start the MCP server as a subprocess
def start_mcp_server() -> subprocess.Popen:
    uv_executable = shutil.which("uv")
    if uv_executable is None:
        raise RuntimeError(
            "Cannot start MCP server because the 'uv' command was not found."
        )

    logger.info("Starting MCP server: %s", MCP_SERVER_SCRIPT)
    process = subprocess.Popen(
        [uv_executable, "run", str(MCP_SERVER_SCRIPT), "streamable-http"],
        cwd=str(PROJECT_ROOT),
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    deadline = time.time() + 15.0
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError("MCP server process exited unexpectedly.")
        if is_mcp_server_running():
            logger.info(
                "MCP server started successfully on %s:%d",
                MCP_SERVER_HOST,
                MCP_SERVER_PORT,
            )
            return process
        time.sleep(0.2)

    process.terminate()
    raise RuntimeError("Timed out waiting for MCP server to start.")


# Stop the MCP server as a subprocess
def stop_mcp_server(process: subprocess.Popen) -> None:
    if process is None:
        return
    if process.poll() is None:
        logger.info("Stopping MCP server")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("MCP server did not stop cleanly; killing")
            process.kill()
            process.wait(timeout=5)


# Context manager to ensure the MCP server is running during the execution of a block of code
@contextmanager
def mcp_server_context():
    started = False
    process = None
    if not is_mcp_server_running():
        process = start_mcp_server()
        started = True
    try:
        yield
    finally:
        if started and process is not None:
            stop_mcp_server(process)


# Define the internet search tool using the Tavily API
@tool
def internet_search_tool(query: str) -> str:
    """
    Search the internet for latest information.
    """

    return asyncio.run(
        search_and_format(
            queries=[query],
            api_key=tavily_api_key,
            search_depth="basic",
            max_results=0,
        )
    )


# Define the calculator tools using the MCP server
calculator_tools = mcp_tool(
    server_url=CALCULATOR_MCP_URL,
    name="calculator-agent",
    description="Calculator tools from the calculator-agent MCP server",
    tool_names=["add", "subtract", "multiply", "divide"],
)


# Define the chatbot agent with its instructions, tools, and memory
chatbot_agent = Agent(
    name="chatbot_agent",
    model="openai/gpt-5.4-mini",
    instructions="""
    You are a helpful agent named Alex. Introduce yourself when greeting users. 
    Use the internet search tool when you need up-to-date information.
    Use the calculator-agent MCP tools (add, subtract, multiply, divide) for any calculations.
    """,
    tools=[internet_search_tool, calculator_tools],
    memory=memory,
)


# Function to get a response from the chatbot agent
def get_resp(query):
    with mcp_server_context():
        with AgentRuntime() as runtime:
            result = runtime.run(chatbot_agent, query, session_id=session_id)
            return result


# Main function to interact with the chatbot agent
def main():
    while True:
        query = input("Ask Query: ")

        if query == "q":
            break

        resp = get_resp(query)
        # Prefer explicit result/message values when available.
        output = getattr(resp, "output", {}) or {}
        result = output.get("result") if isinstance(output, dict) else None

        if isinstance(result, dict) and "message" in result:
            print(f"Agent Response: {result['message']}")
        elif isinstance(output, dict) and "message" in output:
            print(f"Agent Response: {output['message']}")
        elif result is not None:
            print(f"Agent Response: {result}")
        else:
            print("Agent Response:")
            try:
                resp.print_result()
            except Exception:
                print(output)


# Entry point of the script
if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("fork")
    except RuntimeError:
        pass
    main()
