from pydantic import BaseModel
from typing import Optional, Dict, Any

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    node: str
    payload: Dict[str, Any]
