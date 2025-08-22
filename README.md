# Meeting Agent 🤖

A powerful AI-powered meeting assistant that helps you manage and process meeting recordings, generate summaries, and organize information in Notion.

## Features

- 🎥 **Zoom Integration**: Automatically fetch and process Zoom meeting recordings
- 📝 **Transcript Generation**: Convert meeting recordings to searchable text
- 📊 **Meeting Debrief**: Generate summaries, action items, and key takeaways
- 📚 **Notion Integration**: Save and organize meeting information in Notion
- 🎯 **Task Tracking**: Extract and track action items and todos
- 💡 **Smart Interface**: User-friendly Streamlit interface for easy interaction

## Prerequisites

- Python 3.9+
- Zoom API credentials
- OpenAI API key
- Notion API integration
- Virtual environment (recommended)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Zoom
ZOOM_ACCOUNT_ID=your_zoom_account_id
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret

# Notion
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_notion_database_id
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd sekai_meeting_agent
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Enter your query in the text area. Example queries:
   - "Get transcript of meet recording named 'AI Sharing分享' and summarize it"
   - "Generate action items from my last meeting"
   - "Save the meeting summary to Notion"

## Project Structure

```
sekai_meeting_agent/
├── app.py                 # Main Streamlit application
├── debrief_agent.py      # Meeting debrief processing logic
├── graph.py              # LangGraph workflow definitions
├── notion_agent.py       # Notion integration
├── zoom_agent.py         # Zoom integration
├── tools/
│   ├── debrief_tools.py  # Tools for meeting analysis
│   ├── notion_tools.py   # Notion API tools
│   └── zoom_tools.py     # Zoom API tools
└── utils/
    └── get_transcript.py # Transcript processing utilities
```

## API Integration Setup

### Zoom Setup
1. Create a Zoom App in the Zoom Marketplace
2. Configure OAuth credentials
3. Add the required scopes:
   - `recording:read`
   - `recording:write`
   - `user:read`

### Notion Setup
1. Create a new integration at https://www.notion.so/my-integrations
2. Share your Notion database with the integration
3. Copy the database ID from the URL

### OpenAI Setup
1. Create an account at https://platform.openai.com
2. Generate an API key
3. Add the key to your `.env` file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]

## Support

For support, please [specify contact method or create an issue].