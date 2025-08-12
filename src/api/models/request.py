"""Request models for the API."""

from typing import List
from pydantic import BaseModel, Field, HttpUrl, validator


class QueryRequest(BaseModel):
    """Request model for the main query endpoint."""
    
    documents: str = Field(
        ...,
        description="PDF Blob URL pointing to the document to analyze",
        example="https://example.com/document.pdf"
    )
    
    questions: List[str] = Field(
        ...,
        min_items=1,
        description="List of questions to ask about the document",
        example=[
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?"
        ]
    )
    
    @validator('questions')
    def validate_questions_length(cls, v):
        """Validate questions list length."""
        if len(v) > 10:  # Max questions per request
            raise ValueError('Maximum 10 questions allowed per request')
        return v
    
    @validator('questions')
    def validate_question_content(cls, v):
        """Validate individual question content."""
        for question in v:
            if not question.strip():
                raise ValueError('Questions cannot be empty')
            if len(question) > 500:
                raise ValueError('Questions must be less than 500 characters')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "documents": "https://storage.googleapis.com/example-bucket/insurance-policy.pdf",
                "questions": [
                    "What is the waiting period for pre-existing diseases (PED) to be covered?",
                    "Does this policy cover maternity expenses, and what are the conditions?",
                    "What are the exclusions for this insurance policy?"
                ]
            }
        }
