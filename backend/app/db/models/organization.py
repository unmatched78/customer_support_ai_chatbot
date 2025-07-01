from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class OrganizationPlan(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class OrganizationStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"


class Organization(Base):
    """
    Multi-tenant organization model - the core of tenant isolation
    Each organization represents a customer company using our SaaS platform
    """
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)  # URL-friendly identifier
    domain = Column(String(255), index=True)  # Optional custom domain
    
    # Subscription & billing
    plan = Column(Enum(OrganizationPlan), default=OrganizationPlan.FREE)
    status = Column(Enum(OrganizationStatus), default=OrganizationStatus.TRIAL)
    trial_ends_at = Column(DateTime(timezone=True))
    subscription_id = Column(String(255))  # External billing system ID
    
    # Configuration
    settings = Column(JSON, default={})  # Flexible settings storage
    branding = Column(JSON, default={})  # Logo, colors, custom CSS
    
    # Limits based on plan
    max_users = Column(Integer, default=5)
    max_api_keys = Column(Integer, default=3)
    max_conversations_per_month = Column(Integer, default=1000)
    max_knowledge_base_size_mb = Column(Integer, default=100)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="organization", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="organization", cascade="all, delete-orphan")
    knowledge_bases = relationship("KnowledgeBase", back_populates="organization", cascade="all, delete-orphan")
    system_prompts = relationship("SystemPrompt", back_populates="organization", cascade="all, delete-orphan")


class UserRole(str, enum.Enum):
    OWNER = "owner"          # Full access, billing management
    ADMIN = "admin"          # Full access except billing
    MEMBER = "member"        # Standard user access
    VIEWER = "viewer"        # Read-only access
    API_USER = "api_user"    # API-only access (for service accounts)


class User(Base):
    """
    Users belong to organizations and have roles within them
    Integrates with Clerk for authentication
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    clerk_user_id = Column(String(255), unique=True, index=True, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # User info (synced from Clerk)
    email = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(String(500))
    
    # Role & permissions
    role = Column(Enum(UserRole), default=UserRole.MEMBER)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role}) in {self.organization.name}>"


class APIKeyScope(str, enum.Enum):
    READ = "read"                    # Read conversations, analytics
    WRITE = "write"                  # Create conversations, send messages
    ADMIN = "admin"                  # Manage settings, users
    KNOWLEDGE_BASE = "knowledge_base" # Manage knowledge base
    FULL_ACCESS = "full_access"      # All permissions


class APIKey(Base):
    """
    API keys for programmatic access to the platform
    Each organization can have multiple API keys with different scopes
    """
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Key details
    name = Column(String(255), nullable=False)  # Human-readable name
    key_hash = Column(String(255), unique=True, index=True, nullable=False)  # Hashed API key
    key_prefix = Column(String(20), index=True)  # First few chars for identification
    
    # Permissions & limits
    scopes = Column(JSON, default=[])  # List of APIKeyScope values
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))  # Optional expiration
    last_used_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="api_keys")
    created_by = relationship("User")
    usage_logs = relationship("APIUsageLog", back_populates="api_key", cascade="all, delete-orphan")


class APIUsageLog(Base):
    """
    Track API usage for billing and analytics
    """
    __tablename__ = "api_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Request details
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer)
    
    # Usage tracking
    tokens_used = Column(Integer, default=0)  # For AI API calls
    cost_cents = Column(Integer, default=0)   # Cost in cents
    
    # Metadata
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    api_key = relationship("APIKey", back_populates="usage_logs")
    organization = relationship("Organization")