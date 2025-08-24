# Meeting Agent API

A FastAPI-based service for processing meeting transcripts and managing Notion integration using LangGraph agents.

## Project Structure

```
sekai_meeting_agent/
├── src/
│   ├── api/
│   │   ├── models.py      # API request/response models
│   │   └── routes.py      # FastAPI routes
│   ├── agents/
│   │   ├── zoom_agent.py      # Zoom transcript handling
│   │   ├── debrief_agent.py   # Meeting analysis
│   │   └── notion_agent.py    # Notion integration
│   ├── tools/
│   │   ├── zoom_tools.py      # Zoom API tools
│   │   ├── debrief_tools.py   # Analysis tools
│   │   └── notion_tools.py    # Notion MCP tools
│   ├── config/
│   │   └── settings.py        # Configuration management
│   ├── graph.py               # LangGraph workflow
│   └── main.py                # FastAPI application
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── test_api.py
```

## Setup

1. **Environment Variables**
   Create a `.env` file in the root directory:
   ```bash
   # OpenAI settings
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_BASE_URL=https://yunwu.ai/v1
   MODEL_NAME=gpt-4o
   
   # Notion settings
   NOTION_TOKEN=your_notion_token
   
   # Zoom settings
   ZOOM_ACCOUNT_ID=your_zoom_account_id
   ZOOM_CLIENT_ID=your_zoom_client_id
   ZOOM_CLIENT_SECRET=your_zoom_client_secret
   ZOOM_WEBHOOK_USER=your_zoom_webhook_user
   ZOOM_WEBHOOK_PASS=your_zoom_webhook_pass
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Notion MCP Server**
   ```bash
   npm install -g @notionhq/notion-mcp-server
   ```

## Running the Application

### Option 1: Direct Python
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t meeting-agent .
docker run -p 8000:8000 --env-file .env meeting-agent
```

## API Endpoints

### Health Check
```bash
GET /api/v1/health
```

### Process Query
```bash
POST /api/v1/query
Content-Type: application/json

{
  "query": "Help me get transcript of meet recording named AI Sharing分享 and summarise it",
  "context": {}  // optional
}
```

## Testing

Run the test script to verify the API:
```bash
python test_api.py
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Production Deployment

1. **Environment Variables**: Ensure all sensitive data is in environment variables
2. **Reverse Proxy**: Use Nginx or similar for production
3. **SSL**: Configure HTTPS for production
4. **Monitoring**: Add logging and monitoring

### Example Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Development

### Adding New Agents
1. Create agent file in `src/agents/`
2. Add agent node to `src/graph.py`
3. Update routing logic as needed

### Adding New Tools
1. Create tool file in `src/tools/`
2. Import and use in relevant agents
3. Update requirements.txt if needed

## Troubleshooting

1. **Notion MCP Issues**: Ensure Node.js and npm are installed
2. **Import Errors**: Check that all imports use the new `src.` prefix
3. **Environment Variables**: Verify `.env` file exists and contains all required variables