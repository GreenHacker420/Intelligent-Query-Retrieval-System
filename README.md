# 🧠 Intelligent Query Retrieval System

**LLM-Powered Document Analysis for HackRx 2025** ✅ **FULLY OPERATIONAL**

A state-of-the-art AI system that processes large documents (PDFs, DOCX, emails) and answers natural language questions with explainable, structured responses using Google Gemini AI and Pinecone vector search.

## 🎯 Features

- **🔄 Advanced Multi-Step Analysis**: Query decomposition → Vector search → LLM reranking → Logic evaluation
- **📄 Multi-format Document Processing**: PDF (pdfminer.six), DOCX, and text support
- **❓ Natural Language Queries**: Ask complex questions in plain English
- **🧠 Explainable AI**: Get detailed rationale with confidence scores for every answer
- **📊 Structured Responses**: JSON format with source references and metadata
- **🎯 Domain Expertise**: Optimized for insurance, legal, HR, and compliance documents
- **⚡ High Performance**: Async operations, vector caching, hybrid search

## 🏗️ Architecture

- **Backend**: FastAPI with async support ✅ **RUNNING**
- **AI Models**: Google Gemini 2.0 Flash + text-embedding-004 ✅ **CONNECTED**
- **Vector Store**: Pinecone serverless for semantic search ✅ **CONNECTED**
- **Document Processing**: pdfminer.six, python-docx ✅ **WORKING**
- **API**: RESTful with OpenAPI documentation ✅ **LIVE**
- **Advanced Features**: Hybrid search, LLM reranking, multi-step reasoning ✅ **IMPLEMENTED**

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (tested with Python 3.13)
- Google Gemini API key ✅ **CONFIGURED**
- Pinecone API key ✅ **CONFIGURED**

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Intelligent-Query-Retrieval-System
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** ✅ **ALREADY DONE**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys (already configured)
   ```

5. **Test the setup**
   ```bash
   python check_env_simple.py  # Basic config check
   python test_env_config.py   # API connectivity test
   ```

6. **Run the application** ✅ **CURRENTLY RUNNING**
   ```bash
   source venv/bin/activate
   python main.py
   ```

7. **Start the web interface** ✅ **AVAILABLE**
   ```bash
   # In a new terminal
   cd frontend
   python3 server.py
   ```

**🌐 Web Interface**: `http://localhost:5001` ✅ **LIVE**
**📡 API Backend**: `http://localhost:8000` ✅ **RUNNING**

## 🌐 **Web Interface** ✅ **LIVE & READY**

### 🖥️ **User-Friendly Web UI**
- **Frontend URL**: `http://localhost:5001` ✅ **RUNNING**
- **Modern Interface**: Responsive design for all devices
- **Easy Document Upload**: Simple URL input with validation
- **Interactive Questions**: Add multiple questions with samples
- **Rich Results Display**: Visual indicators, confidence scores, detailed analysis
- **Export Functionality**: Download results as JSON

### 📱 **Features**
- ✅ **Document URL Input** with validation and sample documents
- ✅ **Multi-Question Support** with sample question suggestions
- ✅ **Real-time Analysis** with loading indicators
- ✅ **Visual Results** with coverage status, confidence bars, conditions
- ✅ **Export Results** as JSON files
- ✅ **Responsive Design** for desktop, tablet, and mobile
- ✅ **Error Handling** with user-friendly messages

## 📡 API Usage ✅ **LIVE & TESTED**

### 🌐 Available Endpoints

- **Web Interface**: `http://localhost:5001` (User-friendly UI)
- **Main API**: `POST http://localhost:8000/api/v1/hackrx/run`
- **Health Check**: `GET http://localhost:8000/health`
- **Root Info**: `GET http://localhost:8000/`
- **API Docs**: `http://localhost:8000/docs` (when debug=true)

### 🚀 Main Endpoint Usage

**POST** `/api/v1/hackrx/run`

```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/insurance-policy.pdf",
    "questions": [
      "Does this policy cover knee surgery?",
      "What is the waiting period for pre-existing conditions?",
      "Are there any exclusions for maternity benefits?"
    ]
  }'
```

### 📊 Enhanced Response Format

```json
{
  "answers": [
    {
      "question": "Does this policy cover knee surgery?",
      "isCovered": true,
      "conditions": [
        "24-month waiting period for pre-existing conditions",
        "Pre-authorization required from network provider",
        "Coverage limited to medically necessary procedures"
      ],
      "clause_reference": {
        "page": 15,
        "clause_title": "Surgical Procedures Coverage"
      },
      "rationale": "Knee surgery is explicitly covered under surgical procedures with specific waiting periods and authorization requirements. [Evidence: strong] [Completeness: complete]",
      "confidence_score": 0.94,
      "processing_metadata": {
        "model_used": "gemini-2.0-flash",
        "embedding_model": "text-embedding-004",
        "chunks_analyzed": 8,
        "total_tokens": 1456
      }
    }
  ],
  "processing_summary": {
    "total_questions": 3,
    "successful_responses": 3,
    "total_processing_time": "4.7s",
    "document_pages_processed": 52
  }
}
```

## 🔧 Configuration ✅ **FULLY CONFIGURED**

### Environment Variables Status

```env
# ✅ CONFIGURED AND WORKING
GEMINI_API_KEY=AIzaSyC3afvFLaqkfDuREqVco6ahr4rYc-3F8UY
PINECONE_API_KEY=pcsk_4mHWWQ_6rDmYFdPSbvgGFzUNMwa1WLiGm8ubccode2RR3YY3yAG4Gk4WmBVbBxV295SSWh
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=hackrx-documents

# ✅ OPTIMIZED SETTINGS
APP_NAME=Intelligent Query Retrieval System
DEBUG=false
MAX_CHUNK_SIZE=1024
CHUNK_OVERLAP=128
MAX_RETRIEVAL_RESULTS=20
RERANK_TOP_K=5
```

### 📚 API Documentation

- **Swagger UI**: `http://localhost:8000/docs` (when debug=true)
- **ReDoc**: `http://localhost:8000/redoc` (when debug=true)
- **Health Check**: `http://localhost:8000/health`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🧪 Testing ✅ **COMPREHENSIVE SUITE AVAILABLE**

### Quick Tests
```bash
# Basic configuration check
python check_env_simple.py

# API connectivity test
python test_env_config.py

# Comprehensive system test
python run_tests.py

# Integration tests (requires pytest)
pytest tests/
```

### Test Coverage
- ✅ Configuration loading and validation
- ✅ Gemini AI client connectivity
- ✅ Pinecone vector store connection
- ✅ Document processing capabilities
- ✅ API model validation
- ✅ End-to-end workflow testing
- ✅ Performance and memory tests

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
│       ├── document_processor.py # Document handling
│       ├── vector_store.py # Pinecone integration
│       ├── retrieval_engine.py # Advanced search
│       └── decision_engine.py # Multi-step reasoning
├── frontend/               # Web User Interface ✅ NEW
│   ├── index.html         # Main web page
│   ├── styles.css         # Modern CSS styling
│   ├── script.js          # Interactive functionality
│   ├── server.py          # Development server
│   └── README.md          # Frontend documentation
├── tests/                  # Comprehensive test suite
├── prd/                    # Product requirements
├── requirements.txt        # Dependencies
├── main.py                # Application entry point
└── run_tests.py           # System verification
```

## 🔄 Advanced System Workflow ✅ **FULLY IMPLEMENTED**

1. **📥 Document Upload**: User provides blob URL to document
2. **📄 Document Processing**: System downloads, parses, and intelligently chunks the document
3. **🗄️ Vector Storage**: Document chunks are embedded and stored in Pinecone
4. **❓ Query Analysis**: Gemini AI analyzes user questions for intent, entities, and domain
5. **🔍 Hybrid Retrieval**: Vector similarity search + keyword matching for relevant chunks
6. **🎯 LLM Reranking**: Advanced relevance scoring using Gemini AI
7. **🧠 Multi-Step Reasoning**: Query decomposition → Sub-analysis → Synthesis → Validation
8. **⚖️ Decision Engine**: Complex logic evaluation with contradiction detection
9. **📊 Response Generation**: Structured JSON with explainability, confidence scores, and metadata

## 🎯 Use Cases

| Domain | Example Query |
|--------|---------------|
| **Insurance** | "Does this policy cover knee surgery, and what are the conditions?" |
| **Legal** | "What are the termination clauses in this agreement?" |
| **HR** | "What is the maternity leave policy and required documentation?" |
| **Compliance** | "Is there a clause on GDPR data retention?" |

## 🎯 System Status: **PRODUCTION READY** ✅

### ✅ **FULLY COMPLETED (100%)**:
- ✅ **Project Foundation**: Modern FastAPI + async architecture
- ✅ **Gemini AI Integration**: Latest google-genai SDK with full connectivity
- ✅ **Document Processing**: PDF (pdfminer.six), DOCX, text with intelligent chunking
- ✅ **Vector Store**: Pinecone integration with auto-indexing and hybrid search
- ✅ **Advanced Retrieval**: Multi-stage pipeline with LLM reranking
- ✅ **Decision Engine**: Complex multi-step reasoning with validation
- ✅ **API Endpoints**: Complete RESTful API with OpenAPI documentation
- ✅ **Testing Framework**: Comprehensive test suite with integration tests
- ✅ **Configuration**: Environment setup with API key validation
- ✅ **Documentation**: Complete usage guides and implementation tracking

### 🚀 **READY FOR**:
- ✅ **Production Deployment**: Fully tested and operational
- ✅ **HackRx 2025 Submission**: All requirements met and exceeded
- ✅ **Real-world Usage**: Insurance, legal, HR, compliance document analysis
- ✅ **Scale**: Async operations, vector caching, performance optimization

## 🤝 Contributing

This project is developed for HackRx 2025. For questions or contributions, please refer to the project documentation.



**Built with ❤️ by team 'CuttingEdge' for HackRx 2025**
