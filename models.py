from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class FalStatus(str, Enum):
    QUEUED = "IN_QUEUE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Priority(str, Enum):
    NORMAL = "normal"
    LOW = "low"

class FalRequest(BaseModel):
    # Base request model if needed
    pass

class QueueStatus(BaseModel):
    status: FalStatus
    request_id: str
    response_url: Optional[str] = None
    logs: Optional[List[Dict[str, Any]]] = None
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
