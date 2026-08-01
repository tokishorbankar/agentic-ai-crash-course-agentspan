# Agentic AI Crash Course

A small Python crash-course repository for experimenting with OpenAI model calls and AgentSpan-based AI agents. The examples progress from a direct OpenAI chat loop to tool-using agents with memory, internet search, guardrails, structured output, and human approval.

## What Is Included

| File | Purpose |
| --- | --- |
| `main.py` | Minimal terminal chatbot using the OpenAI Responses API directly. |
| `chatbot_agent.py` | AgentSpan chatbot named `Alex` with conversation memory, a required greeting tool, and Tavily-powered internet search. |
| `customer_support.py` | Customer support agent with mock order lookup, refund approval, input guardrails, and structured Pydantic output. |
| `pyproject.toml` | Project metadata and Python dependencies. |
| `uv.lock` | Locked dependency versions for reproducible installs with `uv`. |

## Requirements

- Python 3.11 or newer
- `uv` for dependency management
- OpenAI API key
- Tavily API key for `chatbot_agent.py` internet search

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

3. Run any example with `uv run`.

## Usage

### Basic OpenAI Chat

```bash
uv run python main.py
```

Type a prompt at `Ask Query:`. Enter `q` to exit.

### Agent Chatbot With Web Search

```bash
uv run python chatbot_agent.py
```

This example uses AgentSpan with:

- Conversation memory
- A custom `say_hello` tool
- A Tavily internet search tool
- The `openai/gpt-5.4` model setting

Enter `q` to exit.

### Customer Support Agent

```bash
uv run python customer_support.py
```

This example demonstrates:

- Input guardrails that block common prompt-injection phrases
- A mock order database lookup tool
- A refund tool that requires human approval
- Structured output using a `SupportResponse` Pydantic model

Try prompts such as:

```text
What is the status of order 1?
Refund order 2 please.
```

Enter `q` to exit.

## Dependencies

The main dependencies are:

- `openai` for direct model access
- `agentspan` for agents, tools, memory, guardrails, runtime, and approvals
- `tavily-agent-toolkit` for internet search
- `python-dotenv` for loading local environment variables

## Notes

- Keep `.env` out of version control because it contains API keys.
- The customer support database is mocked in code and is only for learning purposes.
- The scripts are interactive examples, not production services.