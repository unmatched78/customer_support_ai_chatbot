from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.db.models import OrganizationPlan, OrganizationStatus, UserRole, APIKeyScope


# Organization schemas
class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    branding: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OrganizationCreate(OrganizationBase):
    slug: str = Field(..., min_length=1, max_length=100, pattern=r'^[a-z0-9-]+$')
    plan: OrganizationPlan = OrganizationPlan.FREE


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    settings: Optional[Dict[str, Any]] = None
    branding: Optional[Dict[str, Any]] = None
    max_users: Optional[int] = Field(None, ge=1)
    max_api_keys: Optional[int] = Field(None, ge=1)
    max_conversations_per_month: Optional[int] = Field(None, ge=0)
    max_knowledge_base_size_mb: Optional[int] = Field(None, ge=0)


class OrganizationResponse(OrganizationBase):
    id: int
    slug: str
    plan: OrganizationPlan
    status: OrganizationStatus
    trial_ends_at: Optional[datetime]
    subscription_id: Optional[str]
    max_users: int
    max_api_keys: int
    max_conversations_per_month: int
    max_knowledge_base_size_mb: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserCreate(UserBase):
    clerk_user_id: str = Field(..., max_length=255)
    role: UserRole = UserRole.MEMBER


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    clerk_user_id: str
    organization_id: int
    role: UserRole
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# API Key schemas
class APIKeyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scopes: List[APIKeyScope] = Field(default_factory=lambda: [APIKeyScope.READ])
    rate_limit_per_minute: int = Field(60, ge=1, le=10000)
    rate_limit_per_hour: int = Field(1000, ge=1, le=100000)
    rate_limit_per_day: int = Field(10000, ge=1, le=1000000)


class APIKeyCreate(APIKeyBase):
    expires_at: Optional[datetime] = None


class APIKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    scopes: Optional[List[APIKeyScope]] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=10000)
    rate_limit_per_hour: Optional[int] = Field(None, ge=1, le=100000)
    rate_limit_per_day: Optional[int] = Field(None, ge=1, le=1000000)
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class APIKeyResponse(APIKeyBase):
    id: int
    organization_id: int
    created_by_user_id: int
    key_prefix: str
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class APIKeyCreateResponse(APIKeyResponse):
    """Response when creating a new API key - includes the full key"""
    api_key: str = Field(..., description="The full API key - save this as it won't be shown again")


# Usage analytics schemas
class UsageStats(BaseModel):
    total_conversations: int = 0
    total_messages: int = 0
    total_api_calls: int = 0
    total_tokens_used: int = 0
    total_cost_cents: int = 0


class OrganizationStats(BaseModel):
    organization: OrganizationResponse
    usage_current_month: UsageStats
    usage_total: UsageStats
    active_users: int
    active_api_keys: int
    knowledge_bases_count: int
    total_documents: int