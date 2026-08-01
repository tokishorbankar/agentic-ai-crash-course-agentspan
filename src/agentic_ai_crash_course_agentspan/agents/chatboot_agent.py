from agentspan.agents import Agent, AgentRuntime, ConversationMemory, tool
from dotenv import load_dotenv
import os
from tavily_agent_toolkit import search_and_format
import asyncio
import multiprocessing

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY is not set in the environment variables.")


memory = ConversationMemory(max_messages=3)
session_id = "chatbot_session"


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


chatbot_agent = Agent(
    name="chatbot_agent",
    model="openai/gpt-5.4-mini",
    instructions="You are a helpful agent named Alex. Introduce yourself when greeting users. Use the internet search tool when you need up-to-date information.",
    tools=[internet_search_tool],
    memory=memory
)


def get_resp(query):
    with AgentRuntime() as runtime:
        result = runtime.run(chatbot_agent, query, session_id=session_id)
        return result


def main():
    while True:
        query = input("Ask Query: ")

        if query == "q":
            break

        resp = get_resp(query)
        # resp.print_result()
        ## print messages in resp
        print(f"Agent Response: {resp.output['result']['message']}")
      


if __name__ == "__main__":
    try:
        multiprocessing.set_start_method('fork')
    except RuntimeError:
        # Start method already set
        pass
    main()
