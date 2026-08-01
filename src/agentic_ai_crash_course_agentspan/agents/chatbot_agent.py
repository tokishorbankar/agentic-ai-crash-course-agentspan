from __future__ import annotations

import logging
import multiprocessing
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
from agentic_ai_crash_course_agentspan.config import load_config
from agentic_ai_crash_course_agentspan.mcp.server_manager import (
    check_prompt,
    mcp_server_context,
)

config = load_config()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# Constants
SESSION_ID = "chatbot_session"
CHATBOT_MEMORY = ConversationMemory(max_messages=2)

# Define the chatbot agent with its tools and instructions
chatbot_agent = Agent(
    name="chatbot_agent",
    model="openai/gpt-5.4-mini",
    instructions=(
        "You are a helpful agent named Alex. Introduce yourself when greeting users. "
        "Use the internet search tool when you need up-to-date information. "
        "Use the calculator-agent MCP tools (add, subtract, multiply, divide) for any calculations."
    ),
    tools=[internet_search_tool, calculator_tools],
    memory=CHATBOT_MEMORY,
    output_type=SupportResponse,
    guardrails=[Guardrail(check_prompt, position=Position.INPUT, on_fail=OnFail.RAISE)],
)


# Function to format the agent's response for display
def format_agent_response(response) -> str:
    output = getattr(response, "output", {}) or {}
    result = output.get("result") if isinstance(output, dict) else None

    if isinstance(result, dict) and "message" in result:
        return result["message"]
    if isinstance(output, dict) and "message" in output:
        return output["message"]
    if result is not None:
        return str(result)

    logger.debug("Falling back to raw agent output: %s", output)
    return str(output)


# Function to get a response from the chatbot agent
def run_interactive(prompt: str):
    with mcp_server_context():
        with AgentRuntime() as runtime:
            handle = runtime.start(chatbot_agent, prompt, session_id=SESSION_ID)
            for event in handle.stream():
                if event.type == "tool_call" and event.args:
                    logger.info("Tool call event: %s", event.args)
                elif event.type == "tool_result":
                    logger.info("Tool result event: %s", event.result)

            return handle.join(timeout=120)


# Main function to interact with the chatbot agent
def main() -> None:
    logger.info("Starting chatbot_agent interactive loop")

    while True:
        prompt = input("Ask Prompt: ").strip()
        if prompt.lower() in {"q", "quit", "exit", "/quit", "/q"}:
            logger.info("Exiting chatbot agent")
            break

        if not prompt:
            print("Please enter a valid prompt.")
            continue

        response = run_interactive(prompt)
        print("Agent Response:", format_agent_response(response))


# Entry point for running the chatbot agent
if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("fork")
    except RuntimeError:
        logger.debug("Process start method already configured")
    main()
