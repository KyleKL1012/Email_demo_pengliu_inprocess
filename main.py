import os
from pathlib import Path
import base64
import streamlit as st
import streamlit.components.v1 as components
import weaviate
from ingesting import ingesting_contract, ingesting_email
from htmlTemplates import css
import requests


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

def init_ses_states():
    session_states = {
        "conversation": None,
        "chat_history": [],
        "metric_result": None,
        "pdf_upload": False
    }
    for state, default_value in session_states.items():
        if state not in st.session_state:
            st.session_state[state] = default_value

def upload_contract(tmp_file_path, class_name):
    st.session_state["conversation"] = None
    st.session_state["chat_history"] = []
    st.session_state["user_question"] = ""

    content_vector = ingesting_contract(source_path=tmp_file_path,
                                       class_name=class_name,
                                       class_description="testing")

    st.session_state.metric_result = content_vector

    st.session_state.pdf_processed = True

    return content_vector


def upload_email(tmp_file_path, class_name):
    st.session_state["conversation"] = None
    st.session_state["chat_history"] = []
    st.session_state["user_question"] = ""

    content_vector = ingesting_email(source_path=tmp_file_path,
                                       class_name=class_name,
                                       class_description="testing")

    st.session_state.metric_result = content_vector

    st.session_state.pdf_processed = True

    return content_vector




def main():
    st.set_page_config(page_title="Multi-Document Chat Bot", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)
    init_ses_states()
    contract_content_path = "./data/Quote Contract.pdf"
    st.title("Contract Advisor 🤖")
    st.subheader("Powered by IBM WatsonX")
    preview_tab, result_tab = st.tabs(["PDF Preview", "Result"])

    with preview_tab:
        with st.sidebar:
            st.title('🤗💬Please upload your file here.')
            st.write('Advisor Bot based on uploaded documents')
            temp_file_save = 'data/file/'
            contract_file = st.sidebar.file_uploader("Please upload the contract",
                                                     type=['.doc', '.docx', '.pdf', '.ppt', '.pptx'])
            email_file = st.sidebar.file_uploader("Please upload the email",
                                                     type=['.doc', '.docx', '.pdf', '.ppt', '.pptx'])
            if contract_file and email_file:
                if not os.path.exists(temp_file_save):
                    os.makedirs(temp_file_save)
                contract_file_path = os.path.join(temp_file_save, contract_file.name)
                email_file_path = os.path.join(temp_file_save, email_file.name)

                with open(contract_file_path, "wb") as f:
                    f.write(contract_file.getbuffer())
                with open(email_file_path, "wb") as f:
                    f.write(email_file.getbuffer())

                contract_vector = upload_contract(tmp_file_path=os.path.join(temp_file_save, contract_file.name),class_name=CONTRACT_CLASS_NAME)
                email_vector = upload_email(tmp_file_path=os.path.join(temp_file_save, email_file.name),class_name=EMAIL_CLASS_NAME)
                st.session_state.contract_result = contract_vector
                st.session_state.email_result = email_vector
                contract_content_path = contract_file_path
                st.session_state["pdf"] = ""
            else:
                st.session_state.pdf_processed = False

        st.sidebar.markdown('''
            ## About
            This app is an LLM-powered chatbot built using:
            - [WatsonX](https://dataplatform.cloud.ibm.com/wx/home?context=wx)
            ''')
        with open(contract_content_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            src = base64_pdf
        pdf_preview(src, 1)

    with result_tab:
        api_key = 'pak-AwkYTgLft5uB85xVSeqWdZIHaMfWD-VlWnxWC_WU50g'
        api_url = 'https://bam-api.res.ibm.com/v1/'
        question = st.text_input("Is there any request? (eg. Please find out if there is any ambiguity.)")

        auth_config = weaviate.AuthApiKey(
            api_key="5R0kyDE1SNBsyrNwZYHiBSgQY6nmluSPxcsA")

        # Instantiate the client with the auth config
        client = weaviate.Client(
            url="https://contract-test-fyb21k5f.weaviate.network",
            auth_client_secret=auth_config
        )

        query1 = (
            client.query.get("ContractContent", ["content", "chunk_id"])
                .with_limit(1)
        )
        contract_vector = query1.do()

        query2 = (
            client.query.get("EmailCollection", ["content", "chunk_id"])
                .with_limit(2)
        )
        email_vector = query2.do()

        contract_content_text = ""
        for i in contract_vector['data']['Get'][CONTRACT_CLASS_NAME]:
            contract_content_text += str(i['chunk_id']) + " " + str(i['content']) + "\n"
        email_content_text = ""
        for i in email_vector['data']['Get'][EMAIL_CLASS_NAME]:
            email_content_text += str(i['chunk_id']) + " " + str(i['content']) + "\n"



        # Prepare template and generate response
        prompt_template = f"Now you are a consultant that specializes in answering questions regarding a BPO (Business Process Outsourcing) contract. The purpose  is to assist users in understanding the contract terms, obligations, and return information to them which they are interested in.\
                    Please refer to the information in the BPO contract from the following content:{contract_content_text} and the information in the email from customers from the following content:{email_content_text}\
                    Please answer my question using the following template:\
                    Questions: {question}\
                    Answer:"


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


if __name__ == "__main__":
    main()