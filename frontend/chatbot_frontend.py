import streamlit as st

with st.chat_message("user"):
    st.text("Hello from user")

with st.chat_message("assistant"):
    st.text("Hello from assistant")

user_input = st.chat_input("Type your message here...")

if user_input:
    with st.chat_message("user"):
        st.text(user_input)