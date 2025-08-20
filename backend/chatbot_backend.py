from langgraph.graph import StateGraph,START,MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_tavily import TavilySearch
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "ChatBot"


# Tavily search function:
tool = TavilySearch(max_results=2,search_depth="advanced")

# Custom function
def multiply(a:float,b:float)->float:
    """Multiply a and b

    Args:
        a (float): first float
        b (float): second float

    Returns:
        float: output float
    """
    return a*b

def add(a:float,b:float)->float:
    """Add a and b

    Args:
        a (float): first float
        b (float): second float

    Returns:
        float: output float
    """
    return a+b

# Define the tools:
tools = [tool,multiply,add]

# Initialize the LLM:
llm = ChatGroq(model="qwen/qwen3-32b")

# Bind tools to the LLM:
llm_with_tool = llm.bind_tools(tools)

# Define the State:we can manually write or can even call MessagesState directlt while defining the chat node function:
class ChatState(TypedDict):

    messages : Annotated[list[BaseMessage], add_messages]
    '''
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages : Annotated[list,add_messages]
    '''

# Defining the node functionality:
def chat_node(state: ChatState):

    # take user query from state
    messages = state["messages"]
    # send to llm and get response
    response = llm_with_tool.invoke(messages)
    # update state with new message and return:
    return {"messages": [response]}

# Simpler way:
def chat_node_simpler(state: MessagesState):

    return {"messages":[llm_with_tool.invoke(state["messages"])]}


# Create the Database:
conn = sqlite3.connect(database="Test.db",check_same_thread=False)

# checkpointer for saving memory:
checkpointer = SqliteSaver(conn=conn)

# initializing the state graph
builder = StateGraph(ChatState)

# Adding nodes:
builder.add_node("tool_calling_llm", chat_node_simpler)
builder.add_node("tools",ToolNode(tools))

# Adding Edges
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",tools_condition
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
)
# iterative workflow: passing the result of tools to model again(if initially llm returned a tool call) to check if another tool call is needed or not
builder.add_edge("tools", "tool_calling_llm")

# Compile the graph
chatbot = builder.compile(checkpointer=checkpointer)

# Checkpointer has a method called list which returns all saved checkpoints for any given thread or for all threads id passed None:
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)

# Monitoring
# Evaluation
# Alerts
# Dataset Creation and Annotation
# Prompt Engineering(try diff prompts,store it)
