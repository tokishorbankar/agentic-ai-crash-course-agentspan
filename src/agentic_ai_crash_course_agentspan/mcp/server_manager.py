from __future__ import annotations

import logging
import socket
import shutil
import subprocess
import time
from contextlib import contextmanager
from typing import Generator

from agentspan.agents import GuardrailResult, guardrail

from agentic_ai_crash_course_agentspan.config import load_config

# Logger setup and configuration loading
logger = logging.getLogger(__name__)
config = load_config()

# Constants for MCP server management
MCP_SERVER_START_TIMEOUT = 15.0
MCP_SERVER_POLL_INTERVAL = 0.2
MCP_SERVER_SHUTDOWN_TIMEOUT = 5.0

# Constants for prompt safety checks
OFFENSIVE_KEYWORDS = frozenset({"offensive", "inappropriate", "banned"})

# Blocked keywords that should not be allowed in prompts
BLOCKED_KEYWORDS = frozenset(
    {
        "hack",
        "exploit",
        "malware",
        "phishing",
        "illegal",
        "unauthorized",
        "bypass",
        "crack",
        "piracy",
        "forget everything",
        "ignore",
        "ignore previous",
        "system prompt",
        "jailbreak",
    }
)


# Check if the MCP server is running by attempting to connect to its host and port
def is_mcp_server_running(timeout: float = 0.5) -> bool:
    logger.debug(
        "Checking MCP server availability at %s:%d",
        config.mcp_server_host,
        config.mcp_server_port,
    )
    try:
        with socket.create_connection(
            (config.mcp_server_host, config.mcp_server_port), timeout=timeout
        ):
            return True
    except OSError:
        return False


# Find the uv executable
def _find_uv_executable() -> str:
    logger.debug("Looking for uv executable in PATH")
    uv_executable = shutil.which("uv")
    if uv_executable is None:
        raise RuntimeError(
            "Cannot start MCP server because the 'uv' command was not found. "
            "Install uv or use a Python environment where it is available."
        )
    return uv_executable


# Start the MCP server as a subprocess
def start_mcp_server() -> subprocess.Popen:
    server_script = config.mcp_server_script
    logger.info("Starting MCP server: %s", server_script)

    process = subprocess.Popen(
        [_find_uv_executable(), "run", str(server_script), "streamable-http"],
        cwd=str(config.project_root),
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    logger.debug("MCP server process launched with PID %s", process.pid)

    deadline = time.time() + MCP_SERVER_START_TIMEOUT
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError("MCP server process exited unexpectedly.")
        if is_mcp_server_running():
            logger.info(
                "MCP server started successfully on %s:%d",
                config.mcp_server_host,
                config.mcp_server_port,
            )
            return process
        time.sleep(0.2)

    process.terminate()
    raise RuntimeError("Timed out waiting for MCP server to start.")


# Stop the MCP server as a subprocess
def stop_mcp_server(process: subprocess.Popen) -> None:
    if process is None or process.poll() is not None:
        return

    logger.info("Stopping MCP server")
    process.terminate()
    try:
        process.wait(timeout=MCP_SERVER_SHUTDOWN_TIMEOUT)
        logger.debug("MCP server process terminated cleanly")
    except subprocess.TimeoutExpired:
        logger.warning("MCP server did not stop cleanly; killing")
        process.kill()
        process.wait(timeout=5)


# Check if the prompt is safe by looking for offensive or blocked keywords
def _is_prompt_safe(prompt: str) -> bool:
    normalized_prompt = prompt.lower()
    return not any(
        keyword in normalized_prompt for keyword in OFFENSIVE_KEYWORDS
    ) and not any(keyword in normalized_prompt for keyword in BLOCKED_KEYWORDS)


# Guardrail to block unsafe or malicious prompts before they reach the agent
@guardrail
def check_prompt(prompt: str) -> GuardrailResult:
    """Block unsafe or malicious prompts before they reach the agent."""

    return GuardrailResult(
        passed=_is_prompt_safe(prompt),
        message="Please ask a different query, this is blocked.",
    )


# Context manager to ensure the MCP server is running during agent execution
@contextmanager
def mcp_server_context() -> Generator[None, None, None]:
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
