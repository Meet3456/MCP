import streamlit as st
from langchain_core.messages import HumanMessage
import os
import sys

# Ensure the project root is on sys.path so sibling package 'backend' is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import the compiled LangGraph app (chatbot) from the backend package
from backend.chatbot_backend import chatbot

# initialize the config:
config = {"configurable": {"thread_id": "thread_1"}}


if "message_history" not in st.session_state:
    # session_state is a dictionary-like object that allows you to store and retrieve values
    # if message_history is not present, initialize it , where key is 'message_history' and value is empty list initially
    st.session_state['message_history'] = []


# print the entire message history and then the current user input and ai response:
for messages in st.session_state['message_history']:
    with st.chat_message(messages["role"]):
        st.text(messages["content"])

user_input = st.chat_input("Type your message here...")

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})

    with st.chat_message('user'):
        st.text(user_input)

    # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            chunk.content if isinstance(chunk.content, str) else chunk.content.get("answer", "")
            for chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config={"configurable": {"thread_id": "thread-1"}},
                stream_mode="messages"
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
