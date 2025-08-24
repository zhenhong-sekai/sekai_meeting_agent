#!/bin/bash

# Build and run script for Meeting Agent
set -e

echo "🚀 Building Meeting Agent Docker containers..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Please create one with your environment variables."
    echo "Example .env file:"
    echo "OPENAI_API_KEY=your-openai-api-key"
    echo "NOTION_TOKEN=your-notion-token"
    echo "ZOOM_ACCOUNT_ID=your-zoom-account-id"
    echo "ZOOM_CLIENT_ID=your-zoom-client-id"
    echo "ZOOM_CLIENT_SECRET=your-zoom-client-secret"
    echo "ZOOM_WEBHOOK_USER=your-zoom-webhook-user"
    echo "ZOOM_WEBHOOK_PASS=your-zoom-webhook-pass"
    echo ""
fi

# Build the containers
echo "📦 Building backend container..."
docker build -f Dockerfile.backend -t meeting-agent-backend .

echo "📦 Building frontend container..."
docker build -f Dockerfile.frontend -t meeting-agent-frontend .

echo "✅ Build completed successfully!"

echo ""
echo "🎯 To run the containers:"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo ""
echo "📋 To view logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 To stop the containers:"
echo "   docker-compose -f docker-compose.prod.yml down"
