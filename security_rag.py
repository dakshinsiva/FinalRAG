import logging
import sys
from PyPDF2 import SimpleDirectoryReader
import logging

def load_documents(input_dir="/Users/dakshinsiva/Downloads/docs"):  # Using the original path from usage_example.py
    """Load documents from a single directory"""
    try:
        reader = SimpleDirectoryReader(
            input_dir=input_dir,
            filename_as_id=True,
            recursive=False,
            required_exts=[".pdf", ".txt", ".doc", ".docx"],
            exclude_hidden=True
        )
        documents = reader.load_data()
        logger.info(f"Loaded {len(documents)} documents from {input_dir}")
        return documents
    except Exception as e:
        logger.error(f"Document loading failed: {str(e)}")
        return None

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Initialize models
    if not initialize_models():
        logger.error("Failed to initialize models. Exiting.")
        sys.exit(1)

    # Load documents from single directory
    documents = load_documents("/Users/dakshinsiva/Downloads/docs")  # Using original path
    if not documents:
        logger.error("Failed to load documents. Exiting.")
        sys.exit(1)

    # Rest of the code remains the same...
