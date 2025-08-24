#!/usr/bin/env python3
"""
Direct test of the graph to show step_summary logging
"""

import asyncio
from src.graph import compiled_graph

async def main():
    print("🚀 Testing step_summary logging directly...")
    print("="*70)
    
    result = await compiled_graph.ainvoke({
        "last_user_message": "Help me get transcript of meet recording named AI Sharing分享 and summarise it",
        "step_summary": []
    })
    
    print("\n🎯 FINAL RESULT:")
    print("="*70)
    print(f"Step Summary: {result.get('step_summary', [])}")
    print(f"Final Summary: {result.get('final_summary', 'N/A')}")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
