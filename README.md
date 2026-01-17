# HR Operations Enterprise Assistant

## Overview

The **HR Operations Enterprise Assistant** is an agentic, terminal-based NLP system designed to answer complex HR policy queries and execute HR-related actions in a reliable, enterprise-safe manner. The system follows a **policy-first and execution-safe design**, ensuring informational answers are grounded in source documents while actions are emitted as strict, machine-readable JSON.

The assistant uses **Retrieval-Augmented Generation (RAG)** to parse and reason over large, unstructured enterprise documents (such as annual reports and HR policy PDFs). It cleanly separates **policy interpretation** from **action execution**, preventing hallucinations in critical workflows like leave applications or HR requests.

---

## Key Capabilities

- **Terminal-Based Agentic Interface (`cli.py`)**  
  A controlled, interactive CLI designed for sequential, human-paced usage. It includes built-in cooldowns, duplicate query protection, and graceful fallback behavior to avoid API abuse and rate-limit failures.

- **Hybrid Intent Classification**  
  Automatically routes user input into one of three execution paths:
  - **Policy / Informational**: Citation-backed answers using RAG  
  - **Action**: Deterministic JSON outputs for HR workflows  

- **Enterprise-Grade RAG Pipeline**  
  Large PDF documents are ingested, chunked, embedded, and indexed using **FAISS**, enabling accurate semantic retrieval across hundreds of pages.

- **Strict Action Contracts**  
  All HR actions are returned as **pure JSON only**, never prose. This enforces a clean contract suitable for downstream automation or HRMS integration.

- **Resilient LLM Integration with Offline Fallback**  
  The system integrates with OpenRouter-hosted LLMs (e.g., Mistral/Gemma) for synthesis, but automatically falls back to a **rule-based offline extraction mode** when APIs are unavailable or rate-limited.

---

## Supported Agentic HR Actions

- Apply for leave  
- Schedule a meeting with HR  
- Create an HR support ticket  
- Check leave eligibility  
- Retrieve leave balance  
- Escalate issues to human HR  

Each action is triggered via natural language and resolved into a deterministic JSON payload.

---

## Project Structure

```text
.
├── cli.py                          # Main terminal-based interface
├── run_hr_agent.py                 # Script for batch / test execution
├── FULL-Annual-Report-2024-25.pdf  # Source document for RAG
└── HR Agent/
    ├── nlp_agent.py                # Central agent orchestrator
    ├── knowledge_base.py           # PDF ingestion and FAISS indexing
    ├── intent_classifier.py        # Intent routing logic
    ├── action_engine.py            # HR action → JSON generation
    ├── llm_interface.py            # LLM + offline fallback handler
    └── config.py                   # Configuration and API keys
```

## Setup & Installation

### Prerequisites

- Python 3.8 or higher  
- Required Python packages:
  ```bash
  pip install openai langchain faiss-cpu pypdf numpy

## Configuration

The system supports both online (LLM-backed) and offline execution modes.

### API Key Setup

Set your OpenRouter / OpenAI API key in either of the following ways:

#### Option 1: Environment Variable (Recommended)

```bash
export OPENAI_API_KEY="sk-..."
```
#### Option 2: onfiguration File
Add the key directly in:
```bash
HR Agent/config.py
OPENAI_API_KEY = "sk-..."
```

### Offline Mode

If no API key is provided, or if the LLM service becomes unavailable or rate-limited, the system automatically switches to **Offline Mode**.

In Offline Mode:

- No external API calls are made  
- Answers are generated using document-grounded extraction logic  
- The system remains fully functional for demos and testing  

This design ensures enterprise-grade resilience and predictable behavior.


---
## Data Ingestion

The HR Operations Enterprise Assistant uses a structured **Retrieval-Augmented Generation (RAG)** ingestion pipeline to process large, complex enterprise documents such as annual reports and HR policy manuals.

Source documents are ingested in their raw PDF form and processed at startup to create a searchable knowledge base that preserves contextual meaning and page-level traceability.

### Ingestion Workflow

- **PDF Loading**  
  The system loads the source document (e.g., Annual Report / HR Policy PDF) from the project root directory.

- **Page-Level Text Extraction**  
  Text is extracted on a per-page basis to retain accurate page references for citation and explainability.

- **Content Cleaning & Normalization**  
  Extracted text is cleaned, normalized, and prepared for semantic processing.

- **Semantic Chunking**  
  The document is divided into logically meaningful text chunks to balance context preservation and retrieval efficiency.

- **Embedding Generation**  
  Vector embeddings are generated for each chunk using a sentence-level embedding model.

- **Vector Indexing (FAISS)**  
  All embeddings are indexed using FAISS to enable fast and accurate semantic similarity search during query execution.

This ingestion process allows the assistant to retrieve precise, context-aware information from documents spanning hundreds of pages while maintaining citation accuracy and minimizing hallucination.

---

## Usage

The HR Operations Enterprise Assistant is designed to be used through a **terminal-based interface**, ensuring controlled, sequential interaction and stable execution under rate-limited environments.

The CLI provides a simple yet powerful way for users to ask HR-related questions or issue action-oriented commands using natural language.

### Interactive CLI

- Launch the assistant by running the CLI entry point.
- Users can type queries directly into the terminal.
- Each query is processed individually to avoid concurrency issues and API abuse.

### Example Interactions

Users can ask informational or policy-based questions such as:
- *What is the dividend distribution policy?*
- *Am I eligible for maternity leave?*

They can also issue action-oriented commands such as:
- *Apply for earned leave next Monday*
- *Schedule a meeting with HR*

---

## System Architecture (High-Level Flow)

The HR Operations Enterprise Assistant follows a **modular, agentic architecture** designed to ensure clarity, safety, and enterprise-grade reliability. Each stage in the pipeline has a well-defined responsibility, enabling explainable reasoning and controlled execution.

### Execution Pipeline

- **Input Capture**  
  User input is captured via the terminal-based CLI and forwarded to the agent orchestrator for processing.

- **Intent Classification**  
  The query is analyzed to determine the user’s intent, categorizing it as:
  - Policy / Informational
  - Action
  - Comparative

- **Context Retrieval (RAG)**  
  For informational and policy queries, relevant document chunks are retrieved from the vector store using semantic similarity search, preserving page-level traceability.

- **Reasoning & Synthesis**  
  Retrieved context is injected into the reasoning layer, where the system synthesizes a grounded response using an LLM or offline extraction logic.

- **Action Execution Path**  
  When an action intent is detected, the system bypasses natural language synthesis and invokes the action engine to construct a deterministic JSON payload.

- **Output Normalization**  
  The final response is normalized before display:
  - Natural language answers for informational queries
  - Raw, machine-readable JSON for action requests

This architecture enforces a strict separation between reasoning and execution, minimizing hallucination risk while enabling agentic workflow behavior.

