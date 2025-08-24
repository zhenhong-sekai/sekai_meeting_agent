from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    node: str
    payload: Dict[str, Any]

class SSEEvent(BaseModel):
    event: str
    data: Dict[str, Any]
    
    def to_sse(self) -> str:
        """Convert to Server-Sent Events format"""
        return f"event: {self.event}\ndata: {json.dumps(self.data)}\n\n"
