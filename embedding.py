from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.embeddings import OpenAIEmbeddings, SentenceTransformerEmbeddings 

from config import logger



def embed_text(text_list: list) -> list:
    """Calculate the embedding of a text chunk.

    Args:
        text_list (list): The list of texts to embed.

    Returns:
        (list): List of embeddings, one for each text.

    """
    model_name='sentence-transformers/all-MiniLM-L6-v2'
    logger.info(f"Embedding with model: {model_name}")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # Calculate the embedding
    doc_embeddings = embeddings.embed_documents(texts=text_list)

    return doc_embeddings
