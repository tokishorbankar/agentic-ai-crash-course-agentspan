# Agentic AI Crash Course

## Requirements

- Python 3.13 or newer
- `uv` for dependency management
- OpenAI API key
- Tavily API key for `chatbot_agent.py` internet search

## Setup

- Install dependencies:

```bash
uv sync
```

- Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- Run any example with `uv run`.

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
