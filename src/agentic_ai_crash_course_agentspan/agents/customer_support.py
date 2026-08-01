from dotenv import load_dotenv
import multiprocessing
from agentspan.agents import (
    Agent,
    AgentRuntime,
    ConversationMemory,
    GuardrailResult,
    Guardrail,
    Position,
    OnFail,
    guardrail,
    tool,
    start,
    EventType,
)

from agentic_ai_crash_course_agentspan.agents.module.response import SupportResponse

MEMORY = ConversationMemory(max_messages=2)
SESSION_ID = "customer_support_session"


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


@tool
def database_tool(order_id: str):
    """lookup and find order and details in database by ID"""
    MOCK_DB = {
        "orders": {
            "1": {"status": "delivered", "total": 10.99},
            "2": {"status": "delivered", "total": 22},
            "3": {"status": "refunded", "total": 19},
        },
    }
    return MOCK_DB["orders"].get(order_id, {"error": "order not found"})


@tool(approval_required=True)
def process_refund(amount, order_id):
    """Request a refund when called"""
    return f"Refunded {amount} for order {order_id}"


customer_support_agent = Agent(
    name="customer_support",
    model="openai/gpt-5.4-mini",
    instructions="You are a customer support agent, your main task is to provide support. Use tools when necessary, especially for refunds and order statuses",
    tools=[database_tool, process_refund],
    memory=MEMORY,
    output_type=SupportResponse,
    guardrails=[Guardrail(check_prompt, position=Position.INPUT, on_fail=OnFail.RAISE)],
)


def run_interactive(prompt: str) -> None:
    with AgentRuntime() as runtime:
        # check when agent goes to waiting state, and when it does, ask a human for approval
        handle = start(
            customer_support_agent, prompt, runtime=runtime, session_id=SESSION_ID
        )

        stream = handle.stream()

        for event in stream:
            if event.type == EventType.TOOL_CALL and event.args:
                order_id = event.args.get("order_id") or order_id

            elif event.type == EventType.TOOL_RESULT and isinstance(event.result, dict):
                amount = event.result.get("total") or amount

            elif event.type == EventType.WAITING:
                print(f"\nApproval required: refund ${amount:.2f} for order {order_id}")

                decision = input("Approve? (y/n): ").lower().strip()

                if decision == "y":
                    handle.approve()
                else:
                    handle.reject("user rejected")

        result = stream.get_result()
        output = result.output.get("result")
        print(f"\n{output}\n")

        result.print_result()


if __name__ == "__main__":
    try:
        multiprocessing.set_start_method("fork")
    except RuntimeError:
        # Start method already set
        pass

    while True:
        prompt = input("Ask Query: ")

        if prompt == "q":
            break

        if not prompt.strip():
            print("Please enter a valid query.")
            continue

        if len(prompt) > 50:
            print("Query is too long. Please limit to 50 characters.")
            continue

        run_interactive(prompt)
