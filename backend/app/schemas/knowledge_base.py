from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.db.models import DocumentStatus, DocumentType


# Knowledge Base schemas
class KnowledgeBaseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_public: bool = False


class KnowledgeBaseCreate(KnowledgeBaseBase):
    slug: str = Field(..., min_length=1, max_length=100, pattern=r'^[a-z0-9-]+$')


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class KnowledgeBaseResponse(KnowledgeBaseBase):
    id: int
    organization_id: int
    created_by_user_id: int
    slug: str
    total_documents: int
    total_chunks: int
    total_size_bytes: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Document schemas
class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    filename: Optional[str] = Field(None, max_length=255)
    document_type: DocumentType
    document_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DocumentCreate(DocumentBase):
    knowledge_base_id: int
    raw_content: Optional[str] = None
    file_path: Optional[str] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    document_metadata: Optional[Dict[str, Any]] = None
    status: Optional[DocumentStatus] = None


class DocumentResponse(DocumentBase):
    id: int
    knowledge_base_id: int
    organization_id: int
    uploaded_by_user_id: int
    file_size_bytes: Optional[int]
    file_hash: Optional[str]
    status: DocumentStatus
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    processing_error: Optional[str]
    total_chunks: int
    total_tokens: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Document Chunk schemas
class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    content: str
    chunk_index: int
    start_char: Optional[int]
    end_char: Optional[int]
    page_number: Optional[int]
    embedding_model: Optional[str]
    chunk_metadata: Optional[Dict[str, Any]]
    token_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Search schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    knowledge_base_id: Optional[int] = None
    limit: int = Field(10, ge=1, le=50)
    min_score: float = Field(0.0, ge=0.0, le=1.0)
    include_metadata: bool = True


class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    content: str
    score: float
    chunk_index: int
    page_number: Optional[int]
    metadata: Optional[Dict[str, Any]]


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: int
    knowledge_base_id: Optional[int]


# File upload schemas
class FileUploadRequest(BaseModel):
    knowledge_base_id: int
    title: Optional[str] = None
    document_type: Optional[DocumentType] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class FileUploadResponse(BaseModel):
    document_id: int
    filename: str
    file_size_bytes: int
    status: DocumentStatus
    message: str


# Bulk operations
class BulkDocumentDelete(BaseModel):
    document_ids: List[int] = Field(..., min_items=1, max_items=100)


class BulkOperationResponse(BaseModel):
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)


# Analytics schemas
class KnowledgeBaseStats(BaseModel):
    knowledge_base: KnowledgeBaseResponse
    documents_by_type: Dict[str, int]
    documents_by_status: Dict[str, int]
    total_size_mb: float
    avg_processing_time_seconds: Optional[float]
    search_queries_last_30_days: int
    most_searched_terms: List[Dict[str, Any]]


class DocumentProcessingStatus(BaseModel):
    document_id: int
    status: DocumentStatus
    progress_percentage: int
    processing_started_at: Optional[datetime]
    estimated_completion_at: Optional[datetime]
    error_message: Optional[str]