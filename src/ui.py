import streamlit as st
import requests
import json

# Page Config
st.set_page_config(page_title="EQx Economic Bot", page_icon="📈")
st.title("📈 EQx Economic Report Assistant")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle User Input
if prompt := st.chat_input("Ask about global economic trends..."):
    # 1. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Stream Assistant Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Connect to your FastAPI Backend
        API_URL = "http://localhost:8000/stream-chat"
        
        try:
            with requests.post(API_URL, json={"user_message": prompt}, stream=True) as r:
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        text = chunk.decode("utf-8")
                        full_response += text
                        # Update the UI instantly
                        message_placeholder.markdown(full_response + "▌")
                        
            message_placeholder.markdown(full_response)
            
            # Save to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Error connecting to server: {e}")