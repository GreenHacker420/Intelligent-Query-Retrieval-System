"""Response models for the API."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ClauseReference(BaseModel):
    """Reference to a specific clause in the document."""
    
    page: Optional[int] = Field(
        None,
        description="Page number where the clause is found",
        example=12
    )
    
    clause_title: Optional[str] = Field(
        None,
        description="Title or description of the relevant clause",
        example="Maternity Benefits"
    )


class ProcessingMetadata(BaseModel):
    """Metadata about the processing of the query."""
    
    model_used: str = Field(
        ...,
        description="The LLM model used for processing",
        example="gemini-2.0-flash"
    )
    
    embedding_model: str = Field(
        ...,
        description="The embedding model used",
        example="text-embedding-004"
    )
    
    chunks_analyzed: int = Field(
        ...,
        description="Number of document chunks analyzed",
        example=5
    )
    
    total_tokens: Optional[int] = Field(
        None,
        description="Total tokens used in processing",
        example=1247
    )


class QueryAnswer(BaseModel):
    """Answer to a single query."""
    
    question: str = Field(
        ...,
        description="The original question asked",
        example="Does this policy cover maternity expenses, and what are the conditions?"
    )
    
    isCovered: bool = Field(
        ...,
        description="Whether the queried topic is covered by the document",
        example=True
    )
    
    conditions: List[str] = Field(
        default_factory=list,
        description="List of conditions or requirements if any",
        example=[
            "At least 24 months of continuous coverage",
            "Limited to two deliveries or terminations"
        ]
    )
    
    clause_reference: ClauseReference = Field(
        ...,
        description="Reference to the relevant clause in the document"
    )
    
    rationale: str = Field(
        ...,
        description="Clear explanation of the decision and reasoning",
        example="The clause states coverage is provided if the insured has been continuously covered for 24 months."
    )
    
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the answer (0.0 to 1.0)",
        example=0.92
    )
    
    processing_metadata: ProcessingMetadata = Field(
        ...,
        description="Metadata about how this query was processed"
    )


class ProcessingSummary(BaseModel):
    """Summary of the overall processing."""
    
    total_questions: int = Field(
        ...,
        description="Total number of questions processed",
        example=2
    )
    
    successful_responses: int = Field(
        ...,
        description="Number of questions that were successfully processed",
        example=2
    )
    
    total_processing_time: str = Field(
        ...,
        description="Total time taken to process all queries",
        example="3.2s"
    )
    
    document_pages_processed: Optional[int] = Field(
        None,
        description="Number of document pages that were processed",
        example=45
    )


class QueryResponse(BaseModel):
    """Response model for the main query endpoint."""
    
    answers: List[QueryAnswer] = Field(
        ...,
        description="List of answers corresponding to the input questions"
    )
    
    processing_summary: ProcessingSummary = Field(
        ...,
        description="Summary of the processing operation"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "answers": [
                    {
                        "question": "Does this policy cover maternity expenses, and what are the conditions?",
                        "isCovered": True,
                        "conditions": [
                            "At least 24 months of continuous coverage",
                            "Limited to two deliveries or terminations"
                        ],
                        "clause_reference": {
                            "page": 12,
                            "clause_title": "Maternity Benefits"
                        },
                        "rationale": "The clause states coverage is provided if the insured has been continuously covered for 24 months.",
                        "confidence_score": 0.92,
                        "processing_metadata": {
                            "model_used": "gemini-2.0-flash",
                            "embedding_model": "text-embedding-004",
                            "chunks_analyzed": 5,
                            "total_tokens": 1247
                        }
                    }
                ],
                "processing_summary": {
                    "total_questions": 1,
                    "successful_responses": 1,
                    "total_processing_time": "3.2s",
                    "document_pages_processed": 45
                }
            }
        }
