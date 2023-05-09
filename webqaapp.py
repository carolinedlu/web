import logging
import streamlit as st
import requests
from bs4 import BeautifulSoup
from gpt_index import SimpleDirectoryReader, GPTListIndex, GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain.chat_models import ChatOpenAI
import sys
from datetime import datetime
import os
from github import Github


if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)

openai_api_key = st.secrets["OPENAI_API_KEY"]

logging.info(f"OPENAI_API_KEY: {openai_api_key}")

# Set up the GitHub API
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo("scooter7/web")


def fetch_urls(url_list):
    """Fetches the HTML content of each URL in url_list and returns a list of tuples
    containing the URL and its text content."""
    result = []
    for url in url_list:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text()
            result.append((url, text))
        except:
            logging.error(f"Failed to fetch content from {url}")
    return result


def construct_index(url_list):
    max_input_size = 4096
    num_outputs = 512
    max_chunk_overlap = 20
    chunk_size_limit = 600

    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", max_tokens=num_outputs))

    documents = fetch_urls(url_list)

    index = GPTSimpleVectorIndex(documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper)

    index.save_to_disk('index.json')

    return index


def chatbot(input_text, first_name, email):
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    prompt = f"{first_name} ({email}): {input_text}"
    response = index.query(prompt, response_mode="compact")

    # Create the content directory if it doesn't already exist
    content_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")

    os.makedirs(content_dir, exist_ok=True)

    # Write the user question and chatbot response to a file in the content directory
    filename = st.session_state.filename
    file_path = os.path.join(content_dir, filename)
    with open(file_path, 'a') as f:
        f.write(f"{first_name} ({email}): {input_text}\n")
        f.write(f"Chatbot response: {response.response}\n")
        
    # Write the chat file to GitHub
    with open(file_path, 'rb') as f:
        contents = f.read()
        repo.create_file(f"content/{filename}", f"Add chat file {filename}", contents)

    return response.response


url_list = ["https://www.carnegiehighered.com/", "https://www.carnegiehighered.com/solutions/"]
index = construct_index(url_list)

st.set_page_config(page_title="Carnegie Chatbot")

# Create a container to hold the chat messages
chat_container = st.container()

# Initialize last_send_pressed to False in session state
if "last_send_pressed" not in st.session_state:
    st.session_state.last_send_pressed = False

# Create a form to enter a message and submit it
form = st.form(key="my_form", clear_on_submit=True)
if "first_send" not in st.session_state:
    st.session_state.first_send = True

input_text = form.text_input("Enter your message:")
form_submit_button = form.form_submit_button(label="Send")

if form_submit_button and input_text:
    # Set the filename key every time the form is submitted
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.txt")
    st.session_state.filename = filename
    response = chatbot(input_text)

    # Remove parentheses from input_text
    input_text = input_text.replace("(", "").replace(")", "")

    # Write the user message and chatbot response to the chat history
    append_to_chat_history(input_text, response)

    # Write the user message and chatbot response to a file in the content directory
    content_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")
    os.makedirs(content_dir, exist_ok=True)
    file_path = os.path.join(content_dir, filename)
    with open(file_path, 'a') as f:
        f.write(f"{input_text}\n")  
        if response:
            f.write(f"Chatbot response: {response}\n")

    # Write the user message and chatbot response to the chat container
    with chat_container:
        st.write(f"{input_text}")
        if response:
            st.write(f"Chatbot: {response}")

# Clear the input field after sending a message
form.empty()

# Create a container to hold the chat messages
chat_container = st.container()

# Initialize last_send_pressed to False in session state
if "last_send_pressed" not in st.session_state:
    st.session_state.last_send_pressed = False

# Create a form to enter a message and submit it
form2 = st.form(key="my_form_2", clear_on_submit=True)
if "first_send" not in st.session_state:
    st.session_state.first_send = True

input_text = form2.text_input("Enter your message:")
form_submit_button = form2.form_submit_button(label="Send")

if form_submit_button and input_text:
    # Set the filename key every time the form is submitted
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.txt")
    st.session_state.filename = filename
    response = chatbot(input_text)

    # Remove parentheses from input_text
    input_text = input_text.replace("(", "").replace(")", "")

    # Write the user message and chatbot response to the chat history
    append_to_chat_history(input_text, response)

    # Write the user message and chatbot response to a file in the content directory
    content_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")
    os.makedirs(content_dir, exist_ok=True)
    file_path = os.path.join(content_dir, filename)
    with open(file_path, 'a') as f:
        f.write(f"{input_text}\n")  
        if response:
            f.write(f"Chatbot response: {response}\n")

    # Write the user message and chatbot response to the chat container
    with chat_container:
        st.write(f"{input_text}")
        if response:
            st.write(f"Chatbot: {response}")

# Clear the input field after sending a message
form.empty()
