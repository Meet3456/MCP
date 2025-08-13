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
    # messages: Annotated[list[AnyMessage], add_messages]
    # Where add_messages is a reducer function that is used to add messages to the state
    # List[AnyMessage] is a list of messages that are added to the state
    builder = StateGraph(MessagesState)

    # Adding nodes:
    builder.add_node("model_node", call_model)
    # note that the name should be "tools" only as the tools_condition function is used to route to the tools node
    builder.add_node("tools",ToolNode(tools))

    # Adding edges:
    builder.add_edge(START, "model_node")
    builder.add_conditional_edges(
        "model_node",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
        # Literal["tools", "__end__"]:
    )
    # iterative workflow: passing the result of tools to model again(if inittially llm returned a tool call) to check if another tool call is needed or not
    builder.add_edge("tools", "model_node")


    # Compiling the graph:
    graph = builder.compile()

    math_response = await graph.ainvoke({"messages": [HumanMessage(content = "what's 12 x 12?")]})

    print(math_response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())




