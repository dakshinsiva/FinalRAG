import logging
from typing import Dict, List, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os

logger = logging.getLogger(__name__)

class SectionReferenceTracker:
    def __init__(self, docs_directory: str):
        self.docs_directory = docs_directory
        self.section_map: Dict[str, List[Tuple[str, int]]] = {}  # Maps keywords to [(document_name, page_number)]
        
    def process_documents(self):
        """Process all PDF documents and create section references"""
        try:
            for filename in os.listdir(self.docs_directory):
                if filename.endswith('.pdf'):
                    pdf_path = os.path.join(self.docs_directory, filename)
                    self._process_single_document(filename, pdf_path)
            
            logger.info(f"Processed documents and created {len(self.section_map)} section references")
        except Exception as e:
            logger.error(f"Error processing documents: {str(e)}")
            raise

    def _process_single_document(self, filename: str, filepath: str):
        """Process a single PDF document and extract section references"""
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        
        for page in pages:
            page_number = page.metadata.get('page', 0) + 1  # 1-based page numbering
            content = page.page_content.lower()
            
            # Look for common section indicators
            self._find_sections(content, filename, page_number, [
                "vulnerability assessment",
                "database security",
                "system security",
                "identity and access management",
                "backup management",
                "logging and monitoring",
                "patch management",
                "key rotation",
                "vpc and subnet",
                "configuration review",
                "architecture review",
                "perimeter security",
                "hosting",
                "data records"
            ])

    def _find_sections(self, content: str, filename: str, page_number: int, keywords: List[str]):
        """Find sections based on keywords and store references"""
        for keyword in keywords:
            if keyword.lower() in content:
                if keyword not in self.section_map:
                    self.section_map[keyword] = []
                self.section_map[keyword].append((filename, page_number))

    def get_reference(self, question: str) -> List[Tuple[str, int]]:
        """Get document references for a specific question"""
        relevant_sections = []
        question_lower = question.lower()
        
        for section, references in self.section_map.items():
            if section in question_lower:
                relevant_sections.extend(references)
        
        return list(set(relevant_sections))  # Remove duplicates

    def format_reference(self, references: List[Tuple[str, int]]) -> str:
        """Format references into a readable string"""
        if not references:
            return "No specific section reference found"
            
        formatted_refs = []
        for doc, page in references:
            formatted_refs.append(f"Document: {doc}, Page: {page}")
        return "\n".join(formatted_refs)

def main():
    """Example usage"""
    try:
        docs_path = "/Users/dakshinsiva/final_RAG/docs"
        tracker = SectionReferenceTracker(docs_path)
        tracker.process_documents()
        
        # Example question
        question = "Vulnerability Management Procedure and VA Reports"
        references = tracker.get_reference(question)
        print(f"\nQuestion: {question}")
        print("References:")
        print(tracker.format_reference(references))
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
