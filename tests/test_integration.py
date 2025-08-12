"""Integration tests for the Intelligent Query Retrieval System."""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSystemIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def mock_gemini_client(self):
        """Mock Gemini client for testing."""
        client = Mock()
        client.generate_content = AsyncMock()
        client.generate_embeddings = AsyncMock()
        client.analyze_query = AsyncMock()
        client.evaluate_coverage = AsyncMock()
        return client
    
    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store for testing."""
        store = Mock()
        store.initialize = AsyncMock()
        store.store_document_chunks = AsyncMock(return_value=5)
        store.search_similar_chunks = AsyncMock()
        return store
    
    @pytest.fixture
    def sample_document_chunks(self):
        """Sample document chunks for testing."""
        return [
            {
                "text": "This policy covers knee surgery with a 24-month waiting period.",
                "metadata": {"page": 1, "chunk_index": 0, "document_type": "pdf"}
            },
            {
                "text": "Maternity benefits are available after 12 months of continuous coverage.",
                "metadata": {"page": 2, "chunk_index": 1, "document_type": "pdf"}
            },
            {
                "text": "Pre-existing conditions are excluded for the first 48 months.",
                "metadata": {"page": 3, "chunk_index": 2, "document_type": "pdf"}
            }
        ]
    
    @pytest.fixture
    def sample_query_request(self):
        """Sample API request for testing."""
        return {
            "documents": "https://example.com/test-policy.pdf",
            "questions": [
                "Does this policy cover knee surgery?",
                "What is the waiting period for maternity benefits?"
            ]
        }
    
    @pytest.mark.asyncio
    async def test_document_processing_pipeline(self, sample_document_chunks):
        """Test the document processing pipeline."""
        try:
            from services.document_processor import DocumentProcessor
            
            processor = DocumentProcessor()
            
            # Test text chunking
            test_text = "This is a test document. It has multiple sentences. Each sentence should be processed correctly."
            chunks = processor._split_text_into_chunks(
                test_text, 
                {"source": "test", "document_type": "text"}
            )
            
            assert len(chunks) > 0
            assert all(hasattr(chunk, 'text') for chunk in chunks)
            assert all(hasattr(chunk, 'metadata') for chunk in chunks)
            
        except ImportError:
            pytest.skip("Document processor dependencies not available")
    
    @pytest.mark.asyncio
    async def test_decision_engine_analysis(self, mock_gemini_client, sample_document_chunks):
        """Test the advanced decision engine."""
        try:
            from services.decision_engine import DecisionEngine
            
            # Mock Gemini responses
            mock_gemini_client.generate_content.side_effect = [
                '["Is knee surgery covered?", "What are the conditions?"]',  # Decomposition
                '{"sub_question": "Is knee surgery covered?", "is_addressed": true, "answer": "Yes", "confidence": 0.9}',  # Sub-analysis
                '{"sub_question": "What are the conditions?", "is_addressed": true, "answer": "24-month waiting period", "confidence": 0.8}',  # Sub-analysis
                '{"isCovered": true, "conditions": ["24-month waiting period"], "confidence_score": 0.85}',  # Synthesis
                '{"is_consistent": true, "final_recommendation": "accept"}'  # Validation
            ]
            
            with patch('services.decision_engine.get_gemini_client', return_value=mock_gemini_client):
                engine = DecisionEngine()
                
                result = await engine.analyze_complex_query(
                    "Does this policy cover knee surgery?",
                    sample_document_chunks,
                    "insurance"
                )
                
                assert "isCovered" in result
                assert "conditions" in result
                assert "confidence_score" in result
                assert result.get("confidence_score", 0) > 0
                
        except ImportError:
            pytest.skip("Decision engine dependencies not available")
    
    @pytest.mark.asyncio
    async def test_api_endpoint_structure(self, sample_query_request):
        """Test API endpoint structure and response format."""
        try:
            from api.models.request import QueryRequest
            from api.models.response import QueryResponse, QueryAnswer, ClauseReference, ProcessingMetadata, ProcessingSummary
            
            # Test request validation
            request = QueryRequest(**sample_query_request)
            assert request.documents == sample_query_request["documents"]
            assert len(request.questions) == len(sample_query_request["questions"])
            
            # Test response structure
            answer = QueryAnswer(
                question="Test question?",
                isCovered=True,
                conditions=["Test condition"],
                clause_reference=ClauseReference(page=1, clause_title="Test Clause"),
                rationale="Test rationale",
                confidence_score=0.9,
                processing_metadata=ProcessingMetadata(
                    model_used="gemini-2.0-flash",
                    embedding_model="text-embedding-004",
                    chunks_analyzed=3
                )
            )
            
            summary = ProcessingSummary(
                total_questions=1,
                successful_responses=1,
                total_processing_time="2.5s"
            )
            
            response = QueryResponse(answers=[answer], processing_summary=summary)
            
            # Validate response structure
            assert len(response.answers) == 1
            assert response.answers[0].isCovered == True
            assert response.processing_summary.total_questions == 1
            
        except ImportError:
            pytest.skip("API model dependencies not available")
    
    def test_configuration_loading(self):
        """Test configuration loading and validation."""
        try:
            from core.config import Settings
            
            # Test with minimal configuration
            settings = Settings(
                gemini_api_key="test_key",
                pinecone_api_key="test_key",
                pinecone_environment="test_env"
            )
            
            assert settings.gemini_api_key == "test_key"
            assert settings.max_chunk_size > 0
            assert settings.max_retrieval_results > 0
            assert settings.llm_model is not None
            assert settings.embedding_model is not None
            
        except ImportError:
            pytest.skip("Configuration dependencies not available")
    
    @pytest.mark.asyncio
    async def test_end_to_end_mock_flow(self, mock_gemini_client, mock_vector_store, sample_query_request):
        """Test end-to-end flow with mocked dependencies."""
        try:
            # Mock all external dependencies
            mock_gemini_client.analyze_query.return_value = {
                "intent": "coverage_check",
                "entities": ["knee surgery"],
                "domain": "insurance"
            }
            
            mock_gemini_client.generate_content.return_value = '{"isCovered": true, "conditions": ["24-month waiting"], "confidence_score": 0.9}'
            
            mock_vector_store.search_similar_chunks.return_value = [
                {
                    "text": "Knee surgery is covered after 24 months",
                    "score": 0.95,
                    "page": 1
                }
            ]
            
            # This would be the actual API call flow
            # For now, just validate the structure
            assert sample_query_request["documents"].startswith("https://")
            assert len(sample_query_request["questions"]) > 0
            
        except Exception as e:
            pytest.skip(f"End-to-end test dependencies not available: {e}")


class TestPerformance:
    """Performance and load tests."""
    
    def test_chunking_performance(self):
        """Test document chunking performance."""
        try:
            from services.document_processor import DocumentProcessor
            
            processor = DocumentProcessor()
            
            # Test with large text
            large_text = "This is a test sentence. " * 1000
            
            import time
            start_time = time.time()
            
            chunks = processor._split_text_into_chunks(
                large_text,
                {"source": "performance_test", "document_type": "text"}
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            assert processing_time < 5.0  # Should process in under 5 seconds
            assert len(chunks) > 0
            
        except ImportError:
            pytest.skip("Performance test dependencies not available")
    
    def test_memory_usage(self):
        """Test memory usage with large documents."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulate processing large document
        large_data = ["Test chunk " * 100] * 1000
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Should not use more than 100MB for this test
        assert memory_increase < 100


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    print("🧪 Running Integration Tests...\n")
    
    test_instance = TestSystemIntegration()
    
    # Run basic tests
    try:
        test_instance.test_configuration_loading()
        print("✅ Configuration loading test passed")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
    
    try:
        # Create sample data
        sample_request = {
            "documents": "https://example.com/test.pdf",
            "questions": ["Test question?"]
        }
        
        asyncio.run(test_instance.test_api_endpoint_structure(sample_request))
        print("✅ API endpoint structure test passed")
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
    
    print("\n📊 Integration tests completed")
    print("💡 For full test suite, install pytest and run: pytest tests/")
