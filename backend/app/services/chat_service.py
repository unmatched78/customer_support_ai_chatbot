from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.db.models import Conversation, Message, Customer
from app.mcp.server import generate_ai_response
import uuid
from datetime import datetime
import google.generativeai as genai
from app.core.config import settings


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        genai.configure(api_key=settings.GEMINI_API_KEY)
    
    async def create_conversation(self, customer_email: str, customer_name: Optional[str] = None) -> str:
        """Create a new conversation and return session_id"""
        session_id = str(uuid.uuid4())
        
        # Create or get customer
        customer = self.db.query(Customer).filter(Customer.email == customer_email).first()
        if not customer:
            customer = Customer(
                email=customer_email,
                name=customer_name,
                subscription_status="unknown",
                subscription_plan="none",
                total_spent="0"
            )
            self.db.add(customer)
            self.db.flush()
        
        # Create conversation
        conversation = Conversation(
            session_id=session_id,
            customer_email=customer_email,
            customer_name=customer_name or customer.name,
            status="active"
        )
        self.db.add(conversation)
        self.db.commit()
        
        return session_id
    
    async def send_message(self, session_id: str, content: str, sender_type: str = "customer") -> Dict[str, Any]:
        """Send a message and get AI response if sender is customer"""
        conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            raise ValueError("Conversation not found")
        
        # Save customer message
        customer_message = Message(
            conversation_id=conversation.id,
            content=content,
            sender_type=sender_type,
            message_metadata={"timestamp": datetime.utcnow().isoformat()}
        )
        self.db.add(customer_message)
        self.db.flush()
        
        response_data = {"message_id": customer_message.id}
        
        # Generate AI response if customer sent the message
        if sender_type == "customer":
            # Get conversation history
            history = self.get_conversation_history(session_id)
            
            # Generate AI response using MCP
            ai_response = generate_ai_response(
                customer_message=content,
                customer_email=conversation.customer_email,
                conversation_history=history
            )
            
            if ai_response["success"]:
                # Save AI response
                ai_message = Message(
                    conversation_id=conversation.id,
                    content=ai_response["response"],
                    sender_type="ai",
                    message_metadata={
                        "confidence": ai_response.get("confidence", 0.0),
                        "suggested_actions": ai_response.get("suggested_actions", []),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                self.db.add(ai_message)
                self.db.commit()
                
                response_data.update({
                    "ai_response": ai_response["response"],
                    "ai_message_id": ai_message.id,
                    "confidence": ai_response.get("confidence", 0.0)
                })
            else:
                # Handle AI error
                error_message = Message(
                    conversation_id=conversation.id,
                    content="I apologize, but I'm experiencing technical difficulties. Let me connect you with a human agent.",
                    sender_type="ai",
                    message_metadata={
                        "error": ai_response.get("error", "Unknown error"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                self.db.add(error_message)
                self.db.commit()
                
                response_data.update({
                    "ai_response": error_message.content,
                    "ai_message_id": error_message.id,
                    "error": True
                })
        else:
            self.db.commit()
        
        return response_data
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history"""
        conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            return []
        
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at).all()
        
        history = []
        for message in messages:
            history.append({
                "id": message.id,
                "content": message.content,
                "sender": message.sender_type,
                "timestamp": message.created_at.isoformat(),
                "metadata": message.message_metadata or {}
            })
        
        return history
    
    def escalate_conversation(self, session_id: str, reason: str) -> Dict[str, Any]:
        """Escalate conversation to human agent"""
        conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            raise ValueError("Conversation not found")
        
        conversation.status = "escalated"
        
        # Add escalation message
        escalation_message = Message(
            conversation_id=conversation.id,
            content=f"Conversation escalated to human agent. Reason: {reason}",
            sender_type="system",
            message_metadata={
                "escalation_reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.db.add(escalation_message)
        self.db.commit()
        
        return {
            "success": True,
            "message": "Conversation has been escalated to a human agent",
            "estimated_wait_time": "5-10 minutes"
        }
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation summary"""
        conversation = self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            raise ValueError("Conversation not found")
        
        message_count = self.db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).count()
        
        return {
            "session_id": session_id,
            "customer_email": conversation.customer_email,
            "customer_name": conversation.customer_name,
            "status": conversation.status,
            "message_count": message_count,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None
        }