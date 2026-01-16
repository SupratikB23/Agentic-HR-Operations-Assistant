# HR Operations Enterprise Assistant

## Overview

The **HR Operations Enterprise Assistant** is an agentic, terminal-based NLP system designed to answer complex HR policy queries and execute HR-related actions in a reliable, enterprise-safe manner. The system follows a **policy-first and execution-safe design**, ensuring informational answers are grounded in source documents while actions are emitted as strict, machine-readable JSON.

The assistant uses **Retrieval-Augmented Generation (RAG)** to parse and reason over large, unstructured enterprise documents (such as annual reports and HR policy PDFs). It cleanly separates **policy interpretation** from **action execution**, preventing hallucinations in critical workflows like leave applications or HR requests.

This project is built for enterprise realism, robustness under rate limits, and demo safety.

---

## Key Capabilities

- **Terminal-Based Agentic Interface (`cli.py`)**  
  A controlled, interactive CLI designed for sequential, human-paced usage. It includes built-in cooldowns, duplicate query protection, and graceful fallback behavior to avoid API abuse and rate-limit failures.

- **Hybrid Intent Classification**  
  Automatically routes user input into one of three execution paths:
  - **Policy / Informational**: Citation-backed answers using RAG  
  - **Action**: Deterministic JSON outputs for HR workflows  
  - **Comparative**: Analytical queries involving trends or differences  

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



