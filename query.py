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



def question_answer(model_platform: str, contract: str, email:str, question: str, task: str) -> dict:
    """Get question answer from LLM.

    Args:
        model_platform (str): BAM or WATSONX.
        context (str): the related text.
        question (str): the question.

    Returns:
        result (dict): the model response.
    """
    if task == 'qa_pdf':
        prompt = f"Now you are a consultant that specializes in answering questions regarding a BPO (Business Process Outsourcing) contract. The purpose  is to assist users in understanding the contract terms, obligations, and return information to them which they are interested in.\
                Please refer to the information in the BPO contract from the following content:{contract} and the information in the email from customers from the following content:{email}.\
                Please answer my question using the following template:\
                Questions: Questions here\
                Answer: Answer of the question here\
                Questions: {question}\
                Answer:"
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