from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
from typing import Dict, Any, List
import google.generativeai as genai
from app.core.config import settings
from app.db import get_db
from app.db.models import Customer, SupportAction, SystemPrompt
from sqlalchemy.orm import Session
import json
from datetime import datetime
from pydantic import BaseModel, Field


# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# Create MCP server
mcp = FastMCP("Customer Support AI")


class CustomerInfo(BaseModel):
    email: str
    name: str
    subscription_status: str
    subscription_plan: str
    total_spent: str


class RefundRequest(BaseModel):
    amount: str = Field(description="Refund amount")
    reason: str = Field(description="Reason for refund")
    order_id: str = Field(description="Order ID to refund")


class SubscriptionAction(BaseModel):
    action: str = Field(description="Action to perform: cancel, pause, or change_plan")
    new_plan: str = Field(default="", description="New plan name if changing plan")


@mcp.resource("customer://{email}")
def get_customer_info(email: str) -> CustomerInfo:
    """Get customer information by email"""
    db = next(get_db())
    try:
        customer = db.query(Customer).filter(Customer.email == email).first()
        if customer:
            return CustomerInfo(
                email=customer.email,
                name=customer.name or "Unknown",
                subscription_status=customer.subscription_status or "unknown",
                subscription_plan=customer.subscription_plan or "none",
                total_spent=customer.total_spent or "0"
            )
        else:
            # Return default customer info if not found
            return CustomerInfo(
                email=email,
                name="Unknown",
                subscription_status="unknown",
                subscription_plan="none",
                total_spent="0"
            )
    finally:
        db.close()


@mcp.resource("system-prompts://active")
def get_active_system_prompts() -> str:
    """Get all active system prompts"""
    db = next(get_db())
    try:
        prompts = db.query(SystemPrompt).filter(SystemPrompt.is_active == True).all()
        prompt_data = []
        for prompt in prompts:
            prompt_data.append({
                "name": prompt.name,
                "content": prompt.content,
                "department": prompt.department,
                "description": prompt.description
            })
        return json.dumps(prompt_data, indent=2)
    finally:
        db.close()


@mcp.tool()
def process_refund(customer_email: str, refund_data: RefundRequest, ctx: Context) -> Dict[str, Any]:
    """Process a refund request for a customer"""
    db = next(get_db())
    try:
        # Log the refund action
        action = SupportAction(
            conversation_id=0,  # Will be updated when integrated with conversation
            action_type="refund",
            action_data={
                "customer_email": customer_email,
                "amount": refund_data.amount,
                "reason": refund_data.reason,
                "order_id": refund_data.order_id
            },
            status="completed",
            executed_at=datetime.utcnow()
        )
        db.add(action)
        db.commit()
        
        ctx.info(f"Processed refund of {refund_data.amount} for customer {customer_email}")
        
        return {
            "success": True,
            "message": f"Refund of {refund_data.amount} has been processed for order {refund_data.order_id}",
            "refund_id": f"REF-{action.id}",
            "amount": refund_data.amount,
            "status": "completed"
        }
    except Exception as e:
        ctx.error(f"Failed to process refund: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to process refund: {str(e)}"
        }
    finally:
        db.close()


@mcp.tool()
def manage_subscription(customer_email: str, subscription_action: SubscriptionAction, ctx: Context) -> Dict[str, Any]:
    """Manage customer subscription (cancel, pause, or change plan)"""
    db = next(get_db())
    try:
        customer = db.query(Customer).filter(Customer.email == customer_email).first()
        if not customer:
            return {
                "success": False,
                "message": "Customer not found"
            }
        
        # Log the subscription action
        action = SupportAction(
            conversation_id=0,  # Will be updated when integrated with conversation
            action_type=f"subscription_{subscription_action.action}",
            action_data={
                "customer_email": customer_email,
                "action": subscription_action.action,
                "old_plan": customer.subscription_plan,
                "new_plan": subscription_action.new_plan if subscription_action.action == "change_plan" else None
            },
            status="completed",
            executed_at=datetime.utcnow()
        )
        db.add(action)
        
        # Update customer subscription
        if subscription_action.action == "cancel":
            customer.subscription_status = "cancelled"
            message = "Subscription has been cancelled successfully"
        elif subscription_action.action == "pause":
            customer.subscription_status = "paused"
            message = "Subscription has been paused successfully"
        elif subscription_action.action == "change_plan":
            customer.subscription_plan = subscription_action.new_plan
            message = f"Subscription plan changed to {subscription_action.new_plan}"
        
        db.commit()
        
        ctx.info(f"Subscription {subscription_action.action} completed for {customer_email}")
        
        return {
            "success": True,
            "message": message,
            "action_id": f"SUB-{action.id}",
            "new_status": customer.subscription_status,
            "new_plan": customer.subscription_plan
        }
    except Exception as e:
        ctx.error(f"Failed to manage subscription: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to manage subscription: {str(e)}"
        }
    finally:
        db.close()


@mcp.tool()
def escalate_to_human(customer_email: str, reason: str, conversation_summary: str, ctx: Context) -> Dict[str, Any]:
    """Escalate conversation to human agent"""
    db = next(get_db())
    try:
        # Log the escalation
        action = SupportAction(
            conversation_id=0,  # Will be updated when integrated with conversation
            action_type="escalate_to_human",
            action_data={
                "customer_email": customer_email,
                "reason": reason,
                "summary": conversation_summary
            },
            status="pending",
            executed_at=datetime.utcnow()
        )
        db.add(action)
        db.commit()
        
        ctx.info(f"Escalated conversation for {customer_email} to human agent")
        
        return {
            "success": True,
            "message": "Your conversation has been escalated to a human agent. You will be contacted shortly.",
            "escalation_id": f"ESC-{action.id}",
            "estimated_wait_time": "5-10 minutes"
        }
    except Exception as e:
        ctx.error(f"Failed to escalate: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to escalate: {str(e)}"
        }
    finally:
        db.close()


@mcp.tool()
def generate_ai_response(
    customer_message: str, 
    customer_email: str, 
    conversation_history: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Generate AI response using Gemini API with customer context"""
    try:
        # Get customer info
        customer_info = get_customer_info(customer_email)
        
        # Build a simple context for Gemini
        context = f"""You are a helpful customer support AI assistant. 

Customer Information:
- Email: {customer_info.email}
- Name: {customer_info.name}
- Subscription Status: {customer_info.subscription_status}
- Subscription Plan: {customer_info.subscription_plan}

Customer Message: {customer_message}

Please provide a helpful, empathetic response. Be professional and offer to help with their inquiry."""
        
        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(context)
        
        return {
            "success": True,
            "response": response.text,
            "confidence": 0.85,
            "suggested_actions": []
        }
    except Exception as e:
        # For development, let's provide a mock response
        return {
            "success": True,
            "response": f"Hello! I understand you need help with your subscription. As a customer support AI, I'm here to assist you. Could you please provide more details about what specific help you need with your subscription? I can help with billing questions, plan changes, cancellations, or other subscription-related issues.",
            "confidence": 0.75,
            "suggested_actions": ["billing_inquiry", "subscription_change"],
            "error_note": f"Gemini API error (using fallback): {str(e)}"
        }


@mcp.prompt()
def customer_support_prompt(customer_message: str, customer_email: str) -> str:
    """Generate a customer support response prompt"""
    return f"""
Please provide a helpful customer support response to the following message from {customer_email}:

Customer Message: {customer_message}

Guidelines:
- Be empathetic and professional
- Provide clear, actionable solutions
- If you need to perform actions like refunds or subscription changes, use the appropriate tools
- If the issue is complex or you're unsure, escalate to a human agent
- Always confirm customer details before taking any actions
"""