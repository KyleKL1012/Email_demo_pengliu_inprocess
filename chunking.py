from llama_index import download_loader, VectorStoreIndex, ServiceContext, SimpleDirectoryReader, Document
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from config import logger

def doc_chunking(text: str) -> list:
    """Split the text into a list of chunks.

    Args:
        text (str): The text.

    Returns:
        (list): List of strings (chunks). The index should be the chunk order.

    """
    max_num_of_tokens = '600'
    chunk_overlap = '200'
    logger.info(f'Splitting text into chunks of {max_num_of_tokens} tokens')
    document = Document(text = text)

    text_splitter = TokenTextSplitter(chunk_size = max_num_of_tokens, chunk_overlap = chunk_overlap)
    text_chunks = text_splitter.split_text(document.text)
    # tokenizer = globals_helper.tokenizer
    chunks = [c.strip() for c in text_chunks if c.strip()]


    logger.info(f'Generated {len(chunks)} chunks')
    
    return chunks





