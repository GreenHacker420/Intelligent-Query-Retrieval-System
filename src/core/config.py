"""Configuration management for the Intelligent Query Retrieval System."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Configuration
    app_name: str = Field(default="Intelligent Query Retrieval System", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Gemini AI Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    
    # Pinecone Configuration
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(default="hackrx-documents", env="PINECONE_INDEX_NAME")
    
    # Processing Configuration (optimized for speed)
    max_chunk_size: int = Field(default=1024, env="MAX_CHUNK_SIZE")
    chunk_overlap: int = Field(default=128, env="CHUNK_OVERLAP")
    max_retrieval_results: int = Field(default=10, env="MAX_RETRIEVAL_RESULTS")  # Reduced for speed
    rerank_top_k: int = Field(default=3, env="RERANK_TOP_K")  # Reduced for speed
    max_document_size_mb: int = Field(default=50, env="MAX_DOCUMENT_SIZE_MB")
    
    # API Configuration
    max_questions_per_request: int = Field(default=10, env="MAX_QUESTIONS_PER_REQUEST")
    request_timeout_seconds: int = Field(default=300, env="REQUEST_TIMEOUT_SECONDS")
    
    # Cache Configuration
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    # Model Configuration
    embedding_model: str = "text-embedding-004"
    llm_model: str = "gemini-2.0-flash"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
