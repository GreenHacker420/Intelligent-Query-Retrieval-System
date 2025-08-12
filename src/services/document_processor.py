"""Document processing service for handling PDF, DOCX, and email files."""

import asyncio
import aiohttp
import tempfile
import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import fitz  # PyMuPDF
from docx import Document
from loguru import logger

from ..core.config import get_settings


class DocumentChunk:
    """Represents a chunk of processed document content."""
    
    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary format."""
        return {
            "text": self.text,
            "metadata": self.metadata
        }


class DocumentProcessor:
    """Service for processing various document formats."""
    
    def __init__(self):
        """Initialize the document processor."""
        self.settings = get_settings()
        self.supported_formats = {'.pdf', '.docx', '.doc', '.txt'}
    
    async def process_blob_url(self, blob_url: str) -> List[DocumentChunk]:
        """
        Process a document from a blob URL.
        
        Args:
            blob_url: URL to the document blob
            
        Returns:
            List of document chunks with metadata
        """
        try:
            # Download the document
            document_content, content_type = await self._download_document(blob_url)
            
            # Determine file type and process accordingly
            if 'pdf' in content_type.lower():
                return await self._process_pdf_content(document_content, blob_url)
            elif 'word' in content_type.lower() or 'docx' in content_type.lower():
                return await self._process_docx_content(document_content, blob_url)
            elif 'text' in content_type.lower():
                return await self._process_text_content(document_content.decode('utf-8'), blob_url)
            else:
                logger.warning(f"Unsupported content type: {content_type}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to process blob URL {blob_url}: {e}")
            raise
    
    async def _download_document(self, blob_url: str) -> tuple[bytes, str]:
        """
        Download document from blob URL.
        
        Args:
            blob_url: URL to download from
            
        Returns:
            Tuple of (document_content, content_type)
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(blob_url) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to download document: HTTP {response.status}")
                    
                    content_type = response.headers.get('content-type', 'application/octet-stream')
                    content = await response.read()
                    
                    # Validate file size
                    if len(content) > self.settings.max_document_size_mb * 1024 * 1024:
                        raise Exception(f"Document too large: {len(content)} bytes")
                    
                    logger.info(f"Downloaded document: {len(content)} bytes, type: {content_type}")
                    return content, content_type
                    
        except Exception as e:
            logger.error(f"Failed to download document from {blob_url}: {e}")
            raise
    
    async def _process_pdf_content(self, content: bytes, source_url: str) -> List[DocumentChunk]:
        """
        Process PDF content and extract text chunks.
        
        Args:
            content: PDF file content as bytes
            source_url: Original source URL
            
        Returns:
            List of document chunks
        """
        chunks = []
        
        try:
            # Create temporary file for PyMuPDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Process PDF with PyMuPDF
                doc = fitz.open(temp_file_path)
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    
                    if text.strip():  # Only process pages with content
                        # Split page into chunks
                        page_chunks = self._split_text_into_chunks(
                            text,
                            {
                                "source": source_url,
                                "page": page_num + 1,
                                "total_pages": len(doc),
                                "document_type": "pdf"
                            }
                        )
                        chunks.extend(page_chunks)
                
                doc.close()
                logger.info(f"Processed PDF: {len(chunks)} chunks from {len(doc)} pages")
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Failed to process PDF content: {e}")
            raise
        
        return chunks
    
    async def _process_docx_content(self, content: bytes, source_url: str) -> List[DocumentChunk]:
        """
        Process DOCX content and extract text chunks.
        
        Args:
            content: DOCX file content as bytes
            source_url: Original source URL
            
        Returns:
            List of document chunks
        """
        chunks = []
        
        try:
            # Create temporary file for python-docx
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Process DOCX with python-docx
                doc = Document(temp_file_path)
                
                # Extract text from paragraphs
                full_text = []
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        full_text.append(paragraph.text)
                
                # Combine all text
                document_text = '\n'.join(full_text)
                
                if document_text.strip():
                    # Split document into chunks
                    chunks = self._split_text_into_chunks(
                        document_text,
                        {
                            "source": source_url,
                            "document_type": "docx",
                            "total_paragraphs": len(full_text)
                        }
                    )
                
                logger.info(f"Processed DOCX: {len(chunks)} chunks from {len(full_text)} paragraphs")
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Failed to process DOCX content: {e}")
            raise
        
        return chunks
    
    async def _process_text_content(self, text: str, source_url: str) -> List[DocumentChunk]:
        """
        Process plain text content.
        
        Args:
            text: Text content
            source_url: Original source URL
            
        Returns:
            List of document chunks
        """
        try:
            chunks = self._split_text_into_chunks(
                text,
                {
                    "source": source_url,
                    "document_type": "text"
                }
            )
            
            logger.info(f"Processed text: {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process text content: {e}")
            raise
    
    def _split_text_into_chunks(self, text: str, base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Split text into chunks for optimal embedding and retrieval.
        
        Args:
            text: Text to split
            base_metadata: Base metadata to include in each chunk
            
        Returns:
            List of document chunks
        """
        chunks = []
        
        # Simple sentence-based chunking with overlap
        sentences = text.split('. ')
        
        chunk_size = self.settings.max_chunk_size
        overlap_size = self.settings.chunk_overlap
        
        current_chunk = ""
        chunk_index = 0
        
        for i, sentence in enumerate(sentences):
            # Add sentence to current chunk
            if current_chunk:
                current_chunk += ". " + sentence
            else:
                current_chunk = sentence
            
            # Check if chunk is large enough or if we're at the end
            if (len(current_chunk) >= chunk_size or i == len(sentences) - 1) and current_chunk.strip():
                # Create chunk metadata
                chunk_metadata = {
                    **base_metadata,
                    "chunk_index": chunk_index,
                    "chunk_size": len(current_chunk),
                    "start_sentence": max(0, i - len(current_chunk.split('. ')) + 1),
                    "end_sentence": i
                }
                
                chunks.append(DocumentChunk(current_chunk.strip(), chunk_metadata))
                
                # Prepare next chunk with overlap
                if i < len(sentences) - 1:  # Not the last sentence
                    # Keep last few sentences for overlap
                    overlap_sentences = current_chunk.split('. ')[-overlap_size:]
                    current_chunk = '. '.join(overlap_sentences)
                else:
                    current_chunk = ""
                
                chunk_index += 1
        
        return chunks


# Global processor instance
_document_processor = None


def get_document_processor() -> DocumentProcessor:
    """Get or create the global document processor instance."""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor
