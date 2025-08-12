"""Vector store service for semantic search using Pinecone."""

import asyncio
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from pinecone import Pinecone, ServerlessSpec, PodSpec
from loguru import logger

from ..core.config import get_settings
from ..core.gemini_client import get_gemini_client
from .document_processor import DocumentChunk


class VectorStore:
    """Service for managing document vectors in Pinecone."""
    
    def __init__(self):
        """Initialize the vector store."""
        self.settings = get_settings()
        self.gemini_client = get_gemini_client()
        self._pinecone_client = None
        self._index = None
        self.embedding_dimension = 768  # text-embedding-004 dimension
    
    async def initialize(self):
        """Initialize Pinecone client and index."""
        try:
            # Initialize Pinecone client
            self._pinecone_client = Pinecone(api_key=self.settings.pinecone_api_key)

            # Create or connect to index
            await self._ensure_index_exists()

            logger.info("Vector store initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    async def _ensure_index_exists(self):
        """Ensure the Pinecone index exists, create if necessary."""
        try:
            index_name = self.settings.pinecone_index_name

            # Check if index exists
            existing_indexes = self._pinecone_client.list_indexes()
            index_names = [idx.name for idx in existing_indexes.indexes]

            if index_name not in index_names:
                logger.info(f"Creating new Pinecone index: {index_name}")

                index_created = False

                # Try serverless first (most common and cost-effective)
                try:
                    logger.info("Trying serverless index creation...")
                    self._pinecone_client.create_index(
                        name=index_name,
                        dimension=self.embedding_dimension,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        )
                    )
                    index_created = True
                    logger.info(f"Serverless index {index_name} created successfully")

                except Exception as serverless_error:
                    logger.warning(f"Serverless creation failed: {serverless_error}")

                    # Try pod-based as fallback
                    try:
                        logger.info("Trying pod-based index creation...")
                        self._pinecone_client.create_index(
                            name=index_name,
                            dimension=self.embedding_dimension,
                            metric="cosine",
                            spec=PodSpec(
                                environment="gcp-starter",
                                pod_type="p1.x1",
                                pods=1
                            )
                        )
                        index_created = True
                        logger.info(f"Pod-based index {index_name} created successfully")
                    except Exception as pod_error:
                        logger.warning(f"Initial pod creation failed: {pod_error}")

                if not index_created:
                    # Try with pod-based spec as fallback
                    pod_environments = [
                        "gcp-starter",
                        "us-west1-gcp",
                        "us-east1-gcp",
                        "asia-northeast1-gcp"
                    ]

                    for env in pod_environments:
                        try:
                            logger.info(f"Trying pod-based spec with environment: {env}")
                            self._pinecone_client.create_index(
                                name=index_name,
                                dimension=self.embedding_dimension,
                                metric="cosine",
                                spec=PodSpec(
                                    environment=env,
                                    pod_type="p1.x1",
                                    pods=1
                                )
                            )
                            index_created = True
                            logger.info(f"Index {index_name} created with pod spec: {env}")
                            break
                        except Exception as pod_error:
                            logger.warning(f"Pod environment {env} failed: {pod_error}")
                            continue

                    if not index_created:
                        logger.error("All Pinecone configurations failed")
                        raise Exception("Failed to create index with any configuration")

                # Wait for index to be ready
                await asyncio.sleep(10)

            # Connect to index
            self._index = self._pinecone_client.Index(index_name)
            logger.info(f"Connected to index: {index_name}")

        except Exception as e:
            logger.error(f"Failed to ensure index exists: {e}")
            raise
    
    async def store_document_chunks(self, chunks: List[DocumentChunk], document_id: str) -> int:
        """
        Store document chunks as vectors in Pinecone.
        
        Args:
            chunks: List of document chunks to store
            document_id: Unique identifier for the document
            
        Returns:
            Number of chunks successfully stored
        """
        try:
            if not self._index:
                await self.initialize()

            # Limit chunks for performance (keep most relevant ones)
            max_chunks = 50  # Reasonable limit for fast processing
            if len(chunks) > max_chunks:
                logger.warning(f"Too many chunks ({len(chunks)}), limiting to {max_chunks} for performance")
                # Keep chunks with good size distribution
                chunks = self._select_best_chunks(chunks, max_chunks)

            # Extract text from chunks
            texts = [chunk.text for chunk in chunks]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} chunks...")
            embeddings = await self.gemini_client.generate_embeddings(texts)
            
            # Prepare vectors for upsert
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = self._generate_vector_id(document_id, i)
                
                # Prepare metadata
                metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "text": chunk.text[:1000],  # Truncate for metadata limits
                    "source": chunk.metadata.get("source", ""),
                    "page": chunk.metadata.get("page"),
                    "document_type": chunk.metadata.get("document_type", ""),
                    "chunk_size": len(chunk.text)
                }
                
                # Remove None values
                metadata = {k: v for k, v in metadata.items() if v is not None}
                
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })
            
            # Upsert vectors in batches
            batch_size = 100
            stored_count = 0
            
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                
                # Run upsert in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self._index.upsert(vectors=batch)
                )
                
                stored_count += len(batch)
                logger.debug(f"Stored batch {i//batch_size + 1}: {len(batch)} vectors")
            
            logger.info(f"Successfully stored {stored_count} vectors for document {document_id}")
            return stored_count
            
        except Exception as e:
            logger.error(f"Failed to store document chunks: {e}")
            raise

    def _select_best_chunks(self, chunks: List[DocumentChunk], max_chunks: int) -> List[DocumentChunk]:
        """
        Select the best chunks for processing based on size and content quality.

        Args:
            chunks: All available chunks
            max_chunks: Maximum number of chunks to select

        Returns:
            Selected best chunks
        """
        if len(chunks) <= max_chunks:
            return chunks

        # Score chunks based on size and content quality
        scored_chunks = []
        for chunk in chunks:
            score = 0
            text_len = len(chunk.text)

            # Prefer chunks with good size (not too small, not too large)
            if 500 <= text_len <= 2000:
                score += 3
            elif 200 <= text_len <= 3000:
                score += 2
            else:
                score += 1

            # Prefer chunks with more content indicators
            if any(keyword in chunk.text.lower() for keyword in ['policy', 'coverage', 'benefit', 'condition', 'exclusion']):
                score += 2

            # Prefer chunks with structured content
            if any(indicator in chunk.text for indicator in [':', '-', '•', '1.', '2.', 'a)', 'b)']):
                score += 1

            scored_chunks.append((score, chunk))

        # Sort by score and take the best ones
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        selected = [chunk for score, chunk in scored_chunks[:max_chunks]]

        logger.info(f"Selected {len(selected)} best chunks from {len(chunks)} total chunks")
        return selected
    
    async def search_similar_chunks(
        self, 
        query: str, 
        top_k: int = None,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar document chunks using vector similarity.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of similar chunks with metadata and scores
        """
        try:
            if not self._index:
                await self.initialize()
            
            if top_k is None:
                top_k = self.settings.max_retrieval_results
            
            # Generate query embedding
            logger.debug(f"Generating embedding for query: {query[:100]}...")
            query_embeddings = await self.gemini_client.generate_embeddings([query])
            query_vector = query_embeddings[0]
            
            # Perform similarity search
            loop = asyncio.get_event_loop()
            search_results = await loop.run_in_executor(
                None,
                lambda: self._index.query(
                    vector=query_vector,
                    top_k=top_k,
                    include_metadata=True,
                    include_values=False,
                    filter=filter_metadata
                )
            )
            
            # Process results
            similar_chunks = []
            for match in search_results.matches:
                chunk_data = {
                    "id": match.id,
                    "score": float(match.score),
                    "text": match.metadata.get("text", ""),
                    "page": match.metadata.get("page"),
                    "document_id": match.metadata.get("document_id"),
                    "chunk_index": match.metadata.get("chunk_index"),
                    "metadata": match.metadata
                }
                similar_chunks.append(chunk_data)
            
            logger.info(f"Found {len(similar_chunks)} similar chunks for query")
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Failed to search similar chunks: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> int:
        """
        Delete all vectors for a specific document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Number of vectors deleted
        """
        try:
            if not self._index:
                await self.initialize()
            
            # Query for all vectors with this document_id
            loop = asyncio.get_event_loop()
            query_results = await loop.run_in_executor(
                None,
                lambda: self._index.query(
                    vector=[0.0] * self.embedding_dimension,  # Dummy vector
                    top_k=10000,  # Large number to get all
                    include_metadata=True,
                    include_values=False,
                    filter={"document_id": document_id}
                )
            )
            
            # Extract vector IDs
            vector_ids = [match.id for match in query_results.matches]
            
            if vector_ids:
                # Delete vectors
                await loop.run_in_executor(
                    None,
                    lambda: self._index.delete(ids=vector_ids)
                )
                
                logger.info(f"Deleted {len(vector_ids)} vectors for document {document_id}")
                return len(vector_ids)
            else:
                logger.info(f"No vectors found for document {document_id}")
                return 0
                
        except Exception as e:
            logger.error(f"Failed to delete document vectors: {e}")
            raise
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector index.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            if not self._index:
                await self.initialize()
            
            loop = asyncio.get_event_loop()
            stats = await loop.run_in_executor(
                None,
                lambda: self._index.describe_index_stats()
            )
            
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": dict(stats.namespaces) if stats.namespaces else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}
    
    def _generate_vector_id(self, document_id: str, chunk_index: int) -> str:
        """
        Generate a unique vector ID for a document chunk.
        
        Args:
            document_id: Document identifier
            chunk_index: Index of the chunk within the document
            
        Returns:
            Unique vector ID
        """
        # Create a hash-based ID to ensure uniqueness
        content = f"{document_id}_{chunk_index}"
        hash_object = hashlib.md5(content.encode())
        return f"doc_{hash_object.hexdigest()[:16]}_chunk_{chunk_index}"


# Global vector store instance
_vector_store = None


async def get_vector_store() -> VectorStore:
    """Get or create the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        await _vector_store.initialize()
    return _vector_store
