import os
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["server.py"],  # Ensure correct absolute path
                "transport": "stdio",

            },
            "weather": {
                "url": "http://localhost:8000/mcp",  # Ensure server is running here
                "transport": "streamable_http",
            }

        }
    )
    # Get the tools from the servers:
    tools = await client.get_tools()
    # Create the model:
    model = ChatGroq(model="gemma2-9b-it")
    # Create the agent:
    agent = create_react_agent(
        model=model,
        tools=tools,
        debug=True
    )

    # Invoke the agent with the math tool:
    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    print("Math response:", math_response['messages'][-1].content)

    # Invoke the agent with the weather tool:
    weather_response = await agent.ainvoke(
        {"messages": [
            {"role": "user", "content": "what is the weather in California?"}]}
    )
    print("Weather response:", weather_response['messages'][-1].content)

asyncio.run(main())
