from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    ARCHIVED = "archived"


class ConversationChannel(str, enum.Enum):
    WEB_CHAT = "web_chat"
    API = "api"
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Session & customer info
    session_id = Column(String, unique=True, index=True, nullable=False)
    customer_email = Column(String, index=True)
    customer_name = Column(String)
    customer_id = Column(String, index=True)  # External customer ID
    
    # Conversation details
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    channel = Column(Enum(ConversationChannel), default=ConversationChannel.WEB_CHAT)
    priority = Column(String, default="normal")  # low, normal, high, urgent
    
    # Assignment
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"))  # Human agent
    assigned_at = Column(DateTime(timezone=True))
    
    # AI & automation
    ai_enabled = Column(Boolean, default=True)
    system_prompt_id = Column(Integer, ForeignKey("system_prompts.id"))
    
    # Analytics
    first_response_time_seconds = Column(Integer)  # Time to first AI/human response
    resolution_time_seconds = Column(Integer)      # Time to resolution
    customer_satisfaction_score = Column(Integer)  # 1-5 rating
    
    # Metadata
    conversation_metadata = Column(JSON, default={})  # Custom fields, tags, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="conversations")
    assigned_to = relationship("User")
    system_prompt = relationship("SystemPrompt")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    support_actions = relationship("SupportAction", back_populates="conversation", cascade="all, delete-orphan")


class MessageSenderType(str, enum.Enum):
    CUSTOMER = "customer"
    AI = "ai"
    HUMAN_AGENT = "human_agent"
    SYSTEM = "system"


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Message content
    content = Column(Text, nullable=False)
    content_type = Column(String, default="text")  # text, markdown, html
    
    # Sender info
    sender_type = Column(Enum(MessageSenderType), nullable=False)
    sender_id = Column(String)  # User ID for human agents, customer ID for customers
    sender_name = Column(String)  # Display name
    
    # AI-specific fields
    ai_model = Column(String)  # Model used for AI responses
    ai_confidence = Column(Integer)  # 0-100 confidence score
    ai_tools_used = Column(JSON)  # List of MCP tools used
    
    # Message metadata
    message_metadata = Column(JSON, default={})  # Additional data, attachments, etc.
    
    # Performance tracking
    processing_time_ms = Column(Integer)  # Time to generate response
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    organization = relationship("Organization")


class SystemPrompt(Base):
    __tablename__ = "system_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Prompt details
    name = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    description = Column(Text)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Default prompt for new conversations
    department = Column(String, default="general")  # general, billing, technical, etc.
    
    # AI model settings
    model_settings = Column(JSON, default={})  # Temperature, max tokens, etc.
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="system_prompts")
    created_by = relationship("User")
    conversations = relationship("Conversation", back_populates="system_prompt")


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Customer identification
    external_id = Column(String(255), index=True)  # ID from customer's system
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255))
    phone = Column(String(50))
    
    # Subscription & billing (for the customer's customers)
    subscription_status = Column(String(50))  # active, cancelled, trial, etc.
    subscription_plan = Column(String(100))
    total_spent = Column(String(50))  # Store as string to avoid float precision issues
    
    # Customer metadata
    customer_metadata = Column(JSON, default={})  # Custom fields, tags, preferences
    
    # Analytics
    total_conversations = Column(Integer, default=0)
    last_conversation_at = Column(DateTime(timezone=True))
    satisfaction_score = Column(Integer)  # Average satisfaction
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")


class SupportActionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SupportAction(Base):
    __tablename__ = "support_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Action details
    action_type = Column(String(100), nullable=False)  # refund, cancel_subscription, update_plan, etc.
    action_data = Column(JSON, default={})  # Store action-specific data
    
    # Execution
    status = Column(Enum(SupportActionStatus), default=SupportActionStatus.PENDING)
    executed_by_user_id = Column(Integer, ForeignKey("users.id"))  # Human agent who executed
    executed_by_ai = Column(Boolean, default=False)  # Whether executed by AI
    
    # Results
    result_data = Column(JSON, default={})  # Results of the action
    error_message = Column(Text)  # Error details if failed
    
    # Timestamps
    executed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="support_actions")
    organization = relationship("Organization")
    executed_by = relationship("User")