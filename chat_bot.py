 # Fast custom UI using Gradio or Streamlit
import streamlit as st
import requests
import re

def chat_with_ollama(message, history, model_name):
    prompt = '\n'.join([f'User: {u}\nAI: {a}' for u, a in history]) + f'\nUser: {message}\nAI:'

    # print(prompt)  # DEBUG PRINT - helps us see the prompt being sent to Ollama

    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model_name,  # Or another model you've pulled
                'prompt': prompt,
                "temperature": 0.5,  # temperature: controls creativity
                "top_p": 0.9,         # nucleus sampling
                "repeat_penalty": 1.1, # repeat_penalty: reduce redundancy
                'stream': False,  # Set to True for streaming responses
            }
        )
        json_data = response.json()
        
        if 'response' in json_data:
            output = json_data['response']
        else:
            output = f"Error: Unexpected response from Ollama API - {json_data}"
        
    except Exception as e:
        output = f"Exception occurred: {str(e)}"
    
    # history.append((message, output))
    return output









st.set_page_config(page_title="Ollama Chatbot", page_icon="🤖")
st.title("💬 Ollama Chatbot")

# Model selector (user can change dynamically)
model_list = ["qwen3:1.7b", "llama3.2:1b"]  # Add the models you've pulled locally
selected_model = st.selectbox("Choose a model", model_list)


# Keep chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []  # List of {"role": "user"/"assistant", "content": str}


# Display all messages in chat history

chat_box = st.container()
with chat_box:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
# Chat input for user message
if prompt := st.chat_input("Type your message here..."):


    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Convert history into (user, ai) pairs for Ollama prompt
    history_pairs = [
        (m["content"], st.session_state.messages[i+1]["content"])
        for i, m in enumerate(st.session_state.messages[:-1])
        if m["role"] == "user" and i+1 < len(st.session_state.messages) and st.session_state.messages[i+1]["role"] == "assistant"
    ]


    # Get response from Ollama
    raw_response = chat_with_ollama(prompt, history_pairs,"qwen3:1.7b")
    #strip the response 
    response=re.sub(r"<think>.*?</think>", "", raw_response, flags=re.DOTALL).strip()

    # print("Response from Ollama:", response)  # DEBUG PRINT - helps us see the response

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
