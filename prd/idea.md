# 🧾 Product Requirements Document (PRD)

## 📌 Title
LLM-Powered Intelligent Query–Retrieval System

## 🧠 Prepared For
HackRx 2025

## 1. 🎯 Problem Statement

Professionals in insurance, legal, HR, and compliance domains often deal with large, unstructured documents. Extracting relevant information from such documents requires domain knowledge, time, and manual effort.

## 2. ✅ Objective

To build an AI-powered system that:

- Ingests and understands large documents (PDFs, DOCX, emails)
- Allows users to ask natural language questions
- Retrieves the most relevant clauses
- Evaluates coverage and logic using LLM
- Returns structured, explainable responses in JSON format

## 3. 🔍 Use Case Examples

| Domain | Example Query |
|--------|---------------|
| Insurance | "Does this policy cover knee surgery, and what are the conditions?" |
| Legal | "What are the termination clauses in this agreement?" |
| HR | "What is the maternity leave policy and required documentation?" |
| Compliance | "Is there a clause on GDPR data retention?" |

## 4. 👥 Target Users

- Insurance agents and claim processors
- Legal advisors and compliance officers
- HR managers
- Policyholders or employees seeking document clarity

## 5. 🧱 Key Features

### 1. 📄 Multi-format Document Ingestion
- PDF, DOCX, and email parsing support
- Blob URL input handling

### 2. 🧠 Natural Language Query Understanding
- Accepts user questions in plain language
- Extracts entities, intents, and modifiers

### 3. 📊 Embedding & Semantic Search
- Chunks and indexes documents using Pinecone
- Performs similarity search based on questions

### 4. 🔍 Clause Retrieval & Matching
- Uses LLM to rank retrieved document chunks
- Matches clauses relevant to query semantics

### 5. 🧩 Logic Evaluation with Explainability
- LLM decides if the answer is affirmative or conditional
- Returns rationale and clause source

### 6. 📦 Structured JSON Response
- Outputs answers with fields: `isCovered`, `conditions`, `rationale`, `clause_reference`

## 6. 🔄 System Workflow

```mermaid
flowchart TD
    A[User Uploads Document (PDF/DOCX)] --> B[Document Preprocessing & Chunking]
    B --> C[Embedding via Gemini text-embedding-004]
    C --> D[Pinecone Vector Indexing]
    E[User Asks Natural Language Query] --> F[Gemini 1.5 Pro Parser (Intent & Entity Extraction)]
    F --> G[Pinecone Semantic Search]
    G --> H[Clause Reranking (Gemini 1.5 Pro)]
    H --> I[Logic Evaluation (Gemini 1.5 Pro)]
    I --> J[Structured JSON Output + Rationale]
```

## 7. ⚙️ Technical Architecture

| Component | Tool/Framework |
|-----------|----------------|
| Backend | FastAPI |
| Vector Store | Pinecone |
| Embeddings | Google Gemini (text-embedding-004) |
| LLM | Google Gemini 1.5 Pro |
| PDF Parsing | PyMuPDF / pdfminer.six |
| DOCX Parsing | python-docx |
| Database (optional) | PostgreSQL / SQLite |
| Deployment | Railway / Render / Local |

## 8. 🔐 API Specification

**Endpoint:** `POST /api/v1/hackrx/run`

### Request
```json
{
  "documents": "<PDF Blob URL>",
  "questions": [
    "What is the waiting period for pre-existing diseases (PED) to be covered?",
    "Does this policy cover maternity expenses, and what are the conditions?"
  ]
}
```

### Response
```json
{
  "answers": [
    {
      "question": "Does this policy cover maternity expenses, and what are the conditions?",
      "isCovered": true,
      "conditions": [
        "At least 24 months of continuous coverage",
        "Limited to two deliveries or terminations"
      ],
      "clause_reference": {
        "page": 12,
        "clause_title": "Maternity Benefits"
      },
      "rationale": "The clause states coverage is provided if the insured has been continuously covered for 24 months."
    }
  ]
}
```
## 9. 📊 Evaluation Metrics

| Metric | Description |
|--------|-------------|
| Accuracy | Correct matching of query to clause and correct logical interpretation |
| Token Efficiency | Minimized LLM token usage for cost and speed |
| Latency | Time taken to respond to a query |
| Reusability | Modular design with reusable components |
| Explainability | Does the output include rationale and clause traceability? |

## 10. 🧪 Testing & Evaluation Strategy

### Create unit tests for:
- PDF/DOCX parsing
- Query parsing
- Embedding + retrieval
- Logic evaluation

### Run end-to-end tests using:
- Known documents (low weight)
- Unknown documents (high weight)

### Score queries using:
```python
Score = Question Weight × Document Weight if answer is correct
```
## 11. 🗓️ Timeline

| Day | Task |
|-----|------|
| 1 | Setup FastAPI, blob fetching, and document parsing |
| 2 | Implement chunking + embedding + Pinecone integration |
| 3 | LLM-based query parsing + clause retrieval logic |
| 4 | JSON output formatting + testing |
| 5 | Evaluation, optimization, deployment |

## 12. ✨ Future Enhancements

- Multilingual query support
- Clause highlighting in original PDF
- Feedback loop to fine-tune retrieval accuracy
- UI for document upload and query submission

