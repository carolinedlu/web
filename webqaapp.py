import logging
import streamlit as st
from langchain.chat_models import ChatOpenAI
import sys
import os
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import faiss
from langchain import OpenAI
from langchain.chains import VectorDBQAWithSourcesChain
from datetime import datetime
from github import Github
import pickle

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)

openai_api_key = st.secrets["OPENAI_API_KEY"]

logging.info(f"OPENAI_API_KEY: {openai_api_key}")

# Set up the GitHub API
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo("scooter7/web")

# Initialize chat history list
chat_history = []

def append_to_chat_history(question, answer):
    chat_history.append({'user': question, 'bot': answer})

def extract_text_from(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    return '\n'.join(line for line in lines if line)

urls = [
    "https://www.carnegiehighered.com/solutions/",
    "https://www.carnegiehighered.com/services/",
    "https://www.carnegiehighered.com/about/"
]

pages = []
for url in urls:
    pages.append({'text': extract_text_from(url), 'source': url})


text_splitter = CharacterTextSplitter(chunk_size=1500, separator="\n")
docs, metadatas = [], []
for page in pages:
    splits = text_splitter.split_text(page['text'])
    docs.extend(splits)
    metadatas.extend([{"source": page['source']}] * len(splits))

with open("faiss_store.pkl", "rb") as f:
    store = pickle.load(f)

from langchain.chains import RetrievalQAWithSourcesChain.from_llm(
            llm=OpenAI(temperature=0), vectorstore=store)

st.title(" ")

def chatbot(input_text):
    prompt = input_text.strip()
    # Remove parentheses from input_text
    if prompt.startswith("(") and prompt.endswith(")"):
        prompt = prompt[1:-1]
    response = chain(prompt)

    # Create the content directory if it doesn't already exist
    content_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")
    os.makedirs(content_dir, exist_ok=True)
    
    if 'answer' in response:
        return response['answer']
    else:
        return ''

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
