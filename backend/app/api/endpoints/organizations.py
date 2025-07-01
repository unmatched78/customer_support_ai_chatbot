from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_database, get_current_user, get_current_organization
from app.db.models import Organization, User, APIKey, UserRole
from app.schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    UserCreate, UserUpdate, UserResponse,
    APIKeyCreate, APIKeyResponse, APIKeyCreateResponse,
    OrganizationStats
)
import hashlib
import secrets
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=OrganizationResponse)
async def get_current_organization(
    current_org: Organization = Depends(get_current_organization)
):
    """Get current organization details"""
    return current_org


@router.put("/", response_model=OrganizationResponse)
async def update_organization(
    org_update: OrganizationUpdate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization)
):
    """Update organization details (requires admin role)"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update organization"
        )
    
    # Update organization fields
    update_data = org_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_org, field, value)
    
    current_org.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_org)
    
    return current_org


@router.get("/stats", response_model=OrganizationStats)
async def get_organization_stats(
    current_org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_database)
):
    """Get organization usage statistics"""
    # This would typically involve complex queries
    # For now, return basic stats
    from app.db.models import Conversation, Message, APIUsageLog, KnowledgeBase, Document
    
    # Count active users
    active_users = db.query(User).filter(
        User.organization_id == current_org.id,
        User.is_active == True
    ).count()
    
    # Count active API keys
    active_api_keys = db.query(APIKey).filter(
        APIKey.organization_id == current_org.id,
        APIKey.is_active == True
    ).count()
    
    # Count knowledge bases and documents
    knowledge_bases_count = db.query(KnowledgeBase).filter(
        KnowledgeBase.organization_id == current_org.id
    ).count()
    
    total_documents = db.query(Document).filter(
        Document.organization_id == current_org.id
    ).count()
    
    # Basic usage stats (would be more complex in production)
    total_conversations = db.query(Conversation).filter(
        Conversation.organization_id == current_org.id
    ).count()
    
    total_messages = db.query(Message).filter(
        Message.organization_id == current_org.id
    ).count()
    
    return OrganizationStats(
        organization=current_org,
        usage_current_month={
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_api_calls": 0,
            "total_tokens_used": 0,
            "total_cost_cents": 0
        },
        usage_total={
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_api_calls": 0,
            "total_tokens_used": 0,
            "total_cost_cents": 0
        },
        active_users=active_users,
        active_api_keys=active_api_keys,
        knowledge_bases_count=knowledge_bases_count,
        total_documents=total_documents
    )


# User management endpoints
@router.get("/users", response_model=List[UserResponse])
async def list_organization_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_database)
):
    """List all users in the organization"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to list users"
        )
    
    users = db.query(User).filter(
        User.organization_id == current_org.id
    ).offset(skip).limit(limit).all()
    
    return users


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_database)
):
    """Create a new user in the organization"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create users"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        User.clerk_user_id == user_create.clerk_user_id
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this Clerk ID already exists"
        )
    
    # Check organization user limit
    current_user_count = db.query(User).filter(
        User.organization_id == current_org.id,
        User.is_active == True
    ).count()
    
    if current_user_count >= current_org.max_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization has reached the maximum number of users ({current_org.max_users})"
        )
    
    # Create new user
    new_user = User(
        **user_create.dict(),
        organization_id=current_org.id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_database)
):
    """Update a user in the organization"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update users"
        )
    
    # Get user
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == current_org.id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user


# API Key management endpoints
@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_database)
):
    """List all API keys for the organization"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to list API keys"
        )
    
    api_keys = db.query(APIKey).filter(
        APIKey.organization_id == current_org.id
    ).offset(skip).limit(limit).all()
    
    return api_keys


@router.post("/api-keys", response_model=APIKeyCreateResponse)
async def create_api_key(
    api_key_create: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_database)
):
    """Create a new API key"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create API keys"
        )
    
    # Check API key limit
    current_key_count = db.query(APIKey).filter(
        APIKey.organization_id == current_org.id,
        APIKey.is_active == True
    ).count()
    
    if current_key_count >= current_org.max_api_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization has reached the maximum number of API keys ({current_org.max_api_keys})"
        )
    
    # Generate API key
    api_key = f"sk_{current_org.slug}_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    key_prefix = api_key[:12]
    
    # Create API key record
    new_api_key = APIKey(
        **api_key_create.dict(),
        organization_id=current_org.id,
        created_by_user_id=current_user.id,
        key_hash=key_hash,
        key_prefix=key_prefix
    )
    
    db.add(new_api_key)
    db.commit()
    db.refresh(new_api_key)
    
    # Return response with full API key
    response = APIKeyCreateResponse(
        **new_api_key.__dict__,
        api_key=api_key
    )
    
    return response


@router.delete("/api-keys/{api_key_id}")
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
    db: Session = Depends(get_database)
):
    """Delete an API key"""
    if current_user.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete API keys"
        )
    
    # Get API key
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.organization_id == current_org.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Soft delete by deactivating
    api_key.is_active = False
    api_key.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "API key deactivated successfully"}