import logging
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.readers.file import PDFReader
from llama_index.core import SimpleDirectoryReader
import sys
import time
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI  # Updated import

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom QA prompt template

# Update the QA template to better match security audit questions
CYBERSEC_QA_TEMPLATE = PromptTemplate(
    """You are a cybersecurity compliance auditor reviewing cloud infrastructure documentation. Answer based on the provided documentation.

    Context:
    ---------------------
    {context_str}
    ---------------------

    Question: {query_str}

    Format your response:
    1. Finding: [Direct answer with specific configurations/settings found]
    2. Evidence: [Specific documentation/screenshots/configurations cited]
    3. Compliance Status: [Compliant/Non-Compliant/Partial/Unable to Determine]
    4. Gap Analysis: [Missing documentation or configurations needed]
    5. Recommendations: [If applicable]

    If documentation is insufficient, explicitly state what additional evidence is required.
    """
)

# Example questions you might ask:
"""
1. Policy Questions:
   - What is our password policy?
   - How often are security policies reviewed?
   - What is our data retention policy?

2. Access Control:
   - What is the process for granting system access?
   - How are access rights reviewed?
   - What is our MFA implementation?

3. Incident Response:
   - What is our incident response procedure?
   - Who should be contacted in case of a breach?
   - What is our recovery time objective?

4. Compliance:
   - Are we SOC2 compliant?
   - How do we maintain HIPAA compliance?
   - What security certifications do we have?

5. Technical Security:
   - How often are penetration tests conducted?
   - What encryption standards do we use?
   - How are backups managed?

6. Vendor Management:
   - How do we assess vendor security?
   - What is our third-party risk assessment process?
   - How often are vendor reviews conducted?

7. Training and Awareness:
   - What security training is required?
   - How often is security awareness training conducted?
   - How do we track training compliance?

8. Physical Security:
   - What physical security measures are in place?
   - How is visitor access managed?
   - How are assets physically secured?

9. Network Security:
   - What firewall rules are in place?
   - How is remote access secured?
   - What network monitoring tools are used?

10. Data Protection:
    - How is sensitive data classified?
    - What DLP measures are in place?
    - How is data encrypted at rest and in transit?
"""

def check_ollama_health():
    """Check if Ollama is running and the model is available"""
    try:
        llm = Ollama(model="llama2", timeout=60)  # Increased timeout
        # Simple test prompt
        response = llm.complete("Test")
        return True
    except Exception as e:
        logger.error(f"Ollama health check failed: {str(e)}")
        return False

def initialize_models():
    """Initialize LLM and embedding models with proper error handling"""
    try:
        # Initialize with optimized settings
        Settings.llm = Ollama(
            model="llama2",
            timeout=120,
            temperature=0.3,
            context_window=2048,  # Reduced from 4096 for better speed
            request_timeout=120.0,
            num_retries=3,
            base_url="http://localhost:11434",
        )
        
        return True
    except Exception as e:
        logger.error(f"Model initialization failed: {str(e)}")
        return False

def load_documents(input_dir):
    """Load and index documents with error handling"""
    try:
        documents = SimpleDirectoryReader(
            input_dir=input_dir,
            filename_as_id=True,
            file_extractor={".pdf": PDFReader()}
        ).load_data()
        
        logger.info(f"Loaded {len(documents)} documents")
        return documents
    except Exception as e:
        logger.error(f"Document loading failed: {str(e)}")
        return None

def create_index(documents):
    """Create and save the vector index"""
    try:
        # Load environment variables
        load_dotenv()

        # Create embedding model
        embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",  # or "text-embedding-ada-002" for older version
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Create LLM
        llm = OpenAI(
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Configure both embedding model and LLM
        Settings.embed_model = embed_model
        Settings.llm = llm

        # Create index
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist("./storage")
        return index
    except Exception as e:
        logger.error(f"Index creation failed: {str(e)}")
        return None

def query_index(index, query_text):
    """Query the index and return response"""
    try:
        # Create query engine with response synthesis
        query_engine = index.as_query_engine(
            response_mode="compact",  # or "tree_summarize" for longer responses
            streaming=False
        )
        response = query_engine.query(query_text)
        return response
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        return None

def main():
    # Check if Ollama is running
    if not check_ollama_health():
        logger.error("Ollama is not running or not responding. Please start Ollama first.")
        sys.exit(1)

    # Initialize models
    if not initialize_models():
        logger.error("Failed to initialize models. Exiting.")
        sys.exit(1)

    # Load documents
    documents = load_documents("/Users/dakshinsiva/final_RAG/docs")
    if not documents:
        logger.error("Failed to load documents. Exiting.")
        sys.exit(1)

    # Create index
    index = create_index(documents)
    if not index:
        logger.error("Failed to create index. Exiting.")
        sys.exit(1)

    # Interactive query loop with better error handling
    while True:
        try:
            query = input("\nEnter your security documentation question (or 'quit' to exit): ")
            if query.lower() == 'quit':
                break

            logger.info("Processing query...")
            response = query_index(index, query)
            
            # Display results with source attribution
            print("\nAnswer:")
            print(response.response)
            print("\nSources:")
            for node in response.source_nodes:
                print(f"\nFrom document: {node.node.metadata.get('file_name', 'Unknown')}")
                print(f"Relevance score: {node.score:.2f}")
                print("Relevant excerpt:")
                print(f"'{node.node.text[:200]}...'")  # Show first 200 chars of context

        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            print("An error occurred. Please try again.")

if __name__ == "__main__":
    main()
