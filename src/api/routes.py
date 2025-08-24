from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from .models import QueryRequest, QueryResponse, SSEEvent
from src.graph import compiled_graph
import asyncio
import json
from typing import AsyncGenerator
import time

router = APIRouter()

@router.post("/query")
async def process_query(request: QueryRequest):
    async def generate_stream():
        try:
            # Send start event
            start_event = SSEEvent(
                event="start",
                data={
                    "message": "Workflow started",
                    "query": request.query,
                    "timestamp": time.time()
                }
            )
            start_sse = start_event.to_sse()
            print(f"[API] Sending start event: {start_sse}")
            yield start_sse
            
            # Stream graph updates with proper streaming mode
            async for update in compiled_graph.astream({
                "last_user_message": request.query,
                "step_summary": [],
                **(request.context or {})
            }, stream_mode="updates"):
                print(f"[API] Received update: {update}")
                print(f"[API] Update type: {type(update)}")
                print(f"[API] Update keys: {update.keys() if hasattr(update, 'keys') else 'No keys'}")
                
                                # Handle the update structure properly
                if isinstance(update, dict):
                    # Each update contains a single node's result
                    for node, payload in update.items():
                        print(f"[API] Processing node: {node}")
                        
                        # Create node update event
                        node_event = SSEEvent(
                            event="node_update",
                            data={
                                "node": node,
                                "payload": payload,
                                "timestamp": time.time()
                            }
                        )
                        node_sse = node_event.to_sse()
                        print(f"[API] Sending node event for {node}")
                        yield node_sse
                        
                        # If this is the final summary, send completion event
                        if node == "log_summary":
                            completion_event = SSEEvent(
                                event="completion",
                                data={
                                    "message": "Workflow completed successfully",
                                    "total_steps": len(payload.get("step_summary", [])),
                                    "timestamp": time.time()
                                }
                            )
                            completion_sse = completion_event.to_sse()
                            print(f"[API] Sending completion event")
                            yield completion_sse
                else:
                    print(f"[API] Non-dict update received: {update}")
                        
        except Exception as e:
            error_event = SSEEvent(
                event="error",
                data={
                    "error": str(e),
                    "timestamp": time.time()
                }
            )
            yield error_event.to_sse()
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/query")
async def process_query_get(query: str = None, context: str = None):
    """GET endpoint for EventSource compatibility"""
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    # Parse context if provided
    parsed_context = {}
    if context:
        try:
            parsed_context = json.loads(context)
        except json.JSONDecodeError:
            pass
    
    # Create a mock request object
    class MockRequest:
        def __init__(self, query: str, context: dict):
            self.query = query
            self.context = context
    
    request = MockRequest(query, parsed_context)
    
    async def generate_stream():
        try:
            # Send start event
            start_event = SSEEvent(
                event="start",
                data={
                    "message": "Workflow started",
                    "query": request.query,
                    "timestamp": time.time()
                }
            )
            start_sse = start_event.to_sse()
            print(f"[API] Sending start event: {start_sse}")
            yield start_sse
            
            # Stream graph updates with proper streaming mode
            async for update in compiled_graph.astream({
                "last_user_message": request.query,
                "step_summary": [],
                **(request.context or {})
            }, stream_mode="updates"):
                print(f"[API] Received update: {update}")
                print(f"[API] Update type: {type(update)}")
                print(f"[API] Update keys: {update.keys() if hasattr(update, 'keys') else 'No keys'}")
                
                # Handle the update structure properly
                if isinstance(update, dict):
                    # Each update contains a single node's result
                    for node, payload in update.items():
                        print(f"[API] Processing node: {node}")
                        
                        # Create node update event
                        node_event = SSEEvent(
                            event="node_update",
                            data={
                                "node": node,
                                "payload": payload,
                                "timestamp": time.time()
                            }
                        )
                        node_sse = node_event.to_sse()
                        print(f"[API] Sending node event for {node}")
                        yield node_sse
                        
                        # If this is the final summary, send completion event
                        if node == "log_summary":
                            completion_event = SSEEvent(
                                event="completion",
                                data={
                                    "message": "Workflow completed successfully",
                                    "total_steps": len(payload.get("step_summary", [])),
                                    "timestamp": time.time()
                                }
                            )
                            completion_sse = completion_event.to_sse()
                            print(f"[API] Sending completion event")
                            yield completion_sse
                else:
                    print(f"[API] Non-dict update received: {update}")
                        
        except Exception as e:
            error_event = SSEEvent(
                event="error",
                data={
                    "error": str(e),
                    "timestamp": time.time()
                }
            )
            yield error_event.to_sse()
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/test-sse")
async def test_sse():
    """Test endpoint for SSE connection"""
    async def generate_test_stream():
        for i in range(5):
            test_event = SSEEvent(
                event="test",
                data={
                    "message": f"Test message {i+1}",
                    "timestamp": time.time()
                }
            )
            test_sse = test_event.to_sse()
            print(f"[API] Sending test event {i+1}: {test_sse}")
            yield test_sse
            await asyncio.sleep(2)  # Increased delay to make streaming more visible
        
        # Send completion event
        completion_event = SSEEvent(
            event="completion",
            data={
                "message": "Test completed",
                "timestamp": time.time()
            }
        )
        completion_sse = completion_event.to_sse()
        print(f"[API] Sending test completion: {completion_sse}")
        yield completion_sse
    
    return StreamingResponse(
        generate_test_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Accel-Buffering": "no"
        }
    )
