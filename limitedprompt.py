import logging
import openai
import os
import streamlit as st
import importlib
import sys
from github import Github
from langchain.base_language import BaseLanguageModel

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)

openai_api_key = st.secrets["OPENAI_API_KEY"]

logging.info(f"OPENAI_API_KEY: {openai_api_key}")

# Set up the GitHub API
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo("scooter7/limitedprompt)

# Define the options for the dropdown
program_options = ["Computer Science", "Psychology", "Biology", "Marketing"]

# Define the options for the radio buttons
institution_type_options = ["Public", "Private"]

# Define the options for the text input
degree_level_options = ["Associate", "Bachelor's", "Master's", "Doctoral"]
region_options = ["Northeast", "Southeast", "Midwest", "West"]

# Create the Streamlit app
def app():
    importlib.reload(sys)
    
    st.title("Limiting Text Prompts with Interactive Elements")

    # Add a dropdown for program selection
    program = st.selectbox("Select a program:", program_options)

    # Add radio buttons for institution type selection
    institution_type = st.radio("Select an institutional type:", institution_type_options)

    # Add a text input for degree level selection
    degree_level = st.text_input("Enter a degree level (e.g. Bachelor's):")

    # Add a dropdown for region selection
    region = st.selectbox("Select a region:", region_options)

    # Generate the initial text prompt based on the user's selections
    prompt = f"I am interested in {program} at {institution_type} institutions for {degree_level} degrees in the {region} region."

    # Use the OpenAI API to generate a response to the initial prompt
    max_tokens = 1024
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.5,
    )

    output_text = response.choices[0].text

    # Display the initial response on the page
    st.write(response.choices[0].text.encode('utf-8').decode())

    # Add a text input for follow-up questions
    followup_question = st.text_input("Ask a follow-up question:")

    # Use the user's follow-up question as the prompt for the OpenAI API
    if followup_question:
        prompt = f"{followup_question}"
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=0.5,
        )

        output_text = response.choices[0].text

        st.write(response.choices[0].text.encode('utf-8').decode())


if __name__ == "__main__":
    app()
