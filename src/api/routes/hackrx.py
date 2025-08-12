"""HackRx API routes for the intelligent query retrieval system."""

import time
import asyncio
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from ..models.request import QueryRequest
from ..models.response import (
    QueryResponse, QueryAnswer, ClauseReference, 
    ProcessingMetadata, ProcessingSummary
)
from ...services.document_processor import get_document_processor
from ...core.gemini_client import get_gemini_client
from ...core.config import get_settings


router = APIRouter()


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
        
        # Step 2: Process each question
        logger.info("Step 2: Processing questions...")
        answers = []
        successful_responses = 0
        
        for question in request.questions:
            try:
                answer = await process_single_question(
                    question, document_chunks, gemini_client, settings
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
        
        # Step 3: Create response summary
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
    document_chunks: List, 
    gemini_client, 
    settings
) -> QueryAnswer:
    """
    Process a single question against the document chunks.
    
    Args:
        question: The question to process
        document_chunks: List of document chunks
        gemini_client: Gemini AI client
        settings: Application settings
        
    Returns:
        QueryAnswer with the analysis results
    """
    try:
        # Step 1: Analyze the question to understand intent
        logger.debug(f"Analyzing question: {question}")
        query_analysis = await gemini_client.analyze_query(question)
        
        # Step 2: Find relevant chunks (simple text matching for now)
        # In a full implementation, this would use vector similarity search
        relevant_chunks = find_relevant_chunks(question, document_chunks, query_analysis)
        
        # Step 3: Evaluate coverage using LLM
        logger.debug(f"Evaluating coverage with {len(relevant_chunks)} relevant chunks")
        evaluation = await gemini_client.evaluate_coverage(question, relevant_chunks)
        
        # Step 4: Create structured response
        answer = QueryAnswer(
            question=question,
            isCovered=evaluation.get("isCovered", False),
            conditions=evaluation.get("conditions", []),
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
        
        return answer
        
    except Exception as e:
        logger.error(f"Error processing question '{question}': {e}")
        raise


def find_relevant_chunks(question: str, document_chunks: List, query_analysis: dict) -> List[dict]:
    """
    Find relevant document chunks for a question.
    
    This is a simplified implementation using keyword matching.
    In a full implementation, this would use vector similarity search with Pinecone.
    
    Args:
        question: The question being asked
        document_chunks: All available document chunks
        query_analysis: Analysis of the question from LLM
        
    Returns:
        List of relevant chunks with metadata
    """
    try:
        # Extract key terms from question and analysis
        key_terms = set()
        key_terms.update(question.lower().split())
        key_terms.update(query_analysis.get("key_terms", []))
        key_terms.update(query_analysis.get("entities", []))
        
        # Score chunks based on keyword overlap
        scored_chunks = []
        
        for chunk in document_chunks:
            chunk_text = chunk.text.lower()
            score = 0
            
            # Count keyword matches
            for term in key_terms:
                if term.lower() in chunk_text:
                    score += 1
            
            if score > 0:
                scored_chunks.append({
                    "text": chunk.text,
                    "score": score,
                    "page": chunk.metadata.get("page"),
                    "chunk_index": chunk.metadata.get("chunk_index"),
                    "metadata": chunk.metadata
                })
        
        # Sort by score and return top chunks
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top 5 most relevant chunks
        top_chunks = scored_chunks[:5]
        
        logger.debug(f"Found {len(top_chunks)} relevant chunks out of {len(document_chunks)} total")
        
        return top_chunks
        
    except Exception as e:
        logger.error(f"Error finding relevant chunks: {e}")
        # Return first few chunks as fallback
        return [
            {
                "text": chunk.text,
                "score": 0,
                "page": chunk.metadata.get("page"),
                "chunk_index": chunk.metadata.get("chunk_index"),
                "metadata": chunk.metadata
            }
            for chunk in document_chunks[:3]
        ]
