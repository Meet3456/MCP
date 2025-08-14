from dataclasses_json import config
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
config = {"configurable":{"thread_id":"thread_1"}}


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
    # append the user input to the message history
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    # display the user message in the chat
    with st.chat_message("user"):
        st.text(user_input)

    # invoke the chatbot with user_input:
    response = chatbot.invoke({"messages": [HumanMessage(content=user_input)]},config=config)
    ai_response = response["messages"][-1].content

    # append the ai input to the message history
    st.session_state['message_history'].append({"role": "assistant", "content": ai_response})
    # display the ai message in the chat
    with st.chat_message("assistant"):
        st.text(ai_response)









    