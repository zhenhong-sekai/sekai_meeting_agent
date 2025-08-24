#!/usr/bin/env python3
"""
Test script to verify step_summary logging at the end of the pipeline
"""

import asyncio
from src.graph import compiled_graph

async def test_step_summary():
    print("🧪 Testing step_summary logging...")
    print("="*60)
    
    async for update in compiled_graph.astream({
        "last_user_message": "Help me get transcript of meet recording named AI Sharing分享 and summarise it",
        "step_summary": []
    }):
        for node, payload in update.items():
            print(f"📡 Node: {node}")
            if "step_summary" in payload:
                step_summary = payload["step_summary"]
                print(f"   Step Summary: {step_summary}")
            if "final_summary" in payload:
                print(f"   Final Summary: {payload['final_summary']}")
            print()

if __name__ == "__main__":
    asyncio.run(test_step_summary())
