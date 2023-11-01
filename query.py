import json
from weaviate_db import WeaviateEmail, WeaviateContract
from model.bam import Bam
from model.watsonx import Watsonx

from config import logger


def queryemail(input_string: str, class_name: str, properties: list) -> json:
    """Query weaviate to get related text chunks.

    Args:
        input_string (str): the user input query.
        class_name (str): the weaviate class name to query.

    Returns:
        json: Related text chunks.
    """
    wea_db = WeaviateEmail()
    query_result = wea_db.query_near_vector(input_string=input_string, class_name=class_name,
                                            properties=properties)
    logger.info(f"Query result: {str(query_result)}")
    return query_result

def querycontract(input_string: str, class_name: str, properties: list) -> json:
    """Query weaviate to get related text chunks.

    Args:
        input_string (str): the user input query.
        class_name (str): the weaviate class name to query.

    Returns:
        json: Related text chunks.
    """
    wea_db = WeaviateContract()
    query_result = wea_db.query_near_vector(input_string=input_string, class_name=class_name,
                                            properties=properties)
    logger.info(f"Query result: {str(query_result)}")
    return query_result

def get_context(query_result: json, class_name: str) -> str:
    """Combine the text chunks together.

    Args:
        query_result (json): the weaviate query result.
        class_name (str): the weaviate class which the query result generated from.

    Returns:
        str: the combined text.
    """
    try:
        chunk_list = [x["content"] for x in query_result["data"]["Get"][class_name]]
        return " ".join(chunk_list)
    except Exception as e:
        logger.error(f"Error generating context: {e}")
        return ""


def generate_metric_tb(model_platform: str, context: str, question: str, task: str) -> dict:
    """Generate metric table.

    Args:
        model_platform (str): BAM or WATSONX.
        context (str): the related text.
        question (str): the question.

    Returns:
        result (dict): the model response.
    """
    model_input = f'''
    Answer the question and provide your reasoning.

    The following key information was extracted from the email from customers. Does this align with the assessment of "{question}"?
    Please answer with 'Aligned' or 'Not aligned'.
    Information:
    {context}

    Response:
    '''
    result = {}
    if model_platform == "BAM" and task == "compare":
        bam_instance = Bam()
        result = bam_instance.call_bam(input_str=model_input, task="compare")

    elif model_platform == "WATSONX":
        watsonx_instance = Watsonx()
        result = watsonx_instance.call_watsonx(input_str=model_input, task="qa")
    logger.info(f"{model_platform} QA result: {str(result)}")

    return result


def question_answer(model_platform: str, context: str, question: str, task: str) -> dict:
    """Get question answer from LLM.

    Args:
        model_platform (str): BAM or WATSONX.
        context (str): the related text.
        question (str): the question.

    Returns:
        result (dict): the model response.
    """
    if task == 'qa_pdf':
        prompt = f'''
                You are a academic assistant AI chatbot here to assist the user based on the academic PDFs they uploaded, and the subsequent Huggingface embeddings. 
                This academic persona allows you to use as much outside academic responses as you can.
                But remember this is an app for academix PDF question. Please respond in as academic a way as possible, with an academix audience in mind.
                Please assist the user to the best of your knowledge, with this academic persona based on the following PDF context, embeddings and the user input. 

                PDF CONTEXT:
                {context}
                USER INPUT: 
                {question}
                RESPONSE:
        '''
    elif task == 'qa':
        prompt = '''
                You are a assistant AI chatbot based on your knowledge base. If you don't know just say I don't know.
                USER INPUT: 
                {question}
                RESPONSE:
        '''

    result = {}
    if model_platform == "BAM" and task == "qa_pdf":
        bam_instance = Bam()
        result = bam_instance.call_bam(input_str=prompt, task="qa_pdf")

    elif model_platform == "BAM" and task == "qa":
        bam_instance = Bam()
        result = bam_instance.call_bam(input_str=prompt, task="qa")
    logger.info(f"{model_platform} QA result: {str(result)}")
    return result


def summarization(model_platform: str, context: str):
    if model_platform == "BAM":
        bam_instance = Bam()
        model_input = f"Summarize the following text without adding additional information.\n Text: {context} \n Summary: "
        result = bam_instance.call_bam(input_str=model_input, task="summarization")
        return result