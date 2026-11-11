import streamlit as st
import requests
import datetime

# from exception.exceptions import TradingBotException
import sys

BASE_URL = "http://localhost:8000"  # Backend endpoint, baseurl when we are going to expose functionality as api  

st.set_page_config(
    # page_title="🌍 Travel Planner Agentic Application",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("🌍 Travel Planner Agentic Application")
# 1. Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Render all past messages from history every time the app reruns
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Chat input box at the bottom (using st.chat_input for a modern chat UI)
if user_input := st.chat_input("Ask me about your trip..."):
    # Append and display the user's message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.spinner("Bot is thinking..."):
            # Send the ENTIRE message history to the backend for context
            payload = {"messages": st.session_state.messages}
            response = requests.post(f"{BASE_URL}/query", json=payload)

        if response.status_code == 200:
            answer = response.json().get("answer", "No answer returned.")
            
            # Display and append the assistant's response
            with st.chat_message("assistant"):
                st.markdown(answer)
            
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error(f"Server Error ({response.status_code}): {response.text}")

    except Exception as e:
        st.error(f"The request failed due to {e}")