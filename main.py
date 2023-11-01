import os
import re
from pathlib import Path
from typing import Optional
import base64
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from config import config, logger
from ingesting import ingesting_contract, ingesting_email
from htmlTemplates import css, bot_template, user_template
from query import queryemail, querycontract, question_answer


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



def display_convo(prompt):
    with st.container():
        # for i, message in enumerate(reversed(st.session_state.chat_history)):
        #     if i % 2 == 0:
        #         st.markdown(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        #     else:
        #         st.markdown(user_template.replace("{{MSG}}", message.content[len(prompt):]), unsafe_allow_html=True)
        for i, message in enumerate(reversed(st.session_state.chat_history)):
            message = str(message)
            if i % 2 == 0:
                st.markdown(bot_template.replace("{{MSG}}", message), unsafe_allow_html=True)
            else:
                st.markdown(user_template.replace("{{MSG}}", message), unsafe_allow_html=True)


def handle_userinput(user_question):
    if st.session_state.get("pdf_processed"):
        context_email = queryemail(user_question, 'EmailCollection', ["chunk_id", "doc_id", "title", "content", "metadata"])
        context_contract = querycontract(user_question, 'ContractContent', ["chunk_id", "doc_id", "title", "content", "metadata"])

        context_contract = context_contract['data']['Get']
        context_email = context_email['data']['Get']
        context = {**context_contract, **context_email}

        response = question_answer(model_platform="BAM", context=context, question=user_question, task='qa_pdf')

        st.session_state.chat_history.append({"user": user_question, "role": "user"})
        st.session_state.chat_history.append({"assistant": response, "role": "assistant"})

        print(st.session_state.chat_history)
        with st.spinner('Generating response...'):
            display_convo(user_question)
    else:
        response = question_answer(model_platform="BAM", context=None, question=user_question, task='qa')
        st.session_state.chat_history.append({"user": user_question, "role": "user"})
        st.session_state.chat_history.append({"assistant": response, "role": "assistant"})

        print(st.session_state.chat_history)
        with st.spinner('Generating response...'):
            display_convo(user_question)




def main():
    st.set_page_config(page_title="Multi-Document Chat Bot", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)
    init_ses_states()
    contract_vector = st.session_state.metric_result
    email_vector = st.session_state.metric_result
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
        if st.session_state.get("pdf_processed"):
            st.caption("Here is the result.")

            st.subheader("Collective Summary:")

            with st.form("user_input_form"):
                user_question = st.text_input("Ask a question about the result:")
                send_button = st.form_submit_button("Send")
            if send_button and user_question:
                handle_userinput(user_question)


        else:
            st.caption("Please upload your file on the left sidebar.")


if __name__ == "__main__":
    main()