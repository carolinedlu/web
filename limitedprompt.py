import logging
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

def display_dropdown_fields():
    institution_type = st.selectbox("Select institution type:", ["Community College", "Public College/University", "Private College/University", "Other"])
    degree_level = st.selectbox("Select degree level:", ["Certificate", "Associate's degree", "Bachelor's degree", "Master's degree", "Doctoral degree", "Other"])
    program_type = st.selectbox("Select program type:", ["Undergraduate", "Graduate", "Certificate", "Other"])
    region = st.selectbox("Select region:", ["Northeast", "Midwest", "South", "West"])

    return institution_type, degree_level, program_type, region

def get_first_prompt(dropdown_selections):
    institution_type, degree_level, program_type, region = dropdown_selections
    return f"Please provide a list of colleges that meet {institution_type}, {degree_level}, {program_type}, and {region} region of the US."

def chatbot(input_text, first_name, email):
    index = GPTSimpleVectorIndex.load_from_disk('index.json')

    if "first_prompt_sent" not in st.session_state:
        st.session_state.first_prompt_sent = False

if not st.session_state.first_prompt_sent:
        st.session_state.first_prompt_sent = True
        dropdown_selections = display_dropdown_fields()
        input_text = get_first_prompt(dropdown_selections)
        st.text_input("Enter your first name:", key="first_name")
       
# Set up the initial dropdown fields
institution_type = st.selectbox("Select institution type:", ["Community College", "Public College/University", "Private College/University", "Other"])
degree_level = st.selectbox("Select degree level:", ["Certificate", "Associate's degree", "Bachelor's degree", "Master's degree", "Doctoral degree", "Other"])
program_type = st.selectbox("Select program type:", ["Undergraduate", "Graduate", "Certificate", "Other"])
region = st.selectbox("Select region:", ["Northeast", "Midwest", "South", "West"])

if "dropdowns_filled" not in st.session_state:
    st.session_state.dropdowns_filled = False

# Check if all dropdown fields are filled
if institution_type and degree_level and program_type and region:
    st.session_state.dropdowns_filled = True

# If all dropdown fields are filled, send the initial prompt
if st.session_state.dropdowns_filled and not st.session_state.first_prompt_sent:
    first_prompt = get_first_prompt()
    with chat_container:
        st.write(f"Chatbot: Please provide a list of colleges that meet {institution_type}, {degree_level}, {program_type}, and {region} region of the US.")
    st.session_state.first_prompt_sent = True

# Display the name, email, and input fields after the initial prompt is sent
if st.session_state.first_prompt_sent:
    if "first_send" not in st.session_state:
        st.session_state.first_send = True

    if st.session_state.first_send:
        first_name = form.text_input("Enter your first name:", key="first_name")
        email = form.text_input("Enter your email address:", key="email")
        st.session_state.first_send = False
    else:
        first_name = st.session_state.first_name
        email = st.session_state.email

    input_text = form.text_input("Enter your message:")
    form_submit_button = form.form_submit_button(label="Send")

    if form_submit_button and input_text:
        # Set the filename key every time the form is submitted
        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.docx")
        st.session_state.filename = filename

        response = chatbot(input_text, first_name, email)

        # Write the user message and chatbot response to the chat container
        with chat_container:
            st.write(f"{first_name}: {input_text}")
            st.write(f"Chatbot: {response}")

        # Save the first name and email in session state
        st.session_state.first_name = first_name
        st.session_state.email = email

    # Clear the input field after sending a message
    form.empty()
