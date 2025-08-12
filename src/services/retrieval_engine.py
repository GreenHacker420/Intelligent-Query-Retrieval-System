"""Advanced retrieval engine combining vector search and keyword matching."""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from ..core.config import get_settings
from ..core.gemini_client import get_gemini_client
from .vector_store import get_vector_store
from .document_processor import DocumentChunk


class RetrievalEngine:
    """Advanced retrieval engine for finding relevant document chunks."""
    
    def __init__(self):
        """Initialize the retrieval engine."""
        self.settings = get_settings()
        self.gemini_client = get_gemini_client()
        self._vector_store = None
    
    async def initialize(self):
        """Initialize the retrieval engine."""
        try:
            self._vector_store = await get_vector_store()
            logger.info("Retrieval engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize retrieval engine: {e}")
            raise
    
    async def store_document(self, chunks: List[DocumentChunk], document_id: str) -> Dict[str, Any]:
        """
        Store document chunks in the vector store.
        
        Args:
            chunks: List of document chunks
            document_id: Unique document identifier
            
        Returns:
            Storage result with statistics
        """
        try:
            if not self._vector_store:
                await self.initialize()
            
            # Store chunks in vector store
            stored_count = await self._vector_store.store_document_chunks(chunks, document_id)
            
            result = {
                "document_id": document_id,
                "total_chunks": len(chunks),
                "stored_chunks": stored_count,
                "success": stored_count == len(chunks)
            }
            
            logger.info(f"Document storage result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to store document: {e}")
            raise
    
    async def retrieve_relevant_chunks(
        self, 
        query: str, 
        document_id: Optional[str] = None,
        use_hybrid_search: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query using hybrid search.
        
        Args:
            query: Search query
            document_id: Optional document ID to filter results
            use_hybrid_search: Whether to combine vector and keyword search
            
        Returns:
            List of relevant chunks with scores
        """
        try:
            if not self._vector_store:
                await self.initialize()
            
            # Prepare metadata filter
            filter_metadata = {}
            if document_id:
                filter_metadata["document_id"] = document_id
            
            # Perform vector search
            logger.debug(f"Performing vector search for: {query[:100]}...")
            vector_results = await self._vector_store.search_similar_chunks(
                query=query,
                top_k=self.settings.max_retrieval_results,
                filter_metadata=filter_metadata
            )
            
            if use_hybrid_search:
                # Enhance with keyword matching
                enhanced_results = await self._enhance_with_keyword_search(query, vector_results)
                return enhanced_results
            else:
                return vector_results
                
        except Exception as e:
            logger.error(f"Failed to retrieve relevant chunks: {e}")
            # Fallback to empty results
            return []
    
    async def _enhance_with_keyword_search(
        self, 
        query: str, 
        vector_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enhance vector search results with keyword matching.
        
        Args:
            query: Original search query
            vector_results: Results from vector search
            
        Returns:
            Enhanced results with combined scoring
        """
        try:
            # Extract keywords from query
            query_words = set(query.lower().split())
            
            enhanced_results = []
            
            for result in vector_results:
                text = result.get("text", "").lower()
                
                # Calculate keyword match score
                keyword_matches = sum(1 for word in query_words if word in text)
                keyword_score = keyword_matches / len(query_words) if query_words else 0
                
                # Combine vector similarity and keyword scores
                vector_score = result.get("score", 0.0)
                combined_score = (0.7 * vector_score) + (0.3 * keyword_score)
                
                enhanced_result = {
                    **result,
                    "keyword_score": keyword_score,
                    "combined_score": combined_score,
                    "keyword_matches": keyword_matches
                }
                
                enhanced_results.append(enhanced_result)
            
            # Sort by combined score
            enhanced_results.sort(key=lambda x: x["combined_score"], reverse=True)
            
            logger.debug(f"Enhanced {len(enhanced_results)} results with keyword matching")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Failed to enhance with keyword search: {e}")
            return vector_results
    
    async def rerank_chunks(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rerank chunks using LLM-based relevance scoring.
        
        Args:
            query: Original query
            chunks: List of chunks to rerank
            
        Returns:
            Reranked chunks with LLM scores
        """
        try:
            if not chunks:
                return chunks
            
            # Limit to top chunks for reranking to manage token usage
            top_chunks = chunks[:self.settings.rerank_top_k * 2]
            
            # Prepare reranking prompt
            chunk_texts = []
            for i, chunk in enumerate(top_chunks):
                chunk_texts.append(f"Chunk {i+1}: {chunk.get('text', '')[:500]}...")
            
            rerank_prompt = f"""
            Query: "{query}"
            
            Please rank the following document chunks by their relevance to the query.
            Respond with a JSON array of chunk numbers (1-{len(chunk_texts)}) in order of relevance (most relevant first).
            
            Chunks:
            {chr(10).join(chunk_texts)}
            
            Response format: [1, 3, 2, ...]
            """
            
            # Get LLM ranking
            ranking_response = await self.gemini_client.generate_content(rerank_prompt)
            
            try:
                import json
                ranking = json.loads(ranking_response.strip())
                
                # Reorder chunks based on LLM ranking
                reranked_chunks = []
                for rank_idx, chunk_num in enumerate(ranking):
                    if 1 <= chunk_num <= len(top_chunks):
                        chunk = top_chunks[chunk_num - 1].copy()
                        chunk["llm_rank"] = rank_idx + 1
                        chunk["llm_score"] = 1.0 - (rank_idx / len(ranking))
                        reranked_chunks.append(chunk)
                
                # Add remaining chunks that weren't ranked
                ranked_indices = set(ranking)
                for i, chunk in enumerate(top_chunks):
                    if (i + 1) not in ranked_indices:
                        chunk_copy = chunk.copy()
                        chunk_copy["llm_rank"] = len(ranking) + 1
                        chunk_copy["llm_score"] = 0.0
                        reranked_chunks.append(chunk_copy)
                
                logger.debug(f"Reranked {len(reranked_chunks)} chunks using LLM")
                return reranked_chunks[:self.settings.rerank_top_k]
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse LLM ranking, using original order: {e}")
                return top_chunks[:self.settings.rerank_top_k]
                
        except Exception as e:
            logger.error(f"Failed to rerank chunks: {e}")
            return chunks[:self.settings.rerank_top_k]
    
    async def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        Get retrieval engine statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            if not self._vector_store:
                await self.initialize()
            
            index_stats = await self._vector_store.get_index_stats()
            
            return {
                "vector_store_stats": index_stats,
                "settings": {
                    "max_retrieval_results": self.settings.max_retrieval_results,
                    "rerank_top_k": self.settings.rerank_top_k,
                    "embedding_model": self.settings.embedding_model,
                    "llm_model": self.settings.llm_model
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get retrieval stats: {e}")
            return {}


# Global retrieval engine instance
_retrieval_engine = None


async def get_retrieval_engine() -> RetrievalEngine:
    """Get or create the global retrieval engine instance."""
    global _retrieval_engine
    if _retrieval_engine is None:
        _retrieval_engine = RetrievalEngine()
        await _retrieval_engine.initialize()
    return _retrieval_engine
