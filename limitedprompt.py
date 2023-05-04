import streamlit as st
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
repo = g.get_repo("scooter7/limitedprompt")

def construct_index():
    max_input_size = 4096
    num_outputs = 512
    max_chunk_overlap = 20
    chunk_size_limit = 600

    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", max_tokens=num_outputs))

    index = GPTSimpleVectorIndex([], llm_predictor=llm_predictor, prompt_helper=prompt_helper)

    return index

def get_first_prompt():
    institution_type = st.selectbox("Select institution type:", ["Community College", "Public College/University", "Private College/University", "Other"])
    degree_level = st.selectbox("Select degree level:", ["Certificate", "Associate's degree", "Bachelor's degree", "Master's degree", "Doctoral degree", "Other"])
    program_type = st.selectbox("Select program type:", ["Undergraduate", "Graduate", "Certificate", "Other"])
    region = st.selectbox("Select region:", ["Northeast", "Midwest", "South", "West"])

    # Add submit button for dropdowns
    if st.button("Select all dropdowns"):
        # Save the selected values in session state
        st.session_state.institution_type = institution_type
        st.session_state.degree_level = degree_level
        st.session_state.program_type = program_type
        st.session_state.region = region

        # Set the flag to True
        st.session_state.dropdowns_selected = True

    # Check if all dropdowns are selected before moving to the name, email, and text input view
    if "dropdowns_selected" in st.session_state and st.session_state.dropdowns_selected:
        # Add a delay to give time for the page to update
        st.experimental_set_query_params(submit_clicked=True)

def chatbot(input_text, first_name, email):
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    response = index.query(input_text, response_mode="compact")

    # Create the content directory if it doesn't already exist
    content_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")
    os.makedirs(content_dir, exist_ok=True)

    # Write the user question and chatbot response to a file in the content directory
    with chat_container:
        st.write(f"{first_name}: {input_text}")
        st.write(f"Chatbot: {response}")

        # Save the first name and email in session state
        st.session_state.first_name = first_name
        st.session_state.email = email

    # Clear the input field after sending a message
    form.empty()
