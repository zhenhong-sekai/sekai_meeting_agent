# Meeting Agent UI

A Next.js application that provides a real-time interface for the Meeting Agent workflow using Server-Sent Events (SSE).

## Features

- 🚀 Real-time streaming of meeting agent workflow
- 🎨 Modern, responsive UI with Tailwind CSS
- 📊 Live event log with color-coded event types
- 🧪 SSE connection testing
- ⚡ Fast query processing with streaming responses

## Prerequisites

- Node.js 18+ 
- Your Meeting Agent API running on `http://localhost:8000`

## Setup

1. **Install dependencies:**
   ```bash
   cd nextjs-app
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## Usage

### Testing SSE Connection
1. Click the "Test SSE" button to verify the SSE connection
2. Watch for 5 test messages over 5 seconds
3. Verify that events are displayed in the Event Log

### Sending Queries
1. Enter your query in the text area (e.g., "Help me get transcript of meeting AI Sharing and summarize it")
2. Click "Send Query"
3. Watch the real-time workflow execution in the Event Log

### Event Types

- **🚀 Start**: Workflow initialization
- **🤖 Node Update**: Each agent execution (Supervisor, Zoom, Debrief, Notion)
- **✅ Completion**: Workflow completion with final summary
- **❌ Error**: Error messages
- **🧪 Test**: Test messages for connection verification

## API Endpoints

The app connects to your Meeting Agent API through the following endpoints:

- `POST /api/query` - Send queries to the meeting agent
- `GET /api/test-sse` - Test SSE connection
- `GET /api/health` - Health check

**Note**: The Next.js app proxies these requests to `http://localhost:8000/api/v1/` endpoints.

## Architecture

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Server-Sent Events** for real-time streaming

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint
```

## Troubleshooting

1. **Connection Issues**: Make sure your Meeting Agent API is running on `http://localhost:8000`
2. **SSE Not Working**: Check browser console for errors and verify CORS settings
3. **Events Not Displaying**: Ensure the API is returning properly formatted SSE events

## Customization

- Modify `next.config.js` to change the API proxy settings
- Update `types/sse.ts` to match your API's event structure
- Customize styling in `components/` files
