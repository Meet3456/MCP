import streamlit as st
from langchain_core.messages import HumanMessage
import uuid
import os
import sys
import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.chatbot_backend import chatbot


# **************************************** utility functions *************************


def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    existing_ids = [t['id'] for t in st.session_state['chat_threads']]
    if thread_id not in existing_ids:
        st.session_state['chat_threads'].append({
            'id': thread_id,
            'created_at': datetime.datetime.now()
        })

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']


# **************************************** Session Setup ******************************


if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])


# **************************************** Sidebar UI *********************************


st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    formatted_time = thread_id["created_at"].strftime("%d %b, %I:%M:%S %p")
    if st.sidebar.button(formatted_time):
        st.session_state['thread_id'] = thread_id['id']
        messages = load_conversation(thread_id['id'])

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages


# **************************************** Main UI ************************************


# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    # first add the User message to message_history:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})

    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # Display the AI message:
    with st.chat_message('assistant'):
        try:
            with st.spinner("Thinking..."):

                def extract_content(chunk):
                    if isinstance(chunk.content, str):
                        return chunk.content
                    elif isinstance(chunk.content, dict) and "answer" in chunk.content:
                        return chunk.content["answer"]
                    return None

                ai_message=st.write_stream(
                    (text for chunk, metadata in chatbot.stream(
                        {"messages": [HumanMessage(content=user_input)]},
                        config=CONFIG,
                        stream_mode="messages"
                    )
                        if (text := extract_content(chunk)) is not None)
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")
            ai_message="Sorry, I encountered an error while processing your request."

    # Append AI message to history:
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
