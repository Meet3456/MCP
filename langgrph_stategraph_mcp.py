from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END , MessagesState
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

import asyncio

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

model = ChatGroq(model="gemma2-9b-it")

async def main():
    # Initialize the multi server mcp client:
    client = MultiServerMCPClient(
        {
            "math":{
                "command": "python",
                "args": ["server.py"],
                "transport": "stdio",
            },
            "weather":{
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            }
        }
    )

    # Get the tools from the servers:
    tools = await client.get_tools()

    def call_model(state: MessagesState):
        # MessagesState Looks like - messages: Annotated[list[AnyMessage], add_messages]
        response = model.bind_tools(tools).invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)

    # Adding nodes:
    builder.add_node("model", call_model)
    builder.add_node(ToolNode(tools))

    # Adding edges:
    builder.add_edge(START, "model")
    builder.add_conditional_edges(
        "model",
        tools_condition,
    )
    builder.add_edge("tools", "model")

    # Compiling the graph:
    graph = builder.compile()

    math_response = await graph.ainvoke({"messages": [HumanMessage(content = "what's (3 + 5) x 12?")]})

    print(math_response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())




