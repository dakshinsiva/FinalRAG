import os
import base64
import io
import logging
from pdf2image import convert_from_path
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Optional, Union
import json
import datetime
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
import asyncio
import time
import re
from collections import defaultdict
import numpy as np
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define SecurityChecker class
class SecurityChecker:
    def scan(self, file_path: str) -> bool:
        # Implement security check logic here
        return True

class SecurityQuestionnaire:
    def __init__(self):
        # Define sections first
        self.sections = {
            "vulnerability_management": "Vulnerability Assessment and Management",
            "configuration_security": "Configuration and Security Controls",
            "database_security": "Database Security",
            "system_security": "System Security",
            "iam": "Identity and Access Management",
            "backup": "Backup and Recovery",
            "monitoring": "Monitoring and Logging",
            "infrastructure": "Infrastructure Security",
            "1B_questionnaire": "Security Assessment Questionnaire"
        }

        # Define questions as before
        self.questions = {
            "vulnerability_management": {
                "VA_PT_reports": "What is your vulnerability assessment and penetration testing process?",
                "remediation_status": "How do you track and manage remediation of security findings?",
                "security_reporting_sources": "What are your security reporting and monitoring sources?"
            },
            "configuration_security": {
                "ssl_certificate": "Describe your SSL/TLS certificate management process",
                "object_versioning": "How is object versioning implemented?",
                "encryption": "What encryption methods are used for data at rest and in transit?",
                "public_access": "How is public access to resources controlled?",
                "masking_mechanism": "What data masking mechanisms are in place?",
                "data_storage_location": "Where is sensitive data stored?",
                "key_storage": "How are encryption keys managed and stored?",
                "deletion_protection": "What deletion protection measures are in place?",
                "auto_healing": "Describe your auto-healing capabilities",
                "iam_configuration": "Detail your IAM configuration and policies"
            },
           
            
            "1B_questionnaire": {
                "outsourcing_nature": "What is the nature of process/service to be outsourced?",
                "spii_access": "Does the process/service/solution involve accessing or processing of SPII data of ABC's or Intellectual property (e.g. trade secrets, trademark, patents etc. ) details?",
                "spii_sharing": "Does the process/service/solution involve Sharing of SPII data of ABC's or Intellectual property (e.g. trade secrets, trademark, patents etc. ) details?",
                "spii_storage": "Does the process/service/solution involve storing of SPII data of ABC's or Intellectual property (e.g. trade secrets, trademark, patents etc. ) details?",
                "pii_access": "Does the process/service/solution involve accessing or processing of PII data of ABC customers or employees?",
                "pii_sharing": "Does the process/service/solution involve sharing of ABC customers' or employees' PII data?",
                "pii_storage": "Does the process/service/solution involve storing of ABC customers' or employees' PII data on the third party systems?",
                "business_critical_access": "Does the process/service/solution involve accessing or processing of ABC's business critical / confidential data (e.g. financial / Market research data)?",
                "business_critical_sharing": "Does the process/service/solution involve sharing of ABC's business critical / confidential data (e.g. Financial / Market research data)?",
                "business_critical_storage": "Does the process/service/solution involve storing of ABC's critical / confidential data (e.g. financial / Market research data) on third party systems?",
                "pii_records": "How many customers' or employees' PII/ SPI records will be accessed, processed, or shared for this process?",
                "data_origin": "At which location(s) will the data be originated?",
                "cross_border_transfer": "Does this process/service/solution involve cross-border transfer(sending data outside the country) of data?",
                "network_access": "Does the process/service/solution require access to ABC's internal network?",
                "network_access_level": "What level of network access will be required for this process/service/solution?",
                "remote_transfer": "Does the process/service/solution require transfer of ABC's confidential information or PII/SPI data via remote mechanism?",
                "business_disruption": "Would there be significant disruption to ABC's business operation if this process/service/solution stops abruptly?",
                "customer_impact": "Would the sudden failure of this process/service/solution impact ABC's customers?",
                "restoration_impact": "If the time required to restore the service/process is more than 24 hours, would there be a negative impact to ABC?",
                "brand_harm": "Would the process/service/solution failure cause significant harm to ABC's brand or reputation?",
                "revenue_impact": "Would the sudden failure of this process/service/solution impact ABC's revenue?",
                "regulatory_risk": "Would ABC be subjected to regulatory review, enforcement actions, or fines if there is a failure or interruption of the process/service/solution?",
                "local_regulations": "Is the process/service/solution subjected to local regulations / jurisdictions as a result of cross-border operations in multiple regions?"
            },
            "2a_vendor_selection": {
                "services_provided": "What services are provided by the vendor to ABC?",
                "data_access": "Which ABC data would you need access to (Personally identifiable information (PII) or SPII data or Business critical / confidential data (e.g. financial / business research data) or Intellectual property (e.g. trade secrets, trademark, patents etc)). Please select all the data classification you have access to",
                "data_storage": "Would you store any ABC data?",
                "payment_card_info": "Do you process/store payment card information data?",
                "data_storage_location_geo": "Where will you store the ABC data - Geographically?",
                "data_storage_location": "Where will you store the ABC data?",
                "iso_27001": "Is the vendor processing centre ISO 27001 (Information Security Management System- ISMS)?",
                "iso_22301": "Is the vendor processing centre ISO 22301 (Business continuity)?",
                "pci_dss": "Is the vendor processing centre PCI DSS compliant?",
                "soc_compliance": "Is the vendor processing centre SOC 1 or SOC 2 compliant?",
                "info_security_policy": "Does your organisation have Information Security Policy in line with industry best practices such as ISO27001 standard and has this been reviewed in the last 12 months?",
                "data_privacy_policy": "Does your organisation have data privacy policy and has this been reviewed in the last 12 months?",
                "security_team": "Do you have a Information security team?",
                "vulnerability_management": "Does your organisation have a Vulnerability Management and Penetration testing program that ensures that application vulnerabilities are addressed in a timely manner?",
                "logging_monitoring": "Do you have logging and monitoring enabled on all your information processing systems and maintain the logs securely for a rolling period of 180 days?",
                "security_operations": "Do you have a security operations centre and SIEM technology?",
                "endpoint_security": "Do you have end point security solutions implemented (Anti-virus and DLP)?",
                "threat_intelligence": "Do you have threat intelligence tools or controls implemented?",
                "application_security": "Do you perform application security assessments as per OWASP standards?",
                "network_monitoring": "Do you have network perimeter monitoring devices such as IDS/ IPS/ Next generation firewall/ application firewall/ proxy?",
                "usage_policy": "Do you have an acceptable usage policy which restricts printing of confidential information?",
                "data_retention_policy": "Do you have a data retention and disposal policy?",
                "idam_solution": "Do you have an Identity access management solution (IDAM) for normal user IDs?",
                "pim_pam_solution": "Do you have a privileged identity access management solution (PIM/ PAM) for privileged user IDs?",
                "user_access_review": "Do you perform a user access review for normal and privileged user IDs?",
                "change_management": "Do you have a change management policy in place?",
                "backup_restoration": "Do you have a data backup and restoration process?",
                "data_encryption": "Do you use data encryption/ cryptography?",
                "cyber_crisis_management": "Do you have a cyber crisis notification and management process?",
                "patch_management": "Do you have patch management process?",
                "breach_history": "Please mark no if you have been breached in last 12 months?",
                "physical_security": "Do you have physical security and environmental controls such as CCTV monitoring equipment security, physical ID and access cards, etc.?",
                "cloud_security_policy": "Do you have a cloud security policy?",
                "data_controls": "Do you have controls implemented for data at rest and data in transit?",
                "security_awareness": "Do you have a security awareness program for your employees, part-timers?",
                "cmdb_asset_discovery": "Do you use CMDB and asset discovery tool?",
                "business_continuity_policy": "Is there a Business Continuity policy, IT Disaster Recovery policy (and supporting documentation) which maintained, reviewed and signed off in the last 12 months?"
            },
            "3b_access_form": {
                "product_service_description": "Describe the product or service to be provided",
                "third_party_access_type": "Classify the type of third party access:\n(Service Provider\nManaged Services\nCustomer Access\nOutsourcing\nAuditor\nConsultant\nDeveloper\nCleaning/Catering/Support services\nTemp/Work Experience/Student Placement)",
                "systems_applications_access": "What systems or applications are to be accessed logically – if any?",
                "site_access": "Will the third party require access to the ABC site?",
                "computer_room_access": "Will the third party require access to the ABC computer room?",
                "remote_access": "Will the third party require Remote Access – if so describe how this will be achieved?",
                "sensitive_info_access": "Will the third party require access to any sensitive or confidential information – if so describe.",
                "personnel_count": "How many personnel from the third party will require access?",
                "third_party_contacts": "Who is the/are the key contacts at the third party (provide email addresses/telephone numbers)?",
                "sponsor_contact": "Which Aggregate employee or contact will sponsor the access?",
                "access_duration": "How long is the access required for?",
                "asset_requirements": "Does the third party require any Aggregate owned assets?",
                "service_continuity_impact": "Does this third party access have any impact on IT service continuity?",
                "it_stakeholders": "Identify any key contacts or stakeholders in IT related to this third party access.",
                "business_stakeholders": "Identify any key contacts or stakeholders in the business related to this third party access.",
                "legal_regulatory_impact": "Is there any identified legal or regulatory impact?",
                "contract_status": "Is there a valid and signed contract or MSA signed with the vendor organization?",
                "nda_status": "Are the NDA and Confidentiality Agreements signed by the vendor?"
            }
        }

    def get_section_name(self, section_key):
        """Get the friendly name of a section"""
        return self.sections.get(section_key, section_key)

    def get_questions_by_section(self, section_key):
        """Get all questions for a specific section"""
        return self.questions.get(section_key, {})

class VisionProcessor:
    def __init__(self):
        """Initialize Vision Processor with OpenAI client"""
        try:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg']
            self.questionnaire = SecurityQuestionnaire()
        except Exception as e:
            logger.error(f"Failed to initialize VisionProcessor: {str(e)}")
            raise

    def convert_pdf_to_images(self, pdf_path: str) -> List[str]:
        """Convert PDF pages to base64 encoded images"""
        try:
            images = convert_from_path(pdf_path)
            base64_images = []
            
            for img in images:
                # Optimize image size while maintaining readability
                img = img.resize((2000, int(2000 * img.size[1] / img.size[0])))
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=85)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                base64_images.append(img_str)
            
            return base64_images
        except Exception as e:
            logger.error(f"PDF conversion failed for {pdf_path}: {str(e)}")
            return []

    def analyze_document(self, image_data: str, query: Optional[str] = None) -> Dict:
        """Analyze document using GPT-4 Vision API"""
        try:
            # Enhanced system prompt for better accuracy
            system_prompt = """You are an expert CISO advisor analyzing security documentation. 
            Provide detailed, accurate analysis with specific references to the document content.
            Focus on:
            1. Security controls and policies - cite specific configurations
            2. Compliance requirements - reference specific standards
            3. Risk assessments - provide quantitative measures where possible
            4. Technical configurations - include exact settings
            5. Security metrics and KPIs - quote specific numbers
            6. Incident response procedures - detail exact steps
            7. Data protection measures - specify encryption methods and standards
            
            Always ground your analysis in visible evidence from the document.
            If information is unclear or missing, explicitly state this."""

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "high"  # Using highest detail level
                            }
                        }
                    ]
                }
            ]

            # Add specific query if provided
            if query:
                messages[1]["content"].append({
                    "type": "text",
                    "text": query
                })

            # Using GPT-4 Turbo with Vision for best performance
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",  # Latest vision model
                messages=messages,
                max_tokens=4096,  # Maximum context
                temperature=0.1,   # Lower temperature for more focused responses
                top_p=0.95,       # Slightly constrained sampling
                presence_penalty=0.0,  # Neutral presence penalty
                frequency_penalty=0.1   # Slight penalty for repetition
            )
            
            return {
                'content': response.choices[0].message.content,
                'usage': response.usage.total_tokens
            }

        except Exception as e:
            logger.error(f"GPT-4 Vision analysis failed: {str(e)}")
            return {'error': str(e)}

    def process_security_document(self, file_path: str, custom_query: Optional[str] = None) -> Dict:
        """Process a security document and extract relevant information"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_ext}")

            results = {
                'file_name': os.path.basename(file_path),
                'analysis': [],
                'summary': {},
                'metadata': {
                    'file_path': file_path,
                    'file_type': file_ext,
                    'processing_date': datetime.now().isoformat()
                }
            }

            if file_ext == '.pdf':
                base64_images = self.convert_pdf_to_images(file_path)
                for idx, image in enumerate(base64_images):
                    analysis = self.analyze_document(image, custom_query)
                    if 'error' not in analysis:
                        analysis['page_number'] = idx + 1
                        results['analysis'].append(analysis)
            else:
                # Handle single image files
                with open(file_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    analysis = self.analyze_document(img_data, custom_query)
                    if 'error' not in analysis:
                        results['analysis'].append(analysis)

            # Generate summary if we have valid analyses
            if results['analysis']:
                results['summary'] = self._generate_summary(results['analysis'])

            return results

        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            return {'error': str(e)}

    def _generate_summary(self, analyses: List[Dict]) -> Dict:
        """Generate a summary of all analyses"""
        try:
            combined_content = "\n".join([a['content'] for a in analyses])
            
            summary_prompt = """Synthesize the key security findings with high precision:
            1. Critical Security Controls - list specific implementations
            2. Compliance Requirements - cite specific standards and gaps
            3. Key Risks - quantify impact and likelihood
            4. Recommended Actions - prioritized and actionable
            5. Important Metrics - include specific numbers and thresholds
            
            Format your response with clear sections and bullet points.
            Include confidence levels for each finding."""

            response = self.client.chat.completions.create(
                model="gpt-4-1106-preview",  # Latest GPT-4 Turbo model
                messages=[
                    {"role": "system", "content": "You are a CISO advisor creating precise, evidence-based executive summaries."},
                    {"role": "user", "content": f"{summary_prompt}\n\nDocument Content:\n{combined_content}"}
                ],
                temperature=0.1,  # Very low temperature for consistency
                max_tokens=4096,  # Maximum context
                top_p=0.95,
                presence_penalty=0.0,
                frequency_penalty=0.1
            )

            return {
                'executive_summary': response.choices[0].message.content,
                'total_pages': len(analyses),
                'total_tokens_used': sum(a.get('usage', 0) for a in analyses),
                'model_version': 'gpt-4-1106-preview'
            }

        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return {'error': str(e)}

    def batch_process_directory(self, directory_path: str) -> Dict:
        """Process all supported documents in a directory"""
        try:
            results = {
                'processed_files': [],
                'failed_files': [],
                'summary': {}
            }

            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if os.path.splitext(filename)[1].lower() in self.supported_formats:
                    logger.info(f"Processing {filename}")
                    result = self.process_security_document(file_path)
                    
                    if 'error' in result:
                        results['failed_files'].append({
                            'file': filename,
                            'error': result['error']
                        })
                    else:
                        results['processed_files'].append(result)

            # Generate overall summary if files were processed
            if results['processed_files']:
                all_summaries = [f['summary'].get('executive_summary', '') 
                               for f in results['processed_files']]
                results['summary'] = self._generate_summary(all_summaries)

            return results

        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            return {'error': str(e)}

    def analyze_security_questionnaire(self, image_data: str) -> Dict:
        """Analyze security questionnaire using GPT-4 Vision API"""
        try:
            system_prompt = """You are a security compliance expert analyzing a security questionnaire. 
            For each question, provide:
            1. A detailed answer based on the evidence visible in the document
            2. Required screenshots or configurations needed
            3. Compliance implications (if any)
            4. Risk level (High/Medium/Low)
            5. Recommended actions if information is missing

            Format your response as a structured JSON with the following sections:
            - question_id
            - question_text
            - answer
            - required_evidence
            - compliance_impact
            - risk_level
            - recommendations
            """

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "text",
                            "text": "Please analyze this security questionnaire and provide detailed responses for each question following the specified format."
                        }
                    ]
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=4096,
                temperature=0.2
            )
            
            # Parse and structure the response
            return self._structure_questionnaire_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Security questionnaire analysis failed: {str(e)}")
            return {'error': str(e)}

    def _structure_questionnaire_response(self, content: str) -> Dict:
        """Structure the questionnaire response into categories"""
        try:
            # Parse the JSON response
            parsed_content = json.loads(content)
            
            # Organize by categories
            structured_response = {
                'vulnerability_management': {},
                'configuration_security': {},
                'access_management': {},
                'security_tools': {},
                'infrastructure': {},
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'total_questions': len(parsed_content),
                    'completion_status': 'complete'
                }
            }

            # Categorize each response
            for item in parsed_content:
                category = self._determine_question_category(item['question_text'])
                if category:
                    structured_response[category][item['question_id']] = item

            return structured_response
        except Exception as e:
            logger.error(f"Response structuring failed: {str(e)}")
            return {'error': str(e)}

    def _determine_question_category(self, question_text: str) -> str:
        """Determine the category of a question based on its content"""
        # Implementation of categorization logic
        pass

    def generate_evidence_checklist(self, analysis_results: Dict) -> Dict:
        """Generate a checklist of required evidence"""
        try:
            evidence_checklist = {
                'screenshots_required': [],
                'configurations_required': [],
                'documents_required': [],
                'access_reviews_required': []
            }

            # Parse through analysis results and compile required evidence
            for category in analysis_results:
                if isinstance(analysis_results[category], dict):
                    for question_id, details in analysis_results[category].items():
                        if 'required_evidence' in details:
                            for evidence in details['required_evidence']:
                                evidence_type = self._determine_evidence_type(evidence)
                                evidence_checklist[f"{evidence_type}_required"].append({
                                    'question_id': question_id,
                                    'evidence_description': evidence,
                                    'status': 'pending'
                                })

            return evidence_checklist
        except Exception as e:
            logger.error(f"Evidence checklist generation failed: {str(e)}")
            return {'error': str(e)}

    def format_answer(self, section, question_id, question, answer, sources, references):
        formatted_response = []
        
        # Add section header if it's the first question in the section
        if self._is_first_question_in_section(section, question_id):
            formatted_response.extend([
                f"\n{section.upper().replace('_', ' ')}",
                "=" * len(section),
                "\n"
            ])
        
        # Format question
        formatted_response.extend([
            f"Question: {question}\n",
            f"Answer: {answer}\n\n"
        ])
        
        # Format sources
        formatted_response.extend([
            "Source Documents:",
            "-" * 20
        ])
        for source in sources:
            formatted_response.append(f"• {os.path.basename(source)}")
        formatted_response.append("\n")
        
        # Format references if available
        if references:
            formatted_response.extend([
                "Relevant Sections:",
                "-" * 20
            ])
            for ref in references:
                formatted_response.extend([
                    f"• File: {os.path.basename(ref['file'])}, Page: {ref['page']}",
                    "  Context Preview:",
                    f"  {ref['preview'].strip()}\n"
                ])
        
        # Add separator
        formatted_response.extend([
            "-" * 80,
            "\n"
        ])
        
        return "\n".join(formatted_response)

    def format_response(self, section, question, answer, sources):
        """Format a single response in a clean, well-formatted Q&A format"""
        section_header = f"\n{'=' * 80}\n{section.upper().replace('_', ' ')}\n{'=' * 80}\n"
        
        formatted_output = [
            section_header,
            "📝 Question:",
            f"{question}\n",
            "🔍 Answer:",
            f"{answer}\n",
            "📚 Source Document:",
            f"• {os.path.basename(sources[0]) if sources else 'No source document'}\n",
            f"{'_' * 80}\n"  # Subtle separator between QA pairs
        ]
        
        return "\n".join(formatted_output)

    def interactive_qa_session(self):
        """Interactive Q&A session with GPT-4"""
        print("\n=== Security Documentation Q&A System (GPT-4) ===")
        print("Type 'exit' or 'quit' to end the session\n")
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        output_file = f'Best_model_results_{timestamp}.txt'
        
        # Initialize conversation history
        conversation_history = [
            {
                "role": "system",
                "content": """You are an expert security analyst assistant. 
                Analyze security documentation and provide detailed, accurate answers.
                Always cite specific evidence from the documents when available.
                If information is not available or unclear, explicitly state this."""
            }
        ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            header = [
                "╔══════════════════════════════════════════════════════════════════════════════╗",
                "║                      Security Questionnaire Analysis                         ║",
                "║                                                                             ║",
                f"║  Generated: {timestamp.ljust(56)}║",
                "╚══════════════════════════════════════════════════════════════════════════════╝\n\n"
            ]
            f.write('\n'.join(header))
            
            while True:
                question = input("\nEnter your question: ").strip()
                
                if question.lower() in ['exit', 'quit']:
                    print("\nEnding Q&A session. Results saved to", output_file)
                    break
                
                if not question:
                    print("Please enter a valid question.")
                    continue
                
                try:
                    # Add user question to conversation
                    conversation_history.append({"role": "user", "content": question})
                    
                    # Get response from GPT-4
                    response = self.client.chat.completions.create(
                        model="gpt-4-1106-preview",  # Using latest GPT-4
                        messages=conversation_history,
                        temperature=0.1,
                        max_tokens=4096,
                        top_p=0.95
                    )
                    
                    answer = response.choices[0].message.content
                    
                    # Add assistant's response to conversation history
                    conversation_history.append({"role": "assistant", "content": answer})
                    
                    # Write to file
                    f.write("\n" + "=" * 80 + "\n")
                    f.write(question.upper() + "\n")
                    f.write("=" * 80 + "\n\n")
                    f.write("📝 Question:\n")
                    f.write(question + "\n\n")
                    f.write("🔍 Answer:\n")
                    f.write(answer + "\n\n")
                    f.write("📚 Source Document:\n")
                    f.write("• " + self._get_relevant_source() + "\n\n")
                    f.write("_" * 80 + "\n\n")
                    
                    # Display on console
                    print(f"\n🔍 Answer: {answer}\n")
                    
                except Exception as e:
                    error_msg = f"Error processing question: {str(e)}"
                    print(error_msg)
                    f.write(f"\nError: {error_msg}\n")
        
        def _get_relevant_source(self):
            """Helper method to get relevant source document"""
            # You can implement logic to find the most relevant source
            # For now, returning a placeholder
            return "Relevant policy document"

    

    def analyze_specificity(self, answer: str) -> float:
        """Analyze the specificity of an answer"""
        specific_patterns = [
            r'\d+',  # Numbers
            r'version \d+(\.\d+)*',  # Version numbers
            r'[A-Z]{2,}-\d+',  # Reference codes
            r'specific|precise|exact',  # Specific terms
        ]
        
        score = sum(bool(re.search(pattern, answer.lower())) for pattern in specific_patterns)
        return min(score / len(specific_patterns), 1.0)

    def analyze_source_citation(self, answer: str) -> float:
        """Analyze the source citation quality"""
        if '📚 Source Document:' not in answer:
            return 0.0
        
        source_section = answer.split('📚 Source Document:')[1]
        has_filename = bool(re.search(r'\.(pdf|doc|docx|txt)\'?', source_section))
        has_date = bool(re.search(r'\d{4}', source_section))
        
        return (has_filename + has_date) / 2

    def analyze_completeness(self, answer: str) -> float:
        """Analyze the completeness of an answer"""
        word_count = len(answer.split())
        sentences = len(re.split(r'[.!?]+', answer))
        
        # Normalize scores
        word_score = min(word_count / 100, 1.0)
        sentence_score = min(sentences / 5, 1.0)
        
        return (word_score + sentence_score) / 2

    def analyze_technical_depth(self, answer: str) -> float:
        """Analyze the technical depth of an answer"""
        technical_terms = {
            'encryption', 'authentication', 'protocol', 'configuration',
            'implementation', 'security', 'compliance', 'monitoring',
            'access control', 'vulnerability', 'audit', 'firewall'
        }
        
        found_terms = sum(term in answer.lower() for term in technical_terms)
        return min(found_terms / len(technical_terms), 1.0)


# Define SecurityQuestionnaireAnalyzer class
class SecurityQuestionnaireAnalyzer:
    def __init__(self, docs_path: str):
        self.docs_path = docs_path
        self.documents = []

    def load_documents(self):
        """Load documents from the specified directory."""
        try:
            for filename in os.listdir(self.docs_path):
                file_path = os.path.join(self.docs_path, filename)
                if os.path.isfile(file_path):
                    content = self._read_file_with_fallback(file_path)
                    if content:
                        self.documents.append(content)
            print(f"Loaded {len(self.documents)} documents.")
            return self.documents
        except Exception as e:
            logger.error(f"Failed to load documents: {str(e)}")
            raise

    def _read_file_with_fallback(self, file_path):
        """Attempt to read a file with multiple encodings."""
        encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        logger.error(f"Failed to decode file: {file_path}")
        return None

    # Add methods for analysis as needed
    def analyze(self):
        pass

def format_output_file():
    """Generate a formatted output filename with timestamp"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    return f"security_questionnaire_responses_{timestamp}.txt"

def write_formatted_results(results, questionnaire):
    """Write formatted results to both text and Word files"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    txt_output = f"security_questionnaire_responses_{timestamp}.txt"
    docx_output = f"security_questionnaire_responses_{timestamp}.docx"
    
    # Create Word document
    doc = Document()
    
    # Set up Word document style
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    
    # Add title to Word document
    title = doc.add_heading('Security Questionnaire Analysis', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add timestamp
    timestamp_para = doc.add_paragraph(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    timestamp_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()  # Add spacing
    
    # Write to both files
    with open(txt_output, 'w', encoding='utf-8') as f:
        # Write header with fancy border for text file
        f.write("╔══════════════════════════════════════════════════════════════════════════════╗\n")
        f.write("║                      Security Questionnaire Analysis                         ║\n")
        f.write("║                                                                             ║\n")
        f.write(f"║  Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                     ║\n")
        f.write("╚══════════════════════════════════════════════════════════════════════════════╝\n\n")

        # Write each section
        for section, questions in results['answers'].items():
            section_name = questionnaire.sections.get(section, section)
            
            # Section header for text file
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"{section_name.upper()}\n")
            f.write("=" * 80 + "\n\n")
            
            # Section header for Word document
            doc.add_heading(section_name.upper(), level=1)
            
            # Questions and answers
            for q_key, answer in questions.items():
                full_question = questionnaire.questions[section][q_key]
                
                # Write to text file
                f.write("📝 Question:\n")
                f.write(f"{full_question}\n\n")
                f.write("🔍 Answer:\n")
                f.write(f"{answer['result'] if isinstance(answer, dict) else answer}\n\n")
                
                # Write to Word document
                q_para = doc.add_paragraph()
                q_para.add_run("Question:\n").bold = True
                q_para.add_run(full_question)
                
                a_para = doc.add_paragraph()
                a_para.add_run("Answer:\n").bold = True
                a_para.add_run(answer['result'] if isinstance(answer, dict) else answer)
                
                # Handle source documents
                source_docs = []
                if isinstance(answer, dict) and 'source_documents' in answer:
                    source_docs = answer['source_documents']
                
                # Write sources to text file
                f.write("📚 Source Documents:\n")
                if source_docs:
                    for doc_ref in source_docs:
                        source = os.path.basename(doc_ref.metadata.get('source', '[Document reference]'))
                        page_num = doc_ref.metadata.get('page', 1)  # Get page number, default to 1
                        f.write(f"• {source} (Page {page_num})\n")
                else:
                    f.write("• [Document reference]\n")
                
                # Write sources to Word document
                s_para = doc.add_paragraph()
                s_para.add_run("Source Documents:\n").bold = True
                if source_docs:
                    for doc_ref in source_docs:
                        source = os.path.basename(doc_ref.metadata.get('source', '[Document reference]'))
                        page_num = doc_ref.metadata.get('page', 1)  # Get page number, default to 1
                        s_para.add_run(f"• {source} (Page {page_num})\n")
                else:
                    s_para.add_run("• [Document reference]")
                
                # Add separator in text file
                f.write("\n" + "_" * 80 + "\n\n")
                
                # Add separator in Word document
                doc.add_paragraph("_" * 80)
                doc.add_paragraph()  # Add spacing

    # Save Word document
    doc.save(docx_output)
    
    return txt_output, docx_output

def main():
    """Main function for RAG system"""
    try:
        # Initialize components
        document_loader = DirectoryLoader("/Users/dakshinsiva/final_RAG/docs", loader_cls=PyPDFLoader)
        documents = document_loader.load()
        
        # Split documents with smaller chunks for more precise page references
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Reduced from 1000 for more precise location tracking
            chunk_overlap=50, # Reduced overlap to minimize duplicate references
            add_start_index=True,
            separators=["\n\n", "\n", " ", ""] # More granular splitting
        )
        texts = text_splitter.split_documents(documents)
        
        # Create vector store
        vector_store = FAISS.from_documents(
            texts, 
            OpenAIEmbeddings()
        )
        
        # Initialize retriever with more specific search
        retriever = vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={
                "k": 4,  # Increased to get more context
                "include_metadata": True,
                "score_threshold": 0.5  # Only include relevant matches
            }
        )
        
        llm = ChatOpenAI(temperature=0)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            verbose=True  # Helpful for debugging
        )
        
        # Load questions
        questionnaire = SecurityQuestionnaire()
        
        # Process questions and get answers
        results = {
            'questions': questionnaire.questions,
            'sections': questionnaire.sections,
            'answers': {}
        }
        
        # Answer questions using RAG
        for section, questions in questionnaire.questions.items():
            results['answers'][section] = {}
            for key, question in questions.items():
                answer = qa_chain({"query": question})  # Changed from qa_chain.run()
                results['answers'][section][key] = answer

        # Write formatted results to both formats
        txt_file, docx_file = write_formatted_results(results, questionnaire)
        
        print(f"\nAnalysis complete!")
        print(f"Results saved to:")
        print(f"- Text file: {txt_file}")
        print(f"- Word document: {docx_file}")
        
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
