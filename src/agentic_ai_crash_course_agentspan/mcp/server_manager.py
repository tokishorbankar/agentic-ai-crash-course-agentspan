from __future__ import annotations

import logging
import os
import socket
import shutil
import subprocess
import time
from contextlib import contextmanager
from typing import Iterator

from agentspan.agents import GuardrailResult, guardrail

from agentic_ai_crash_course_agentspan.config import load_config

logger = logging.getLogger(__name__)
config = load_config()


# Utility functions to manage the MCP server
def is_mcp_server_running(timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(
            (config.mcp_server_host, config.mcp_server_port), timeout=timeout
        ):
            return True
    except OSError:
        return False


# Start the MCP server as a subprocess
def _find_uv_executable() -> str:
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

    deadline = time.time() + 15.0
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
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        logger.warning("MCP server did not stop cleanly; killing")
        process.kill()
        process.wait(timeout=5)

# Guardrail to check if the prompt contains any offensive or inappropriate content
@guardrail
def check_prompt(prompt: str) -> GuardrailResult:
    """
    Guardrail to check if the prompt contains any offensive or inappropriate content.
    It blocks obvious prompt injections attacks and ensures that the prompt is safe for processing.
    """

    offensive_keywords = ["offensive", "inappropriate", "banned"]
    blocked_keywords = [
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
    ]

    cleaned = not any(
        keyword in prompt.lower() for keyword in offensive_keywords
    ) and not any(keyword in prompt.lower() for keyword in blocked_keywords)

    return GuardrailResult(
        passed=cleaned, message="Please ask a different query, this is blocked."
    )

# Context manager to ensure the MCP server is running during a block of code
@contextmanager
def mcp_server_context() -> Iterator[None]:
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
