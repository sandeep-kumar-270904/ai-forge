# System Requirements

This document outlines the core functional capabilities the AIForge system is designed to fulfill.

1.  **REQ-001 (Gateway):** The system shall provide a unified endpoint for querying multiple Large Language Model providers.
2.  **REQ-002 (Prompting):** The system shall allow version-controlled storage of prompt templates.
3.  **REQ-003 (Swarms):** The system shall orchestrate multiple distinct AI agents passing messages to each other sequentially.
4.  **REQ-004 (Security):** The system shall intercept execution graphs before high-risk tools are executed and require explicit HTTP authorization to proceed.
5.  **REQ-005 (Privacy):** The system shall mask Personally Identifiable Information (PII) before persisting LLM logs to the database.
6.  **REQ-006 (Testing):** The system shall provide a framework to score agent outputs against expected outcomes using LLM-as-a-Judge.
