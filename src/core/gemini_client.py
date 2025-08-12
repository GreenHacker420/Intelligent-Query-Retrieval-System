"""Gemini AI client for embeddings and language model operations."""

import asyncio
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from loguru import logger

from .config import get_settings


class GeminiClient:
    """Client for interacting with Google Gemini AI services."""

    def __init__(self):
        """Initialize the Gemini client."""
        self.settings = get_settings()
        self._client = None
        self._configure_client()

    def _configure_client(self):
        """Configure the Gemini API client."""
        try:
            # Create client with API key
            self._client = genai.Client(api_key=self.settings.gemini_api_key)
            logger.info("Gemini AI client configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini AI client: {e}")
            raise

    @property
    def client(self):
        """Get the Gemini client instance."""
        if self._client is None:
            self._configure_client()
        return self._client
    
    async def generate_embeddings(self, texts: List[str], task_type: str = "retrieval_document") -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Gemini text-embedding-004.

        Args:
            texts: List of text strings to embed
            task_type: Type of task for embedding optimization

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []

            # Process texts in batches to avoid rate limits
            batch_size = 10
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = []

                for text in batch:
                    # Run embedding generation in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        lambda t=text: self.client.models.embed_content(
                            model=self.settings.embedding_model,
                            contents=t,
                            config=types.EmbedContentConfig(
                                task_type=task_type
                            )
                        )
                    )
                    batch_embeddings.append(result.embeddings[0].values)

                embeddings.extend(batch_embeddings)

                # Small delay between batches to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)

            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Generate content using Gemini 1.5 Pro.

        Args:
            prompt: The input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text content
        """
        try:
            # Run content generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.settings.llm_model,
                    contents=prompt,
                    **kwargs
                )
            )

            logger.info("Content generated successfully")
            return response.text

        except Exception as e:
            logger.error(f"Failed to generate content: {e}")
            raise
    
    async def analyze_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze a query to extract intent, entities, and other relevant information.
        
        Args:
            query: The user query to analyze
            context: Optional context for better understanding
            
        Returns:
            Dictionary containing analysis results
        """
        prompt = f"""
        Analyze the following query and extract key information:
        
        Query: "{query}"
        Context: {context}
        
        Please provide a JSON response with the following structure:
        {{
            "intent": "The main intent of the query (e.g., 'coverage_check', 'condition_inquiry', 'policy_details')",
            "entities": ["List of important entities mentioned (e.g., 'knee surgery', 'maternity', 'waiting period')"],
            "domain": "The likely domain (insurance, legal, hr, compliance)",
            "question_type": "Type of question (yes_no, conditional, informational)",
            "key_terms": ["Important terms for semantic search"]
        }}
        
        Respond only with valid JSON.
        """
        
        try:
            # Use structured output for better JSON parsing
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.settings.llm_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
            )

            # Parse JSON response
            import json
            analysis = json.loads(response.text.strip())
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze query: {e}")
            # Return default analysis if parsing fails
            return {
                "intent": "general_inquiry",
                "entities": [query],
                "domain": "general",
                "question_type": "informational",
                "key_terms": query.split()
            }
    
    async def evaluate_coverage(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate coverage and generate structured response based on retrieved document chunks.
        
        Args:
            query: The original user query
            retrieved_chunks: List of relevant document chunks with metadata
            
        Returns:
            Structured evaluation result
        """
        # Prepare context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            context_parts.append(f"Chunk {i+1} (Page {chunk.get('page', 'N/A')}):\n{chunk.get('text', '')}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""
        Based on the following document chunks, analyze the query and provide a structured response.
        
        Query: "{query}"
        
        Document Context:
        {context}
        
        Please provide a JSON response with the following structure:
        {{
            "isCovered": true/false,
            "conditions": ["List of conditions or requirements if any"],
            "clause_reference": {{
                "page": "Page number where relevant clause is found",
                "clause_title": "Title or description of the relevant clause"
            }},
            "rationale": "Clear explanation of the decision and reasoning",
            "confidence_score": 0.0-1.0
        }}
        
        Guidelines:
        - Set isCovered to true only if the document explicitly covers the queried topic
        - Include all relevant conditions or limitations
        - Provide clear rationale with specific references to the document
        - Assign confidence score based on clarity and explicitness of the information
        
        Respond only with valid JSON.
        """
        
        try:
            # Use structured output for better JSON parsing
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.settings.llm_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
            )

            import json
            evaluation = json.loads(response.text.strip())
            return evaluation

        except Exception as e:
            logger.error(f"Failed to evaluate coverage: {e}")
            # Return default response if parsing fails
            return {
                "isCovered": False,
                "conditions": [],
                "clause_reference": {"page": "N/A", "clause_title": "N/A"},
                "rationale": "Unable to determine coverage due to processing error",
                "confidence_score": 0.0
            }


# Global client instance
_gemini_client = None


def get_gemini_client() -> GeminiClient:
    """Get or create the global Gemini client instance."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
