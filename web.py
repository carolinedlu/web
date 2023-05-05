import logging
import streamlit as st
import requests
from bs4 import BeautifulSoup
from gpt_index import GPTSimpleVectorIndex, LLMPredictor, PromptHelper
from langchain.chat_models import ChatOpenAI
from datetime import datetime
import os
from github import Github

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    st.stop()

if "GITHUB_TOKEN" not in st.secrets:
    st.error("Please set the GITHUB_TOKEN secret on the Streamlit dashboard.")
    st.stop()

openai_api_key = st.secrets["OPENAI_API_KEY"]

logging.info(f"OPENAI_API_KEY: {openai_api_key}")

# Set up the GitHub API
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo("scooter7/web")

# Create docs directory
if not os.path.exists("docs"):
    os.makedirs("docs")

# Scrape text from URLs
urls = ["https://en.wikipedia.org/wiki/Python_(programming_language)", 
        "https://www.python.org/", 
        "https://docs.python.org/3/tutorial/index.html",
        "https://www.tutorialspoint.com/python/index.htm",
        "https://realpython.com/",
        "https://www.geeksforgeeks.org/python-programming-language/",
        "https://www.codecademy.com/learn/learn-python",
        "https://www.w3schools.com/python/",
        "https://www.datacamp.com/courses/intro-to-python-for-data-science",
        "https://www.learnpython.org/"]

for i, url in enumerate(urls):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text()
    filename = f"docs/{i}.txt"
    with open(filename, "w") as f:
        f.write(text)

# Set up chatbot
index = GPTSimpleVectorIndex.load("models/gpt_index/")
predictor = LLMPredictor.from_index(index)
helper = PromptHelper()
chatbot = ChatOpenAI(predictor=predictor, helper=helper, openai_api_key=openai_api_key)

# Chat with user and save chat history
with st.form(key="chat_form"):
    st.header("Chat with the bot")
    user_input = st.text_input("You", "")
    if st.form_submit_button("Send"):
        response = chatbot.get_response(user_input)
        st.text_area("Bot", response)
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"content/{timestamp}.txt"
        with open(filename, "w") as f:
            f.write(f"You: {user_input}\nBot: {response}")

# End of app
st.info("Thanks for chatting!")
st.balloons()
st.stop()
st.experimental_rerun()
st.write("To start a new chat, refresh the page.")
