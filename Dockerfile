FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Notion MCP globally
RUN npm install -g @notionhq/notion-mcp-server

# Copy application code
COPY src/ ./src/

# Environment variables will be provided at runtime
ENV OPENAI_API_KEY=""
ENV NOTION_TOKEN=""
ENV OPENAI_BASE_URL="https://yunwu.ai/v1"
ENV MODEL_NAME="gpt-4o"
ENV ZOOM_ACCOUNT_ID=""
ENV ZOOM_CLIENT_ID=""
ENV ZOOM_CLIENT_SECRET=""
ENV ZOOM_WEBHOOK_USER=""
ENV ZOOM_WEBHOOK_PASS=""

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
