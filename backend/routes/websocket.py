"""
API Routes for WebSocket Real-time Updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from database import get_db
from services.websocket_service import websocket_manager, real_time_update_service
from schemas import User
from auth import get_current_user
import json

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time updates
    
    Connect to: ws://localhost:8001/ws/ws/{user_id}
    """
    await websocket.accept()
    await websocket_manager.connect(websocket, user_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "data": {
                "user_id": user_id,
                "timestamp": str(datetime.utcnow()),
                "message": "WebSocket connection established"
            }
        })
        
        # Listen for messages from client
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types from client
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "data": {"timestamp": str(datetime.utcnow())}
                })
            elif message.get("type") == "subscribe":
                # Handle subscription requests
                subscription_type = message.get("data", {}).get("subscription_type")
                await handle_subscription(websocket, user_id, subscription_type)
            elif message.get("type") == "unsubscribe":
                # Handle unsubscription requests
                subscription_type = message.get("data", {}).get("subscription_type")
                await handle_unsubscription(websocket, user_id, subscription_type)
            
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
        print(f"User {user_id} disconnected")
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        await websocket_manager.disconnect(websocket)


async def handle_subscription(websocket: WebSocket, user_id: str, subscription_type: str):
    """Handle subscription requests from client"""
    if subscription_type == "portfolio_updates":
        await websocket.send_json({
            "type": "subscription_confirmed",
            "data": {
                "subscription_type": subscription_type,
                "user_id": user_id,
                "message": "Subscribed to portfolio updates"
            }
        })
    elif subscription_type == "market_updates":
        await websocket.send_json({
            "type": "subscription_confirmed",
            "data": {
                "subscription_type": subscription_type,
                "user_id": user_id,
                "message": "Subscribed to market updates"
            }
        })
    elif subscription_type == "alerts":
        await websocket.send_json({
            "type": "subscription_confirmed",
            "data": {
                "subscription_type": subscription_type,
                "user_id": user_id,
                "message": "Subscribed to alerts"
            }
        })


async def handle_unsubscription(websocket: WebSocket, user_id: str, subscription_type: str):
    """Handle unsubscription requests from client"""
    await websocket.send_json({
        "type": "unsubscription_confirmed",
        "data": {
            "subscription_type": subscription_type,
            "user_id": user_id,
            "message": f"Unsubscribed from {subscription_type}"
        }
    })


@router.get("/connections")
async def get_active_connections():
    """
    Get information about active WebSocket connections
    
    Returns:
        Dictionary with connection statistics
    """
    try:
        connected_users = websocket_manager.get_connected_users()
        connection_count = websocket_manager.get_connection_count()
        
        return {
            "success": True,
            "data": {
                "connected_users": connected_users,
                "total_connections": connection_count,
                "timestamp": str(datetime.utcnow())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast")
async def broadcast_message(
    message_type: str,
    message_data: Dict,
    target_users: List[str] = None
):
    """
    Broadcast a message to connected users
    
    Args:
        message_type: Type of message (e.g., "portfolio_update", "market_update")
        message_data: Message content
        target_users: Optional list of specific user IDs (if None, broadcasts to all)
    """
    try:
        message = {
            "type": message_type,
            "data": message_data,
            "timestamp": str(datetime.utcnow())
        }
        
        if target_users:
            await websocket_manager.broadcast_to_users(message, target_users)
        else:
            await websocket_manager.broadcast(message)
        
        return {
            "success": True,
            "message": f"Message broadcasted to {len(target_users) if target_users else 'all'} users"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send/{user_id}")
async def send_personal_message(
    user_id: str,
    message_type: str,
    message_data: Dict
):
    """
    Send a message to a specific user
    
    Args:
        user_id: Target user ID
        message_type: Type of message
        message_data: Message content
    """
    try:
        message = {
            "type": message_type,
            "data": message_data,
            "timestamp": str(datetime.utcnow())
        }
        
        await websocket_manager.send_personal_message(message, user_id)
        
        return {
            "success": True,
            "message": f"Message sent to user {user_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Import datetime
from datetime import datetime
