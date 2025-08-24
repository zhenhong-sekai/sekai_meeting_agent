from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from .models import QueryRequest, QueryResponse
from src.graph import compiled_graph
import asyncio
import json
from typing import AsyncGenerator

router = APIRouter()

@router.post("/query")
async def process_query(request: QueryRequest):
    async def generate_stream():
        try:
            async for update in compiled_graph.astream({
                "last_user_message": request.query,
                "step_summary": [],
                **(request.context or {})
            }):
                for node, payload in update.items():
                    response_data = QueryResponse(
                        node=node,
                        payload=payload
                    )
                    yield f"data: {response_data.model_dump_json()}\n\n"
        except Exception as e:
            error_data = {"error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
