from llama_index import SimpleDirectoryReader
from llama_index import download_loader
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .pdf_image_reader import PdfImageReader
from config import logger



def parse_doc(source_path):
    """Parse a document.

    Args:
        source_path (str): the path to the document.

    Returns:
        (list): A list of Document object.

    """
    try:
        path = Path(source_path)
        if path.suffix in [".jpg", ".png", ".jpeg"]:
            logger.info("Parsing image using pytesseract")
            ImageReader = download_loader("ImageReader")
            imageLoader = ImageReader(text_type="plain_text")
            documents = imageLoader.load_data(file=path)
        elif path.suffix in [".pdf"]:
            logger.info("Parsing pdf")
            PdfReader = download_loader("PDFReader")
            loader = PdfReader()
            documents = loader.load_data(file=path)          
        # TODO: general approach to process other format files
        if (not documents or documents[0].text.strip() == "") and path.suffix == ".pdf":
            logger.info("Parsing image with extension PDF")
            download_loader("FlatPdfReader")
            ImageReader = download_loader("ImageReader")
            imageLoader = ImageReader(text_type="plain_text")
            pdfLoader = PdfImageReader(image_loader=imageLoader)
            documents = pdfLoader.load_data(file=path)

        return documents
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        raise e
    


