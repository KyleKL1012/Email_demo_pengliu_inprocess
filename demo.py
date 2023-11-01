import os
import io
import streamlit as st
import streamlit.components.v1 as components
import PyPDF2
import base64
import requests
from dotenv import load_dotenv
from pathlib import Path
from config import config, logger
from esg_chat.ingesting import ingesting_pipeline
from htmlTemplates import css, bot_template, user_template
from esg_chat.query import query, question_answer
import json


api_key = 'pak-AwkYTgLft5uB85xVSeqWdZIHaMfWD-VlWnxWC_WU50g'
api_url = 'https://bam-api.res.ibm.com/v1/'

st.set_page_config(page_title="Multi-Document Chat Bot", page_icon=":books:")
st.title("Contract Advisor 🤖")
st.subheader("Powered by IBM WatsonX")
preview_tab, result_tab = st.tabs(["Contract Preview", "Result"])

EMAIL_CLASS_NAME = 'EmailCollection'
CONTRACT_CLASS_NAME = 'ContractContent'

pdf_preview_dir = (Path(__file__).parent / "streamlit_components/pdf_preview").absolute()


pdf_preview_func = components.declare_component(
	"pdf_preview", path=str(pdf_preview_dir)
)

# Create the python function that will be called
def pdf_preview(
    src, page
):
    """
    Add a descriptive docstring
    """
    component_value = pdf_preview_func(
        src=src, page=page, key="preview1", default=1
    )

    return component_value



with preview_tab:
    with st.sidebar:
        st.title('🤗💬Please upload your file here.')
        st.write('Advisor Bot based on uploaded documents')
        # methods = ['QA based on uploaded documents']
        # qa_method = st.sidebar.radio('Pick a method', methods)
        # Display file upload fields
        contract_file = st.file_uploader("Upload Contract PDF File", type="pdf")
        email_file = st.file_uploader("Upload Email Text File", type="txt")

        file_path = "./data/Quote Contract.pdf"  # Default value for file_path

        if contract_file:
            temp_file_save = "data/"
            os.makedirs(temp_file_save, exist_ok=True)  # Create the 'data/' directory if it doesn't exist
            uploaded_file_path = os.path.join(temp_file_save, contract_file.name)
            with open(uploaded_file_path, "wb") as f:
                f.write(contract_file.getbuffer())
            file_path = f.name
            st.session_state["pdf"] = ""
        else:
            st.session_state.pdf_processed = False
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            src = base64_pdf
    pdf_preview(src, 1)


    st.sidebar.markdown('''
                ## About
                This app is an LLM-powered chatbot built using:
                - [WatsonX](https://dataplatform.cloud.ibm.com/wx/home?context=wx)
                ''')

with result_tab:
    # Check if files are uploaded
    if contract_file is not None and email_file is not None:
        # Read contract PDF file and extract text
        contract_pdf_path = "temp_contract.pdf"
        with open(contract_pdf_path, "wb") as file:
            file.write(contract_file.read())

        with open(contract_pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            contract_text = ""
            for page in reader.pages:
                contract_text += page.extract_text()

        # Read email content from TXT file
        email_content = email_file.read()

        # Prepare template and generate response
        prompt_template = '''
        Analyze the discount requests mentioned in the email conversation and determine their legality based on the corresponding contract.

        Question: [question]

        Output: 
        '''

        question = st.text_input("Is there any request? (eg. Please find out if there is any ambiguity.)")
        if question:
            template = prompt_template.format(question=question)

            bam_input = {
                "model_id": "meta-llama/llama-2-7b-chat",
                "inputs": [template],
                "parameters": {
                    "decoding_method": "greedy",
                    "temperature": 0.1,
                    "top_p": 0.8,
                    "top_k": 3,
                    "repetition_penalty": 1,
                    "min_new_tokens": 50,
                    "max_new_tokens": 1500,
                    "moderations": {
                        "hap": {
                            "input": True,
                            "threshold": 0.7,
                            "output": True
                        }
                    }
                }
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            url = api_url + 'generate'

            responses = requests.post(
                url=url,
                headers=headers,
                json=bam_input
            )

            if responses.status_code == 200:
                response_json = responses.json()
                if 'results' in response_json and len(response_json['results']) > 0:
                    generated_text = response_json['results'][0].get('generated_text')
                    if generated_text:
                        st.write("This is your answer:", generated_text)
                    else:
                        st.write("No generated text found in the response.")
                else:
                    st.write("No results found in the response.")
            else:
                st.write(f"Request failed with status code: {responses.status_code}")
                st.write(f"Response content: {responses.content}")