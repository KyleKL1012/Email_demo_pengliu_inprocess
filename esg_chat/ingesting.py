import json
import pandas as pd
import os
from esg_chat.loading.doc_loading import parse_doc
from esg_chat.processing.chunking import doc_chunking
from esg_chat.processing.embedding import embed_text
from esg_chat.database.weaviate_db import Weaviate,WeaviateMetric


def parsing_metric(source_path, class_name, class_description):
    """Ingest data from source path, clean, chunk, embed and store in database.

    Args:
        source_path (str): The document path.
        class_name (str): The name of this collection storing in Weaviate.
        class_description (str): The collection description.

    """
    # loading
    pages = parse_doc(source_path)
    # cleaning
    # chunking and embedding
    chunk_obj_list = []
    chunk_vectors = []
    for page in pages:
        chunks = doc_chunking(text=page.text)
        chunk_vectors.extend(embed_text(text_list=chunks))
        for idx, chunk in enumerate(chunks):
            chunk_obj = {}
            chunk_obj["chunk_id"] = idx
            chunk_obj["doc_id"] = page.metadata["file_name"]  # actually should be sth else
            chunk_obj["title"] = page.metadata["file_name"]
            chunk_obj["content"] = chunk
            chunk_obj["metadata"] = json.dumps({"page_number": page.metadata["page_label"]})
            chunk_obj_list.append(chunk_obj)
    # storing
    wea_db = Weaviate()
    if wea_db.varify_class(class_name=class_name):
        wea_db.delete_class(class_name=class_name)
    wea_db.create_class(class_name=class_name, class_description=class_description)
    wea_db.ingest_data(class_name=class_name, chunk_list=chunk_obj_list, vector_list=chunk_vectors)

    # parsing metric to chunk vector
    metric_vector = parsing_metric(source_path, class_name, class_description)

    return metric_vector


def ingesting_pipeline(source_path,class_name,class_description):
    """Ingest data from source path, clean, chunk, embed and store in database.

    Args:
        source_path (str): The document path.
        class_name (str): The name of this collection storing in Weaviate.
        class_description (str): The collection description.
    
    """
    # loading
    pages = parse_doc(source_path)
    # cleaning
    # chunking and embedding
    chunk_obj_list = []
    chunk_vectors = []
    for page in pages:
        chunks = doc_chunking(text=page.text)
        chunk_vectors.extend(embed_text(text_list=chunks))
        for idx,chunk in enumerate(chunks):
            chunk_obj = {}
            chunk_obj["chunk_id"] = idx
            chunk_obj["doc_id"] = page.metadata["file_name"] # actually should be sth else
            chunk_obj["title"] = page.metadata["file_name"]
            chunk_obj["content"] = chunk
            chunk_obj["metadata"] = json.dumps({"page_number":page.metadata["page_label"]})
            chunk_obj_list.append(chunk_obj)
    # storing
    wea_db = Weaviate()
    if wea_db.varify_class(class_name=class_name):
        wea_db.delete_class(class_name=class_name)
    wea_db.create_class(class_name=class_name,class_description=class_description)
    wea_db.ingest_data(class_name=class_name,chunk_list=chunk_obj_list,vector_list=chunk_vectors)

    # parsing metric to chunk vector
    metric_vector = parsing_metric(source_path, class_name, class_description)

    return metric_vector
