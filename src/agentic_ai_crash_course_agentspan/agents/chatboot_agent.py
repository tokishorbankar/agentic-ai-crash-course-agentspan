from agentspan.agents import Agent, AgentRuntime, ConversationMemory, tool
from dotenv import load_dotenv
import os
from tavily_agent_toolkit import search_and_format
import multiprocessing as mp
import asyncio

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY or not TAVILY_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY or TAVILY_API_KEY is not set in the environment variables."
    )

MEMORY = ConversationMemory(max_messages=3)
SESSION_ID = "chatbot_session"


@tool(
    name="internet_search_tool",
    description="Search the internet for latest information.",
)
def internet_search_tool(query: str) -> str:
    """
    Search the internet for latest information.
    """

    if query is None or query.strip() == "":
        return "Please provide a valid search query."

    return asyncio.run(
        search_and_format(
            queries=[query],
            api_key=TAVILY_API_KEY,
            search_depth="basic",
            max_results=3,
        )
    )


chatboot_agent = Agent(
    name="chatbot_agent",
    model="openai/gpt-4o-mini",
    instructions="You are a helpful agent named Alex. Use tools for better responses.",
    tools=[internet_search_tool],
    memory=MEMORY,
)


def get_response(query: str):
    with AgentRuntime() as runtime:
        response = runtime.run(chatboot_agent, query, session_id=SESSION_ID)
        return response


def main():

    print("Welcome to Chatbots Agent! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        response = get_response(user_input)
        print(f"Chatbots Agent Response: {response}")


if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    main()
