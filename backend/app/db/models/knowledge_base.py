from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"      # Uploaded, waiting to be processed
    PROCESSING = "processing" # Being processed (chunked, embedded)
    COMPLETED = "completed"   # Successfully processed and indexed
    FAILED = "failed"        # Processing failed
    ARCHIVED = "archived"    # Soft deleted


class DocumentType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    CSV = "csv"
    JSON = "json"
    URL = "url"              # Web page content
    API_DOCS = "api_docs"    # API documentation


class KnowledgeBase(Base):
    """
    Organization's knowledge base container
    Each organization can have multiple knowledge bases for different purposes
    """
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    slug = Column(String(100), nullable=False, index=True)  # URL-friendly identifier
    
    # Configuration
    settings = Column(JSON, default={})  # Embedding model, chunk size, etc.
    is_public = Column(Boolean, default=False)  # Can be accessed by API without auth
    
    # Statistics
    total_documents = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="knowledge_bases")
    created_by = relationship("User")
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    
    # Unique constraint: organization can't have duplicate knowledge base slugs
    __table_args__ = (
        {"schema": None},
    )


class Document(Base):
    """
    Individual documents within a knowledge base
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Document info
    title = Column(String(500), nullable=False)
    filename = Column(String(255))
    file_path = Column(String(1000))  # Path to stored file
    file_size_bytes = Column(Integer)
    file_hash = Column(String(64), index=True)  # SHA-256 hash for deduplication
    
    # Document type and processing
    document_type = Column(String(20), nullable=False)  # DocumentType enum
    status = Column(String(20), default=DocumentStatus.PENDING)  # DocumentStatus enum
    
    # Content
    raw_content = Column(Text)  # Original text content
    processed_content = Column(Text)  # Cleaned/processed content
    document_metadata = Column(JSON, default={})  # Author, creation date, etc.
    
    # Processing info
    processing_started_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))
    processing_error = Column(Text)
    
    # Statistics
    total_chunks = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    organization = relationship("Organization")
    uploaded_by = relationship("User")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """
    Text chunks from documents with vector embeddings for semantic search
    """
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Chunk content
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within document
    
    # Position in original document
    start_char = Column(Integer)
    end_char = Column(Integer)
    page_number = Column(Integer)  # For PDFs
    
    # Vector embedding for semantic search
    embedding = Column(LargeBinary)  # Stored as binary for efficiency
    embedding_model = Column(String(100))  # Model used for embedding
    
    # Metadata
    chunk_metadata = Column(JSON, default={})  # Headers, context, etc.
    token_count = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    organization = relationship("Organization")


class SearchQuery(Base):
    """
    Track search queries for analytics and improvement
    """
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=True, index=True)
    
    # Query details
    query_text = Column(Text, nullable=False)
    query_embedding = Column(LargeBinary)  # For similarity analysis
    
    # Results
    results_count = Column(Integer, default=0)
    top_result_score = Column(Float)  # Similarity score of best match
    
    # Context
    user_id = Column(Integer, ForeignKey("users.id"))  # If from authenticated user
    api_key_id = Column(Integer, ForeignKey("api_keys.id"))  # If from API
    conversation_id = Column(Integer, ForeignKey("conversations.id"))  # If from chat
    
    # Performance
    search_time_ms = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    organization = relationship("Organization")
    knowledge_base = relationship("KnowledgeBase")
    user = relationship("User")
    api_key = relationship("APIKey")


class KnowledgeBaseAccess(Base):
    """
    Track access to knowledge bases for analytics
    """
    __tablename__ = "knowledge_base_access"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Access details
    user_id = Column(Integer, ForeignKey("users.id"))
    api_key_id = Column(Integer, ForeignKey("api_keys.id"))
    access_type = Column(String(50))  # search, download, view, etc.
    
    # Metadata
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase")
    organization = relationship("Organization")
    user = relationship("User")
    api_key = relationship("APIKey")