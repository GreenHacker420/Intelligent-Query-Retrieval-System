"""Document processing service for handling PDF, DOCX, and email files."""

import asyncio
import aiohttp
import tempfile
import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from pdfminer.high_level import extract_text
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
        Process a document from a blob URL or local file URL.

        Args:
            blob_url: URL to the document blob or local file URL

        Returns:
            List of document chunks with metadata
        """
        try:
            # Check if it's a local file URL
            if blob_url.startswith('file://'):
                return await self._process_local_file(blob_url)

            # Download the document from remote URL
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

    async def _process_local_file(self, file_url: str) -> List[DocumentChunk]:
        """
        Process a local file from a file:// URL.

        Args:
            file_url: Local file URL (file://path/to/file)

        Returns:
            List of document chunks with metadata
        """
        try:
            # Extract file path from URL
            file_path = file_url[7:]  # Remove 'file://' prefix

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Local file not found: {file_path}")

            # Read file content
            with open(file_path, 'rb') as f:
                content = f.read()

            # Determine file type by extension
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.pdf':
                return await self._process_pdf_content(content, file_url)
            elif file_extension in ['.docx', '.doc']:
                return await self._process_docx_content(content, file_url)
            elif file_extension == '.txt':
                return await self._process_text_content(content.decode('utf-8'), file_url)
            else:
                logger.warning(f"Unsupported file extension: {file_extension}")
                return []

        except Exception as e:
            logger.error(f"Failed to process local file {file_url}: {e}")
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
            # Create temporary file for PDF processing
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            try:
                if PYMUPDF_AVAILABLE:
                    # Process PDF with PyMuPDF (preferred)
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
                    logger.info(f"Processed PDF with PyMuPDF: {len(chunks)} chunks from {len(doc)} pages")

                else:
                    # Fallback to pdfminer.six
                    logger.info("Using pdfminer.six for PDF processing (PyMuPDF not available)")
                    text = extract_text(temp_file_path)

                    if text.strip():
                        # Split document into chunks
                        chunks = self._split_text_into_chunks(
                            text,
                            {
                                "source": source_url,
                                "document_type": "pdf",
                                "extraction_method": "pdfminer"
                            }
                        )

                    logger.info(f"Processed PDF with pdfminer.six: {len(chunks)} chunks")

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
        Split text into optimized chunks for better performance and relevance.

        Args:
            text: Text to split
            base_metadata: Base metadata to include in each chunk

        Returns:
            List of document chunks (optimized for fewer, more meaningful chunks)
        """
        chunks = []

        # Clean and normalize text
        text = text.strip()
        if not text:
            return chunks

        # Use larger chunk size for better context and fewer chunks
        optimal_chunk_size = min(self.settings.max_chunk_size * 3, 3072)  # Much larger chunks
        min_chunk_size = 200  # Minimum meaningful size
        overlap_size = 150  # Reasonable overlap

        # Split by paragraphs first for better semantic boundaries
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        if not paragraphs:
            # Fallback to sentence splitting
            paragraphs = [s.strip() + '.' for s in text.split('.') if s.strip()]

        current_chunk = ""
        chunk_index = 0

        for i, paragraph in enumerate(paragraphs):
            # Check if adding this paragraph would exceed chunk size
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph

            if len(potential_chunk) <= optimal_chunk_size:
                current_chunk = potential_chunk
            else:
                # Save current chunk if it has meaningful content
                if current_chunk and len(current_chunk.strip()) > min_chunk_size:
                    chunk_metadata = {
                        **base_metadata,
                        "chunk_index": chunk_index,
                        "chunk_size": len(current_chunk),
                        "chunk_type": "optimized",
                        "paragraph_count": len([p for p in current_chunk.split('\n\n') if p.strip()])
                    }

                    chunks.append(DocumentChunk(current_chunk.strip(), chunk_metadata))
                    chunk_index += 1

                # Start new chunk with overlap from previous chunk
                if current_chunk and len(current_chunk) > overlap_size:
                    # Take last part of previous chunk as overlap
                    overlap_text = current_chunk[-overlap_size:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Add final chunk if it has meaningful content
        if current_chunk and len(current_chunk.strip()) > min_chunk_size:
            chunk_metadata = {
                **base_metadata,
                "chunk_index": chunk_index,
                "chunk_size": len(current_chunk),
                "chunk_type": "optimized",
                "paragraph_count": len([p for p in current_chunk.split('\n\n') if p.strip()])
            }

            chunks.append(DocumentChunk(current_chunk.strip(), chunk_metadata))

        # Log optimization results
        total_chars = sum(len(c.text) for c in chunks)
        avg_size = total_chars // max(len(chunks), 1)
        logger.info(f"Optimized chunking: {len(chunks)} chunks created (avg size: {avg_size} chars, total: {total_chars} chars)")

        return chunks


# Global processor instance
_document_processor = None


def get_document_processor() -> DocumentProcessor:
    """Get or create the global document processor instance."""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor
