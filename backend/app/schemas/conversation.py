from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.db.models import (
    ConversationStatus, ConversationChannel, MessageSenderType, SupportActionStatus
)


# Conversation schemas
class ConversationBase(BaseModel):
    customer_email: Optional[EmailStr] = None
    customer_name: Optional[str] = Field(None, max_length=255)
    customer_id: Optional[str] = Field(None, max_length=255)
    channel: ConversationChannel = ConversationChannel.WEB_CHAT
    priority: str = Field("normal", pattern=r'^(low|normal|high|urgent)$')
    ai_enabled: bool = True


class ConversationCreate(ConversationBase):
    session_id: str = Field(..., min_length=1, max_length=255)
    system_prompt_id: Optional[int] = None


class ConversationUpdate(BaseModel):
    customer_name: Optional[str] = Field(None, max_length=255)
    customer_id: Optional[str] = Field(None, max_length=255)
    status: Optional[ConversationStatus] = None
    priority: Optional[str] = Field(None, pattern=r'^(low|normal|high|urgent)$')
    assigned_to_user_id: Optional[int] = None
    ai_enabled: Optional[bool] = None
    system_prompt_id: Optional[int] = None
    conversation_metadata: Optional[Dict[str, Any]] = None
    customer_satisfaction_score: Optional[int] = Field(None, ge=1, le=5)


class ConversationResponse(ConversationBase):
    id: int
    organization_id: int
    session_id: str
    status: ConversationStatus
    assigned_to_user_id: Optional[int]
    system_prompt_id: Optional[int]
    first_response_time_seconds: Optional[int]
    resolution_time_seconds: Optional[int]
    customer_satisfaction_score: Optional[int]
    conversation_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Message schemas
class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    content_type: str = Field("text", pattern=r'^(text|markdown|html)$')
    sender_type: MessageSenderType
    sender_name: Optional[str] = Field(None, max_length=255)


class MessageCreate(MessageBase):
    conversation_id: int
    sender_id: Optional[str] = Field(None, max_length=255)
    message_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    content_type: Optional[str] = Field(None, pattern=r'^(text|markdown|html)$')
    message_metadata: Optional[Dict[str, Any]] = None


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    organization_id: int
    sender_id: Optional[str]
    ai_model: Optional[str]
    ai_confidence: Optional[int]
    ai_tools_used: Optional[List[str]]
    message_metadata: Optional[Dict[str, Any]]
    processing_time_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# System Prompt schemas
class SystemPromptBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    description: Optional[str] = None
    is_active: bool = True
    is_default: bool = False
    department: str = Field("general", max_length=100)
    model_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SystemPromptCreate(SystemPromptBase):
    pass


class SystemPromptUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    department: Optional[str] = Field(None, max_length=100)
    model_settings: Optional[Dict[str, Any]] = None


class SystemPromptResponse(SystemPromptBase):
    id: int
    organization_id: int
    created_by_user_id: int
    usage_count: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Support Action schemas
class SupportActionBase(BaseModel):
    action_type: str = Field(..., min_length=1, max_length=100)
    action_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SupportActionCreate(SupportActionBase):
    conversation_id: int


class SupportActionUpdate(BaseModel):
    status: Optional[SupportActionStatus] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class SupportActionResponse(SupportActionBase):
    id: int
    conversation_id: int
    organization_id: int
    status: SupportActionStatus
    executed_by_user_id: Optional[int]
    executed_by_ai: bool
    result_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    executed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Customer schemas
class CustomerBase(BaseModel):
    email: EmailStr
    name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    subscription_status: Optional[str] = Field(None, max_length=50)
    subscription_plan: Optional[str] = Field(None, max_length=100)
    total_spent: Optional[str] = Field(None, max_length=50)
    customer_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CustomerCreate(CustomerBase):
    external_id: Optional[str] = Field(None, max_length=255)


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    subscription_status: Optional[str] = Field(None, max_length=50)
    subscription_plan: Optional[str] = Field(None, max_length=100)
    total_spent: Optional[str] = Field(None, max_length=50)
    customer_metadata: Optional[Dict[str, Any]] = None


class CustomerResponse(CustomerBase):
    id: int
    organization_id: int
    external_id: Optional[str]
    total_conversations: int
    last_conversation_at: Optional[datetime]
    satisfaction_score: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Chat API schemas (for external clients)
class ChatStartRequest(BaseModel):
    customer_email: Optional[EmailStr] = None
    customer_name: Optional[str] = None
    customer_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChatStartResponse(BaseModel):
    session_id: str
    conversation_id: int
    message: str = "Chat session started successfully"


class ChatMessageRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=4000)
    sender_name: Optional[str] = None


class ChatMessageResponse(BaseModel):
    message_id: int
    response: str
    confidence: Optional[int]
    suggested_actions: Optional[List[str]]
    processing_time_ms: Optional[int]


# Analytics schemas
class ConversationAnalytics(BaseModel):
    total_conversations: int
    active_conversations: int
    resolved_conversations: int
    escalated_conversations: int
    avg_first_response_time_seconds: Optional[float]
    avg_resolution_time_seconds: Optional[float]
    avg_satisfaction_score: Optional[float]
    conversations_by_channel: Dict[str, int]
    conversations_by_priority: Dict[str, int]


class MessageAnalytics(BaseModel):
    total_messages: int
    messages_by_sender_type: Dict[str, int]
    avg_ai_confidence: Optional[float]
    avg_processing_time_ms: Optional[float]
    most_used_ai_tools: List[Dict[str, Any]]