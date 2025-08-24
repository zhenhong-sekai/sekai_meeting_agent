import asyncio
import httpx
import json

async def test_api():
    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            health_response = await client.get("http://localhost:8000/api/v1/health")
            print(f"Health check: {health_response.status_code}")
            print(f"Health response: {health_response.json()}")
            
            # Test query endpoint
            query_data = {
                "query": "Help me get transcript of meet recording named AI Sharing分享 and summarise it"
            }
            
            print("\nSending query to API...")
            response = await client.post(
                "http://localhost:8000/api/v1/query",
                json=query_data,
                timeout=60.0
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("Streaming response:")
                async for line in response.aiter_lines():
                    if line.strip():
                        if line.startswith("data: "):
                            try:
                                data_str = line[6:]  # Remove "data: " prefix
                                data = json.loads(data_str)
                                                            if "error" in data:
                                print(f"❌ Error: {data['error']}")
                            else:
                                node = data.get('node')
                                payload = data.get('payload')
                                print(f"📡 Node: {node}")
                                
                                # Show step_summary if present
                                if "step_summary" in payload:
                                    step_summary = payload["step_summary"]
                                    print(f"   📋 Step Summary: {step_summary}")
                                
                                # Show final_summary if present
                                if "final_summary" in payload:
                                    print(f"   🎯 Final Summary: {payload['final_summary']}")
                                
                                # Show other key fields
                                for key in ["transcript_path", "summary", "todo", "feedback", "next_step"]:
                                    if key in payload and payload[key]:
                                        print(f"   {key}: {payload[key]}")
                                print()
                            except json.JSONDecodeError:
                                print(f"Raw data: {line}")
                        else:
                            print(f"Raw line: {line}")
            else:
                print(f"Error response: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
