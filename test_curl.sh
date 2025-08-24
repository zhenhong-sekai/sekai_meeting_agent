#!/bin/bash

echo "Testing Meeting Agent API..."

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s http://localhost:8000/api/v1/health | jq .

echo -e "\n2. Testing query endpoint..."
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Help me get transcript of meet recording named AI Sharing分享 and summarise it"
  }' \
  --no-buffer

echo -e "\n\nAPI test completed!"
