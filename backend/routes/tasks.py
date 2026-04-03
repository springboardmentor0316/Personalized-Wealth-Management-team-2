"""
API Routes for Celery Task Management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from database import get_db
from celery_tasks import celery_app, update_market_prices_task, update_portfolio_values_task
from schemas import User
from auth import get_current_user
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/status")
async def get_task_status():
    """
    Get status of Celery workers and tasks
    
    Returns:
        Dictionary with Celery status information
    """
    try:
        inspect = celery_app.control.inspect()
        
        # Get active workers
        active_workers = inspect.active()
        worker_count = len(active_workers) if active_workers else 0
        
        # Get scheduled tasks
        scheduled_tasks = inspect.scheduled()
        
        # Get active tasks
        active_tasks = inspect.active()
        
        return {
            "success": True,
            "data": {
                "celery_status": "active",
                "workers": active_workers,
                "worker_count": worker_count,
                "scheduled_tasks": scheduled_tasks,
                "active_tasks": active_tasks,
                "timestamp": str(datetime.utcnow())
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        return {
            "success": False,
            "data": {
                "celery_status": "inactive",
                "message": "Celery workers are not running",
                "error": str(e)
            }
        }


@router.post("/trigger/market-update")
async def trigger_market_update(
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger market price update task
    
    Returns:
        Task execution result
    """
    try:
        # Trigger the task
        task = update_market_prices_task.delay()
        
        return {
            "success": True,
            "message": "Market price update task triggered",
            "task_id": task.id,
            "status": task.status
        }
        
    except Exception as e:
        logger.error(f"Error triggering market update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/portfolio-update")
async def trigger_portfolio_update(
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger portfolio value update task
    
    Returns:
        Task execution result
    """
    try:
        # Trigger the task
        task = update_portfolio_values_task.delay()
        
        return {
            "success": True,
            "message": "Portfolio value update task triggered",
            "task_id": task.id,
            "status": task.status
        }
        
    except Exception as e:
        logger.error(f"Error triggering portfolio update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/symbol-update/{symbol}")
async def trigger_symbol_update(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger price update for a specific symbol
    
    Args:
        symbol: Stock symbol to update
    
    Returns:
        Task execution result
    """
    try:
        from celery_tasks import update_specific_symbol_task
        
        # Trigger the task
        task = update_specific_symbol_task.delay(symbol.upper())
        
        return {
            "success": True,
            "message": f"Price update task triggered for {symbol}",
            "task_id": task.id,
            "status": task.status
        }
        
    except Exception as e:
        logger.error(f"Error triggering symbol update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status of a specific task
    
    Args:
        task_id: Celery task ID
    
    Returns:
        Task status and result
    """
    try:
        result = celery_app.AsyncResult(task_id)
        
        response = {
            "success": True,
            "data": {
                "task_id": task_id,
                "status": result.status,
                "ready": result.ready()
            }
        }
        
        if result.ready():
            if result.successful():
                response["data"]["result"] = result.result
            else:
                response["data"]["error"] = str(result.info)
        else:
            response["data"]["info"] = result.info
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduled")
async def get_scheduled_tasks():
    """
    Get list of scheduled tasks
    
    Returns:
        List of scheduled tasks
    """
    try:
        scheduled_tasks = []
        
        for task_name, task_config in celery_app.conf.beat_schedule.items():
            scheduled_tasks.append({
                "name": task_name,
                "task": task_config["task"],
                "schedule": str(task_config["schedule"])
            })
        
        return {
            "success": True,
            "data": {
                "scheduled_tasks": scheduled_tasks,
                "total_tasks": len(scheduled_tasks)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduled tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/worker/start")
async def start_worker(background_tasks: BackgroundTasks):
    """
    Start a Celery worker (for development/testing)
    
    Note: In production, workers should be started separately
    """
    try:
        # This is a simplified version for development
        # In production, use: celery -A celery_tasks worker --loglevel=info
        
        return {
            "success": True,
            "message": "Worker start command issued",
            "note": "In production, start workers with: celery -A celery_tasks worker --loglevel=info"
        }
        
    except Exception as e:
        logger.error(f"Error starting worker: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/worker/stop")
async def stop_worker():
    """
    Stop all Celery workers
    
    Note: Use with caution in production
    """
    try:
        # Stop all workers
        celery_app.control.broadcast('shutdown')
        
        return {
            "success": True,
            "message": "Shutdown command sent to all workers"
        }
        
    except Exception as e:
        logger.error(f"Error stopping workers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Import datetime
from datetime import datetime
