# Security Documentation Query System Documentation

## Overview
This Python script implements a document querying system specifically designed for security and compliance documentation. It uses LlamaIndex with Ollama for local LLM processing and HuggingFace embeddings for document vectorization.

## Prerequisites
- Ollama installed and running locally
- Python 3.x
- Required Python packages:
  - llama_index
  - huggingface_hub
  - logging
  - PyPDF2 (for PDF processing)

## Core Components

### 1. Model Initialization
The system uses two main models:
- Local LLM via Ollama for text processing and response generation
- HuggingFace embeddings for document vectorization

### 2. Document Processing
- Supports multiple document formats including PDF, TXT, and DOCX
- Automatically extracts text content and metadata
- Creates vector embeddings for efficient searching

### 3. Query Processing
- Takes natural language queries about security documentation
- Uses vector similarity to find relevant document sections
- Generates contextual responses using the LLM

### 4. Analysis Tools
- Response analyzer for identifying patterns in security questionnaire responses
- Categorization of responses by security domain
- Identification of gaps in documentation

## Usage

### Basic Query
