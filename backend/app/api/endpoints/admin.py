from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.api.deps import get_database
from app.db.models import SystemPrompt, Conversation, Message, SupportAction, Customer
from sqlalchemy import func, desc
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class SystemPromptCreate(BaseModel):
    name: str = Field(..., description="Prompt name")
    content: str = Field(..., description="Prompt content")
    description: str = Field(None, description="Prompt description")
    department: str = Field("general", description="Department")


class SystemPromptUpdate(BaseModel):
    content: str = Field(None, description="Prompt content")
    description: str = Field(None, description="Prompt description")
    is_active: bool = Field(None, description="Is prompt active")
    department: str = Field(None, description="Department")


@router.get("/prompts", response_model=List[Dict[str, Any]])
async def get_system_prompts(
    db: Session = Depends(get_database)
):
    """Get all system prompts"""
    try:
        prompts = db.query(SystemPrompt).order_by(desc(SystemPrompt.created_at)).all()
        return [
            {
                "id": prompt.id,
                "name": prompt.name,
                "content": prompt.content,
                "description": prompt.description,
                "is_active": prompt.is_active,
                "department": prompt.department,
                "created_at": prompt.created_at.isoformat(),
                "updated_at": prompt.updated_at.isoformat() if prompt.updated_at else None
            }
            for prompt in prompts
        ]
    except Exception as e:
        logger.error(f"Error getting system prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompts", response_model=Dict[str, Any])
async def create_system_prompt(
    request: SystemPromptCreate,
    db: Session = Depends(get_database)
):
    """Create a new system prompt"""
    try:
        # Check if prompt name already exists
        existing = db.query(SystemPrompt).filter(SystemPrompt.name == request.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Prompt name already exists")
        
        prompt = SystemPrompt(
            name=request.name,
            content=request.content,
            description=request.description,
            department=request.department
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        
        return {
            "id": prompt.id,
            "name": prompt.name,
            "content": prompt.content,
            "description": prompt.description,
            "is_active": prompt.is_active,
            "department": prompt.department,
            "created_at": prompt.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating system prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/prompts/{prompt_id}", response_model=Dict[str, Any])
async def update_system_prompt(
    prompt_id: int,
    request: SystemPromptUpdate,
    db: Session = Depends(get_database)
):
    """Update a system prompt"""
    try:
        prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        if request.content is not None:
            prompt.content = request.content
        if request.description is not None:
            prompt.description = request.description
        if request.is_active is not None:
            prompt.is_active = request.is_active
        if request.department is not None:
            prompt.department = request.department
        
        db.commit()
        db.refresh(prompt)
        
        return {
            "id": prompt.id,
            "name": prompt.name,
            "content": prompt.content,
            "description": prompt.description,
            "is_active": prompt.is_active,
            "department": prompt.department,
            "updated_at": prompt.updated_at.isoformat() if prompt.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating system prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/prompts/{prompt_id}")
async def delete_system_prompt(
    prompt_id: int,
    db: Session = Depends(get_database)
):
    """Delete a system prompt"""
    try:
        prompt = db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        db.delete(prompt)
        db.commit()
        
        return {"message": "Prompt deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting system prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics(
    db: Session = Depends(get_database)
):
    """Get conversation analytics"""
    try:
        # Total conversations
        total_conversations = db.query(Conversation).count()
        
        # Active conversations
        active_conversations = db.query(Conversation).filter(
            Conversation.status == "active"
        ).count()
        
        # Escalated conversations
        escalated_conversations = db.query(Conversation).filter(
            Conversation.status == "escalated"
        ).count()
        
        # Resolved conversations
        resolved_conversations = db.query(Conversation).filter(
            Conversation.status == "resolved"
        ).count()
        
        # Total messages
        total_messages = db.query(Message).count()
        
        # AI messages
        ai_messages = db.query(Message).filter(Message.sender_type == "ai").count()
        
        # Customer messages
        customer_messages = db.query(Message).filter(Message.sender_type == "customer").count()
        
        # Support actions
        total_actions = db.query(SupportAction).count()
        refund_actions = db.query(SupportAction).filter(
            SupportAction.action_type == "refund"
        ).count()
        subscription_actions = db.query(SupportAction).filter(
            SupportAction.action_type.like("subscription_%")
        ).count()
        
        # Recent conversations
        recent_conversations = db.query(Conversation).order_by(
            desc(Conversation.created_at)
        ).limit(10).all()
        
        recent_conv_data = []
        for conv in recent_conversations:
            message_count = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).count()
            recent_conv_data.append({
                "id": conv.id,
                "session_id": conv.session_id,
                "customer_email": conv.customer_email,
                "status": conv.status,
                "message_count": message_count,
                "created_at": conv.created_at.isoformat()
            })
        
        return {
            "conversations": {
                "total": total_conversations,
                "active": active_conversations,
                "escalated": escalated_conversations,
                "resolved": resolved_conversations
            },
            "messages": {
                "total": total_messages,
                "ai_messages": ai_messages,
                "customer_messages": customer_messages
            },
            "actions": {
                "total": total_actions,
                "refunds": refund_actions,
                "subscription_changes": subscription_actions
            },
            "recent_conversations": recent_conv_data
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=List[Dict[str, Any]])
async def get_all_conversations(
    limit: int = 50,
    offset: int = 0,
    status: str = None,
    db: Session = Depends(get_database)
):
    """Get all conversations with pagination"""
    try:
        query = db.query(Conversation)
        
        if status:
            query = query.filter(Conversation.status == status)
        
        conversations = query.order_by(desc(Conversation.created_at)).offset(offset).limit(limit).all()
        
        result = []
        for conv in conversations:
            message_count = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).count()
            
            last_message = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(desc(Message.created_at)).first()
            
            result.append({
                "id": conv.id,
                "session_id": conv.session_id,
                "customer_email": conv.customer_email,
                "customer_name": conv.customer_name,
                "status": conv.status,
                "message_count": message_count,
                "last_message": last_message.content if last_message else None,
                "last_message_at": last_message.created_at.isoformat() if last_message else None,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers", response_model=List[Dict[str, Any]])
async def get_customers(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_database)
):
    """Get all customers"""
    try:
        customers = db.query(Customer).order_by(desc(Customer.created_at)).offset(offset).limit(limit).all()
        
        result = []
        for customer in customers:
            conversation_count = db.query(Conversation).filter(
                Conversation.customer_email == customer.email
            ).count()
            
            result.append({
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "phone": customer.phone,
                "subscription_status": customer.subscription_status,
                "subscription_plan": customer.subscription_plan,
                "total_spent": customer.total_spent,
                "conversation_count": conversation_count,
                "created_at": customer.created_at.isoformat(),
                "updated_at": customer.updated_at.isoformat() if customer.updated_at else None
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))