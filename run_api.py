#!/usr/bin/env python3
"""
Simple script to run the Meeting Agent API locally
"""

import uvicorn
import os
from pathlib import Path

def main():
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found!")
        print("Please create a .env file with the following variables:")
        print("# OpenAI settings")
        print("OPENAI_API_KEY=your_openai_api_key")
        print("OPENAI_BASE_URL=https://yunwu.ai/v1")
        print("MODEL_NAME=gpt-4o")
        print("")
        print("# Notion settings")
        print("NOTION_TOKEN=your_notion_token")
        print("")
        print("# Zoom settings")
        print("ZOOM_ACCOUNT_ID=your_zoom_account_id")
        print("ZOOM_CLIENT_ID=your_zoom_client_id")
        print("ZOOM_CLIENT_SECRET=your_zoom_client_secret")
        print("ZOOM_WEBHOOK_USER=your_zoom_webhook_user")
        print("ZOOM_WEBHOOK_PASS=your_zoom_webhook_pass")
        print()
    
    print("🚀 Starting Meeting Agent API...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/api/v1/health")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Run the FastAPI server
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
