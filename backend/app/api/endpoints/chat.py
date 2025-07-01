from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.api.deps import get_database
from app.services import ChatService
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class StartChatRequest(BaseModel):
    customer_email: str = Field(..., description="Customer email address")
    customer_name: str = Field(None, description="Customer name (optional)")


class SendMessageRequest(BaseModel):
    session_id: str = Field(..., description="Chat session ID")
    content: str = Field(..., description="Message content")


class EscalateRequest(BaseModel):
    session_id: str = Field(..., description="Chat session ID")
    reason: str = Field(..., description="Reason for escalation")


@router.post("/start", response_model=Dict[str, str])
async def start_chat(
    request: StartChatRequest,
    db: Session = Depends(get_database)
):
    """Start a new chat conversation"""
    try:
        chat_service = ChatService(db)
        session_id = await chat_service.create_conversation(
            customer_email=request.customer_email,
            customer_name=request.customer_name
        )
        return {"session_id": session_id, "status": "started"}
    except Exception as e:
        logger.error(f"Error starting chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=Dict[str, Any])
async def send_message(
    request: SendMessageRequest,
    db: Session = Depends(get_database)
):
    """Send a message in a chat conversation"""
    try:
        chat_service = ChatService(db)
        response = await chat_service.send_message(
            session_id=request.session_id,
            content=request.content
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=List[Dict[str, Any]])
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_database)
):
    """Get chat conversation history"""
    try:
        chat_service = ChatService(db)
        history = chat_service.get_conversation_history(session_id)
        return history
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/escalate", response_model=Dict[str, Any])
async def escalate_chat(
    request: EscalateRequest,
    db: Session = Depends(get_database)
):
    """Escalate chat to human agent"""
    try:
        chat_service = ChatService(db)
        response = chat_service.escalate_conversation(
            session_id=request.session_id,
            reason=request.reason
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error escalating chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{session_id}", response_model=Dict[str, Any])
async def get_chat_summary(
    session_id: str,
    db: Session = Depends(get_database)
):
    """Get chat conversation summary"""
    try:
        chat_service = ChatService(db)
        summary = chat_service.get_conversation_summary(session_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting chat summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, session_id)
    
    # Get database session
    db = next(get_database())
    chat_service = ChatService(db)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                # Process the message
                response = await chat_service.send_message(
                    session_id=session_id,
                    content=message_data.get("content", "")
                )
                
                # Send response back to client
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "data": response
                }))
            
            elif message_data.get("type") == "escalate":
                # Handle escalation
                response = chat_service.escalate_conversation(
                    session_id=session_id,
                    reason=message_data.get("reason", "Customer request")
                )
                
                await websocket.send_text(json.dumps({
                    "type": "escalated",
                    "data": response
                }))
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
    finally:
        db.close()