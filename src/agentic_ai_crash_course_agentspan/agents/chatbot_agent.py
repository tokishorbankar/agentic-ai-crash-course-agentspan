from __future__ import annotations

import logging
import multiprocessing
from typing import Any

from agentspan.agents import (
    Agent,
    AgentRuntime,
    ConversationMemory,
    Guardrail,
    OnFail,
    Position,
)

from agentic_ai_crash_course_agentspan.agents.module.response import SupportResponse
from agentic_ai_crash_course_agentspan.agents.tools import (
    calculator_tools,
    internet_search_tool,
)
from agentic_ai_crash_course_agentspan.mcp.server_manager import (
    check_prompt,
    mcp_server_context,
)

logger = logging.getLogger(__name__)

# Constants

# Session ID and Conversation Memory
SESSION_ID = "chatbot_session"
CHATBOT_MEMORY = ConversationMemory(max_messages=2)

# Agent join timeout in seconds
AGENT_JOIN_TIMEOUT_SECONDS = 120

# Exit commands
EXIT_COMMANDS = {"q", "quit", "exit", "/quit", "/q"}

# Agent instructions
AGENT_INSTRUCTIONS = (
    "You are a helpful agent named Veda. Introduce yourself when greeting users. "
    "Use the internet search tool when you need up-to-date information. "
    "Use the calculator-agent MCP tools (add, subtract, multiply, divide) for any calculations."
)


# Agent for chatbot with its instructions, tools, and memory
chatbot_agent = Agent(
    name="chatbot_agent",
    model="openai/gpt-5.4-mini",
    instructions=AGENT_INSTRUCTIONS,
    tools=[internet_search_tool, calculator_tools],
    memory=CHATBOT_MEMORY,
    output_type=SupportResponse,
    guardrails=[Guardrail(check_prompt, position=Position.INPUT, on_fail=OnFail.RAISE)],
)


# Function to format the agent's response for display
def format_agent_response(response: Any) -> str:
    logger.debug(f"Agent response received: {response}")
    
    output = getattr(response, "output", None) or {}

    if isinstance(output, dict):
        if "message" in output:
            return str(output["message"])

        result = output.get("result")
        if isinstance(result, dict) and "message" in result:
            return str(result["message"])
        if result is not None:
            return str(result)

    logger.debug("Falling back to raw agent output: %s", output)
    return str(output)


# Function to log agent events
def _log_agent_event(event: Any) -> None:
    if event.type == "tool_call" and event.args:
        logger.info("Tool call event: %s", event.args)
    elif event.type == "tool_result":
        logger.info("Tool result event: %s", event.result)


# Function to run an interactive prompt through the agent runtime
def run_interactive(prompt: str) -> Any:
    logger.debug("Running interactive prompt through agent runtime")

    # Use the MCP server context to ensure the MCP server is running
    with mcp_server_context():
        with AgentRuntime() as runtime:
            # Start the agent execution and get a handle to the execution
            handle = runtime.start(chatbot_agent, prompt, session_id=SESSION_ID)
            logger.debug("Agent execution started: %s", handle.execution_id)

            # Stream and log events from the agent execution
            for event in handle.stream():
                _log_agent_event(event)

            # Wait for the agent execution to complete and get the result
            result = handle.join(timeout=AGENT_JOIN_TIMEOUT_SECONDS)
            logger.debug("Agent execution completed: %s", handle.execution_id)

            # Return the result of the agent execution
            return result


# Function to check if the prompt is an exit command
def _is_exit_command(prompt: str) -> bool:
    return prompt.lower() in EXIT_COMMANDS


# function to configure logging for the application
def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


# Main function to run the chatbot agent in an interactive loop
def main() -> None:
    _configure_logging()
    logger.info("Starting chatbot_agent interactive loop")

    while True:
        prompt = input("Ask Prompt: ").strip()
        if _is_exit_command(prompt):
            logger.info("Exiting chatbot agent")
            break

        if not prompt:
            print("Please enter a valid prompt.")
            continue

        response = run_interactive(prompt)
        print("Agent Response:", format_agent_response(response))


# Entry point for the script
if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("fork")
    except RuntimeError:
        logger.debug("Process start method already configured; continuing")
    main()
