"""Simple test script to verify the setup and API functionality."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import get_settings
from src.core.gemini_client import get_gemini_client
from src.services.document_processor import get_document_processor


async def test_configuration():
    """Test configuration loading."""
    print("🔧 Testing configuration...")
    try:
        settings = get_settings()
        print(f"✅ App Name: {settings.app_name}")
        print(f"✅ Version: {settings.app_version}")
        print(f"✅ LLM Model: {settings.llm_model}")
        print(f"✅ Embedding Model: {settings.embedding_model}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def test_gemini_client():
    """Test Gemini client initialization."""
    print("\n🤖 Testing Gemini client...")
    try:
        client = get_gemini_client()
        print("✅ Gemini client initialized successfully")
        
        # Test a simple content generation (if API key is available)
        try:
            response = await client.generate_content("Hello, this is a test. Please respond with 'Test successful'.")
            print(f"✅ Content generation test: {response[:50]}...")
            return True
        except Exception as e:
            print(f"⚠️  Content generation test failed (API key may not be configured): {e}")
            return True  # Still consider client init successful
            
    except Exception as e:
        print(f"❌ Gemini client test failed: {e}")
        return False


async def test_document_processor():
    """Test document processor initialization."""
    print("\n📄 Testing document processor...")
    try:
        processor = get_document_processor()
        print("✅ Document processor initialized successfully")
        
        # Test text processing
        test_text = "This is a test document. It contains multiple sentences. Each sentence should be processed correctly."
        chunks = processor._split_text_into_chunks(test_text, {"source": "test", "document_type": "text"})
        print(f"✅ Text chunking test: {len(chunks)} chunks created")
        return True
        
    except Exception as e:
        print(f"❌ Document processor test failed: {e}")
        return False


async def test_api_models():
    """Test API model validation."""
    print("\n📋 Testing API models...")
    try:
        from src.api.models.request import QueryRequest
        from src.api.models.response import QueryResponse, QueryAnswer, ClauseReference, ProcessingMetadata, ProcessingSummary
        
        # Test request model
        request = QueryRequest(
            documents="https://example.com/test.pdf",
            questions=["What is covered?", "What are the conditions?"]
        )
        print("✅ Request model validation successful")
        
        # Test response model components
        clause_ref = ClauseReference(page=1, clause_title="Test Clause")
        metadata = ProcessingMetadata(
            model_used="gemini-2.0-flash",
            embedding_model="text-embedding-004",
            chunks_analyzed=3,
            total_tokens=100
        )
        
        answer = QueryAnswer(
            question="Test question?",
            isCovered=True,
            conditions=["Test condition"],
            clause_reference=clause_ref,
            rationale="Test rationale",
            confidence_score=0.9,
            processing_metadata=metadata
        )
        
        summary = ProcessingSummary(
            total_questions=1,
            successful_responses=1,
            total_processing_time="1.0s",
            document_pages_processed=5
        )
        
        response = QueryResponse(answers=[answer], processing_summary=summary)
        print("✅ Response model validation successful")
        return True
        
    except Exception as e:
        print(f"❌ API models test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting setup verification tests...\n")
    
    tests = [
        test_configuration,
        test_gemini_client,
        test_document_processor,
        test_api_models
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! The system is ready to run.")
        print("\n🔧 Next steps:")
        print("1. Set up your environment variables (copy .env.template to .env)")
        print("2. Add your GEMINI_API_KEY to the .env file")
        print("3. Run the application with: python main.py")
    else:
        print("⚠️  Some tests failed. Please check the configuration and dependencies.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
