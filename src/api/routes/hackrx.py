"""HackRx API routes for the intelligent query retrieval system."""

import time
import asyncio
import tempfile
import os
import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from loguru import logger

from ..models.request import QueryRequest
from ..models.response import (
    QueryResponse, QueryAnswer, ClauseReference, 
    ProcessingMetadata, ProcessingSummary
)
from ...services.document_processor import get_document_processor
from ...services.retrieval_engine import get_retrieval_engine
from ...services.decision_engine import get_decision_engine
from ...core.gemini_client import get_gemini_client
from ...core.config import get_settings


router = APIRouter()


@router.post("/hackrx/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document file and return a temporary URL for processing.

    This endpoint accepts file uploads and stores them temporarily,
    returning a local file URL that can be used with the main analysis endpoint.
    """
    try:
        # Validate file type
        allowed_types = {
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/msword': '.doc',
            'text/plain': '.txt'
        }

        if file.content_type not in allowed_types:
            # Also check by filename extension
            filename_lower = file.filename.lower() if file.filename else ''
            allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']

            if not any(filename_lower.endswith(ext) for ext in allowed_extensions):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Allowed types: PDF, DOCX, DOC, TXT"
                )

        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()

        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 10MB limit"
            )

        # Create temporary file
        suffix = allowed_types.get(file.content_type, '.tmp')
        if suffix == '.tmp' and file.filename:
            # Try to get extension from filename
            ext = os.path.splitext(file.filename)[1].lower()
            if ext in ['.pdf', '.docx', '.doc', '.txt']:
                suffix = ext

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Create a file URL that the backend can access
        file_url = f"file://{temp_file_path}"

        logger.info(f"File uploaded successfully: {file.filename} -> {temp_file_path}")

        return {
            "success": True,
            "file_url": file_url,
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "message": "File uploaded successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.post("/hackrx/run", response_model=QueryResponse)
async def process_queries(request: QueryRequest) -> QueryResponse:
    """
    Process queries against a document using LLM-powered analysis.
    
    This endpoint:
    1. Downloads and processes the document from the blob URL
    2. Analyzes each question using Gemini AI
    3. Returns structured responses with explainability
    """
    start_time = time.time()
    settings = get_settings()
    
    try:
        logger.info(f"Processing {len(request.questions)} questions for document: {request.documents}")
        
        # Initialize services
        doc_processor = get_document_processor()
        retrieval_engine = await get_retrieval_engine()
        decision_engine = get_decision_engine()
        gemini_client = get_gemini_client()

        # Step 1: Process the document
        logger.info("Step 1: Processing document...")
        document_chunks = await doc_processor.process_blob_url(request.documents)

        if not document_chunks:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract content from the provided document"
            )

        logger.info(f"Document processed: {len(document_chunks)} chunks extracted")

        # Step 2: Store document in vector store
        logger.info("Step 2: Storing document in vector store...")
        document_id = f"doc_{hash(request.documents)}"  # Simple document ID
        storage_result = await retrieval_engine.store_document(document_chunks, document_id)

        if not storage_result["success"]:
            logger.warning(f"Partial storage success: {storage_result}")

        logger.info(f"Document stored: {storage_result['stored_chunks']} chunks in vector store")
        
        # Step 3: Process each question
        logger.info("Step 3: Processing questions...")
        answers = []
        successful_responses = 0

        for question in request.questions:
            try:
                answer = await process_single_question(
                    question, document_id, retrieval_engine, decision_engine, gemini_client, settings
                )
                answers.append(answer)
                successful_responses += 1
                
            except Exception as e:
                logger.error(f"Failed to process question '{question}': {e}")
                # Create error response for this question
                error_answer = QueryAnswer(
                    question=question,
                    isCovered=False,
                    conditions=[],
                    clause_reference=ClauseReference(page=None, clause_title="Error"),
                    rationale=f"Failed to process question due to error: {str(e)}",
                    confidence_score=0.0,
                    processing_metadata=ProcessingMetadata(
                        model_used=settings.llm_model,
                        embedding_model=settings.embedding_model,
                        chunks_analyzed=0,
                        total_tokens=0
                    )
                )
                answers.append(error_answer)
        
        # Step 4: Create response summary
        total_time = time.time() - start_time
        
        # Extract document metadata
        total_pages = None
        if document_chunks:
            page_metadata = [chunk.metadata.get('page') for chunk in document_chunks if chunk.metadata.get('page')]
            if page_metadata:
                total_pages = max(page_metadata)
        
        processing_summary = ProcessingSummary(
            total_questions=len(request.questions),
            successful_responses=successful_responses,
            total_processing_time=f"{total_time:.1f}s",
            document_pages_processed=total_pages
        )
        
        logger.info(f"Processing completed: {successful_responses}/{len(request.questions)} successful in {total_time:.1f}s")
        
        return QueryResponse(
            answers=answers,
            processing_summary=processing_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing queries: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


async def process_single_question(
    question: str,
    document_id: str,
    retrieval_engine,
    decision_engine,
    gemini_client,
    settings
) -> QueryAnswer:
    """
    Process a single question using advanced retrieval and decision analysis.

    Args:
        question: The question to process
        document_id: Document identifier for filtering
        retrieval_engine: Retrieval engine instance
        decision_engine: Advanced decision engine
        gemini_client: Gemini AI client
        settings: Application settings

    Returns:
        QueryAnswer with the analysis results
    """
    try:
        # Step 1: Analyze the question to understand intent
        logger.debug(f"Analyzing question: {question}")
        query_analysis = await gemini_client.analyze_query(question)

        # Step 2: Retrieve relevant chunks using vector search
        logger.debug(f"Retrieving relevant chunks for: {question[:50]}...")
        relevant_chunks = await retrieval_engine.retrieve_relevant_chunks(
            query=question,
            document_id=document_id,
            use_hybrid_search=True
        )

        # Step 3: Rerank chunks using LLM
        if len(relevant_chunks) > settings.rerank_top_k:
            logger.debug(f"Reranking {len(relevant_chunks)} chunks...")
            relevant_chunks = await retrieval_engine.rerank_chunks(question, relevant_chunks)

        # Step 4: Simplified fast analysis
        logger.debug(f"Performing fast analysis with {len(relevant_chunks)} relevant chunks")

        # If no relevant chunks found, use the original document chunks
        if not relevant_chunks:
            logger.warning("No relevant chunks found, using original document chunks")
            # Use the original processed chunks directly
            evaluation = await perform_fast_analysis_with_chunks(question, chunks[:3], gemini_client)
        else:
            evaluation = await perform_fast_analysis(question, relevant_chunks, gemini_client)
        
        # Step 5: Create enhanced structured response
        answer = QueryAnswer(
            question=question,
            isCovered=evaluation.get("isCovered", False),
            conditions=evaluation.get("conditions", []) + evaluation.get("limitations", []),
            clause_reference=ClauseReference(
                page=evaluation.get("clause_reference", {}).get("page"),
                clause_title=evaluation.get("clause_reference", {}).get("clause_title")
            ),
            rationale=evaluation.get("rationale", "No rationale provided"),
            confidence_score=evaluation.get("confidence_score", 0.0),
            processing_metadata=ProcessingMetadata(
                model_used=settings.llm_model,
                embedding_model=settings.embedding_model,
                chunks_analyzed=len(relevant_chunks),
                total_tokens=None  # Would be populated with actual token usage
            )
        )

        # Add advanced analysis metadata to rationale if available
        if evaluation.get("evidence_strength"):
            answer.rationale += f" [Evidence: {evaluation['evidence_strength']}]"
        if evaluation.get("completeness"):
            answer.rationale += f" [Completeness: {evaluation['completeness']}]"
        if evaluation.get("contradictions"):
            answer.rationale += f" [Contradictions found: {len(evaluation['contradictions'])}]"
        
        return answer
        
    except Exception as e:
        logger.error(f"Error processing question '{question}': {e}")
        raise


# Note: The old find_relevant_chunks function has been replaced
# with the advanced vector-based retrieval system in retrieval_engine.py


async def perform_fast_analysis(question: str, chunks: List[Dict], gemini_client) -> Dict[str, Any]:
    """
    Perform fast, simplified analysis without complex decision engine.

    Args:
        question: The question to analyze
        chunks: Relevant document chunks
        gemini_client: Gemini AI client

    Returns:
        Analysis result
    """
    try:
        # Combine top chunks for context
        context_text = "\n\n".join([chunk.get('text', '') for chunk in chunks[:3]])

        # Simple, direct analysis prompt
        analysis_prompt = f"""
        Based on the document content below, answer this question directly and clearly.

        Question: {question}

        Document Content:
        {context_text}

        Provide a JSON response with this exact format:
        {{
            "isCovered": true,
            "conditions": ["condition 1", "condition 2"],
            "rationale": "Clear explanation based on the document",
            "confidence_score": 0.9,
            "clause_reference": {{"page": 1, "clause_title": "Section Name"}}
        }}

        Guidelines:
        - Answer based ONLY on what's explicitly stated in the document
        - If coverage exists, set isCovered to true and list any conditions
        - If no coverage found, set isCovered to false
        - Provide a clear rationale explaining your answer
        - Set confidence between 0.7-0.95 based on clarity of information
        """

        response = await gemini_client.generate_content(analysis_prompt)

        try:
            # Try to parse JSON response
            result = json.loads(response.strip())

            # Validate required fields
            if "isCovered" not in result:
                result["isCovered"] = False
            if "conditions" not in result:
                result["conditions"] = []
            if "rationale" not in result:
                result["rationale"] = "Analysis completed based on document content"
            if "confidence_score" not in result:
                result["confidence_score"] = 0.8
            if "clause_reference" not in result:
                result["clause_reference"] = {"page": 1, "clause_title": "Document"}

            logger.info(f"Fast analysis completed for: {question}")
            return result

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, creating fallback response")

            # Fallback: analyze response text for key indicators
            response_lower = response.lower()
            is_covered = any(word in response_lower for word in ['yes', 'covered', 'included', 'available'])

            return {
                "isCovered": is_covered,
                "conditions": ["See document for specific conditions"],
                "rationale": f"Based on document analysis: {response[:200]}...",
                "confidence_score": 0.7,
                "clause_reference": {"page": 1, "clause_title": "Document"}
            }

    except Exception as e:
        logger.error(f"Fast analysis failed: {e}")
        return {
            "isCovered": False,
            "conditions": [],
            "rationale": f"Analysis error: {str(e)}",
            "confidence_score": 0.0,
            "clause_reference": {"page": None, "clause_title": None}
        }


async def perform_fast_analysis_with_chunks(question: str, chunks, gemini_client) -> Dict[str, Any]:
    """
    Perform fast analysis using document chunks directly.

    Args:
        question: The question to analyze
        chunks: Document chunks (DocumentChunk objects)
        gemini_client: Gemini AI client

    Returns:
        Analysis result
    """
    try:
        # Extract text from DocumentChunk objects
        if chunks and hasattr(chunks[0], 'text'):
            context_text = "\n\n".join([chunk.text for chunk in chunks])
        else:
            context_text = "No document content available"

        # Simple, direct analysis prompt
        analysis_prompt = f"""
        You are analyzing an insurance policy document. Answer this question based on the document content provided.

        Question: {question}

        Document Content:
        {context_text}

        Instructions:
        - Read the document content carefully
        - Answer based ONLY on what's explicitly stated
        - If the document covers the topic, explain the coverage and any conditions
        - If not covered, clearly state it's not covered
        - Be specific about waiting periods, conditions, or limitations

        Provide your answer in this JSON format:
        {{
            "isCovered": true,
            "conditions": ["specific condition 1", "specific condition 2"],
            "rationale": "Clear explanation based on the document text",
            "confidence_score": 0.9,
            "clause_reference": {{"page": 1, "clause_title": "Relevant Section"}}
        }}
        """

        response = await gemini_client.generate_content(analysis_prompt)

        try:
            # Clean the response to extract JSON
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:]
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3]

            result = json.loads(response_clean.strip())

            # Validate and fix required fields
            if "isCovered" not in result:
                result["isCovered"] = False
            if "conditions" not in result:
                result["conditions"] = []
            if "rationale" not in result:
                result["rationale"] = "Analysis completed based on document content"
            if "confidence_score" not in result:
                result["confidence_score"] = 0.8
            if "clause_reference" not in result:
                result["clause_reference"] = {"page": 1, "clause_title": "Document"}

            logger.info(f"Fast analysis with chunks completed for: {question}")
            return result

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, analyzing response text")

            # Fallback: analyze response text for key indicators
            response_lower = response.lower()

            # Look for coverage indicators
            is_covered = any(word in response_lower for word in [
                'yes', 'covered', 'included', 'available', 'provided', 'benefits'
            ])

            # Look for negative indicators
            if any(word in response_lower for word in [
                'not covered', 'excluded', 'not included', 'no coverage', 'not available'
            ]):
                is_covered = False

            # Extract conditions from response
            conditions = []
            if 'waiting period' in response_lower:
                conditions.append("Waiting period applies")
            if 'month' in response_lower:
                conditions.append("Time-based conditions apply")

            return {
                "isCovered": is_covered,
                "conditions": conditions,
                "rationale": f"Analysis based on document content: {response[:200]}...",
                "confidence_score": 0.8,
                "clause_reference": {"page": 1, "clause_title": "Document"}
            }

    except Exception as e:
        logger.error(f"Fast analysis with chunks failed: {e}")
        return {
            "isCovered": False,
            "conditions": [],
            "rationale": f"Analysis error: {str(e)}",
            "confidence_score": 0.0,
            "clause_reference": {"page": None, "clause_title": None}
        }
