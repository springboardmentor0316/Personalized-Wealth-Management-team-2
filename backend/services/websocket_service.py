"""
WebSocket Service for Real-time Updates
Provides real-time updates for portfolio values, market prices, and notifications
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import asyncio


class WebSocketManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: Dict[str, List] = {}
        self.user_connections: Dict[str, Any] = {}
    
    async def connect(self, websocket: Any, user_id: str):
        """Accept a new WebSocket connection"""
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        self.user_connections[id(websocket)] = user_id
        print(f"User {user_id} connected via WebSocket")
    
    async def disconnect(self, websocket: Any):
        """Remove a WebSocket connection"""
        user_id = self.user_connections.get(id(websocket))
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        if id(websocket) in self.user_connections:
            del self.user_connections[id(websocket)]
        print(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: str):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending message to user {user_id}: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected users"""
        disconnected = []
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting to user {user_id}: {e}")
                    disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def broadcast_to_users(self, message: Dict[str, Any], user_ids: List[str]):
        """Broadcast a message to specific users"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    def get_connected_users(self) -> List[str]:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())


class RealTimeUpdateService:
    """Service for generating real-time updates"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.update_interval = 30  # seconds
    
    async def send_portfolio_update(self, user_id: str, portfolio_data: Dict[str, Any]):
        """Send portfolio value update to user"""
        message = {
            "type": "portfolio_update",
            "data": {
                "user_id": user_id,
                "total_value": portfolio_data.get("total_value", 0),
                "total_gain_loss": portfolio_data.get("total_gain_loss", 0),
                "total_gain_loss_percent": portfolio_data.get("total_gain_loss_percent", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.websocket_manager.send_personal_message(message, user_id)
    
    async def send_market_price_update(self, symbols: List[str], price_data: Dict[str, Any]):
        """Send market price updates to all users"""
        message = {
            "type": "market_price_update",
            "data": {
                "symbols": symbols,
                "prices": price_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.websocket_manager.broadcast(message)
    
    async def send_alert_update(self, user_id: str, alert_data: Dict[str, Any]):
        """Send alert update to user"""
        message = {
            "type": "alert_update",
            "data": {
                "user_id": user_id,
                "alert": alert_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.websocket_manager.send_personal_message(message, user_id)
    
    async def send_recommendation_update(self, user_id: str, recommendation_data: Dict[str, Any]):
        """Send recommendation update to user"""
        message = {
            "type": "recommendation_update",
            "data": {
                "user_id": user_id,
                "recommendation": recommendation_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.websocket_manager.send_personal_message(message, user_id)
    
    async def send_goal_progress_update(self, user_id: str, goal_data: Dict[str, Any]):
        """Send goal progress update to user"""
        message = {
            "type": "goal_progress_update",
            "data": {
                "user_id": user_id,
                "goal": goal_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.websocket_manager.send_personal_message(message, user_id)
    
    async def send_system_notification(self, notification: Dict[str, Any]):
        """Send system notification to all users"""
        message = {
            "type": "system_notification",
            "data": {
                "notification": notification,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.websocket_manager.broadcast(message)
    
    async def send_error_notification(self, user_id: str, error_data: Dict[str, Any]):
        """Send error notification to user"""
        message = {
            "type": "error_notification",
            "data": {
                "user_id": user_id,
                "error": error_data,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await self.websocket_manager.send_personal_message(message, user_id)
    
    async def start_background_updates(self):
        """Start background task for periodic updates"""
        while True:
            try:
                # This would typically fetch real data from database
                # For now, we'll just send a heartbeat
                heartbeat_message = {
                    "type": "heartbeat",
                    "data": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "connected_users": self.websocket_manager.get_connection_count()
                    }
                }
                await self.websocket_manager.broadcast(heartbeat_message)
                
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in background updates: {e}")
                await asyncio.sleep(5)


# Global instances
websocket_manager = WebSocketManager()
real_time_update_service = RealTimeUpdateService(websocket_manager)
