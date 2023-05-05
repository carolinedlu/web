import llama_index
from llama_index import GPTSimpleVectorIndex, download_loader
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
from langchain.chains.conversation.memory import ConversationBufferMemory

BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")

loader = BeautifulSoupWebReader()
documents = loader.load_data(urls=['https://google.com'])
index = GPTSimpleVectorIndex(documents)

tools = [
    Tool(
        name="Website Index",
        func=lambda q: index.query(q),
        description=f"Useful when you want answer questions about the text on websites.",
    ),
]
llm = OpenAI(temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history")
agent_chain = initialize_agent(
    tools, llm, agent="zero-shot-react-description", memory=memory
)

output = agent_chain.run(input="What language is on this website?")

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


docs_directory_path = "docs"
index = GPTSimpleVectorIndex.load_from_disk('index.json')

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
