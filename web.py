import logging
import os
import requests
import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime
from github import Github
from gpt_index import GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain.chat_models import ChatOpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up Streamlit secrets
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)
openai_api_key = st.secrets["OPENAI_API_KEY"]
logging.info(f"OPENAI_API_KEY: {openai_api_key}")

# Set up the GitHub API
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo("scooter7/web")

# Define function to extract text from URL and save as text file
def extract_text_from_url(url, output_dir):
    logging.info(f"Extracting text from URL: {url}")
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    text = soup.get_text()
    filename = f"{os.path.join(output_dir, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))}.txt"
    with open(filename, "w") as f:
        f.write(text)
    return filename

# Create folder for text files
if not os.path.exists("docs"):
    os.makedirs("docs")

# Extract text from 10 URLs and save as text files in docs folder
urls = [
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://en.wikipedia.org/wiki/JavaScript",
    "https://en.wikipedia.org/wiki/Java_(programming_language)",
    "https://en.wikipedia.org/wiki/C%2B%2B",
    "https://en.wikipedia.org/wiki/Python_(film)",
    "https://en.wikipedia.org/wiki/JavaScript_(film)",
    "https://en.wikipedia.org/wiki/Java_(1995_film)",
    "https://en.wikipedia.org/wiki/C%2B%2B_(film)",
    "https://en.wikipedia.org/wiki/Python_(Monty)_Pictures",
    "https://en.wikipedia.org/wiki/JavaScript_Monthly"
]
for url in urls:
    extract_text_from_url(url, "docs")

# Create GPT chatbot
logging.info("Creating GPT chatbot")
index = GPTSimpleVectorIndex("docs", vector_len=512)
predictor = LLMPredictor(index)
chatbot = ChatOpenAI(prompt_helper=PromptHelper(predictor))

# Define function to save chat history
def save_chat_history(chat_history, output_dir):
    filename = f"{os.path.join(output_dir, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))}.txt"
    with open(filename, "w") as f:
        f.write(chat_history)
    return filename

# Create folder for chat history
if not os.path.exists("content"):
    os.makedirs("content")

# Start chat with GPT chatbot
logging.info("Starting chat with GPT chatbot")
form = st.form(key="chat")
message = form.text_input(label="You")
chat_history = ""
while True:
    if message:
        response = chatbot.message(message)
        chat_history += f"You: {message}\nBot: {response}\n\n"
        message = form.text_input(label="You", value="")
    else:
        break
form.empty()

# Save chat history
logging.info("Saving chat history")
