import asyncio
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client


async def main() -> None:
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "src/agentic_ai_crash_course_agentspan/mcp/mcp-server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # Call the add tool
            add_result = await session.call_tool("add", {"num1": 5, "num2": 3})
            print(f"\nAddition Result: {add_result.content}")
            
            # Call the multiply tool
            multiply_result = await session.call_tool("multiply", {"num1": 4, "num2": 7})
            print(f"Multiplication Result: {multiply_result.content}")


if __name__ == "__main__":
    asyncio.run(main())
