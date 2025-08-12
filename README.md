# 🧠 Intelligent Query Retrieval System

**LLM-Powered Document Analysis for HackRx 2025**

A sophisticated AI system that processes large documents (PDFs, DOCX, emails) and answers natural language questions with explainable, structured responses.

## 🎯 Features

- **Multi-format Document Processing**: PDF, DOCX, and email support
- **Natural Language Queries**: Ask questions in plain English
- **Explainable AI**: Get detailed rationale for every answer
- **Structured Responses**: JSON format with confidence scores
- **Domain Expertise**: Optimized for insurance, legal, HR, and compliance

## 🏗️ Architecture

- **Backend**: FastAPI with async support
- **AI Models**: Google Gemini 2.0 Flash + text-embedding-004
- **Vector Store**: Pinecone for semantic search
- **Document Processing**: PyMuPDF, python-docx
- **API**: RESTful with OpenAPI documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key
- Pinecone API key (for vector search)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Intelligent-Query-Retrieval-System
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

4. **Test the setup**
   ```bash
   python test_setup.py
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 📡 API Usage

### Main Endpoint

**POST** `/api/v1/hackrx/run`

```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is the waiting period for pre-existing diseases?",
    "Does this policy cover maternity expenses?"
  ]
}
```

### Response Format

```json
{
  "answers": [
    {
      "question": "Does this policy cover maternity expenses?",
      "isCovered": true,
      "conditions": [
        "At least 24 months of continuous coverage",
        "Limited to two deliveries"
      ],
      "clause_reference": {
        "page": 12,
        "clause_title": "Maternity Benefits"
      },
      "rationale": "Coverage provided after 24 months continuous enrollment",
      "confidence_score": 0.92,
      "processing_metadata": {
        "model_used": "gemini-2.0-flash",
        "embedding_model": "text-embedding-004",
        "chunks_analyzed": 5,
        "total_tokens": 1247
      }
    }
  ],
  "processing_summary": {
    "total_questions": 1,
    "successful_responses": 1,
    "total_processing_time": "3.2s",
    "document_pages_processed": 45
  }
}
```

## 🔧 Configuration

### Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment

# Optional
MAX_CHUNK_SIZE=1024
CHUNK_OVERLAP=128
MAX_RETRIEVAL_RESULTS=20
DEBUG=false
```

### API Documentation

When running in debug mode, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

Run the setup verification:
```bash
python test_setup.py
```

This will test:
- Configuration loading
- Gemini AI client initialization
- Document processing capabilities
- API model validation

## 📁 Project Structure

```
├── src/
│   ├── api/                 # FastAPI application
│   │   ├── main.py         # App initialization
│   │   ├── models/         # Pydantic models
│   │   └── routes/         # API endpoints
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration management
│   │   └── gemini_client.py # Gemini AI integration
│   └── services/           # Business logic
│       └── document_processor.py # Document handling
├── prd/                    # Product requirements
├── requirements.txt        # Dependencies
├── main.py                # Application entry point
└── test_setup.py          # Setup verification
```

## 🔄 System Workflow

1. **Document Upload**: User provides blob URL to document
2. **Document Processing**: System downloads and chunks the document
3. **Query Analysis**: LLM analyzes user questions for intent/entities
4. **Semantic Search**: Find relevant document sections
5. **Coverage Evaluation**: LLM determines if query is covered
6. **Response Generation**: Structured JSON with explainability

## 🎯 Use Cases

| Domain | Example Query |
|--------|---------------|
| **Insurance** | "Does this policy cover knee surgery, and what are the conditions?" |
| **Legal** | "What are the termination clauses in this agreement?" |
| **HR** | "What is the maternity leave policy and required documentation?" |
| **Compliance** | "Is there a clause on GDPR data retention?" |

## 🚧 Current Status

✅ **Completed**:
- Project setup and configuration
- Google Gemini API integration (updated to latest SDK)
- Document processing pipeline (PDF, DOCX, text)
- FastAPI application with proper models
- Basic query processing and response generation

🔄 **In Progress**:
- Vector store integration with Pinecone
- Advanced semantic search capabilities
- Performance optimization

📋 **Planned**:
- Comprehensive testing suite
- Deployment configuration
- Performance monitoring

## 🤝 Contributing

This project is developed for HackRx 2025. For questions or contributions, please refer to the project documentation.

## 📄 License

[Add your license information here]

---

**Built with ❤️ for HackRx 2025**
