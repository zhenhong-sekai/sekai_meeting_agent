# tools/notion_tools.py
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import os

load_dotenv()
notion_token = os.getenv("NOTION_TOKEN")

client = MultiServerMCPClient({
    "notion": {
        "command": "npx",
        "args": ["-y", "@notionhq/notion-mcp-server"],
        "transport": "stdio",
        "env": {
            "OPENAPI_MCP_HEADERS": (
                '{"Authorization": "Bearer ' + notion_token + '",'
                '"Notion-Version": "2022-06-28"}'
            )
        },
    }
})

# Instead of trying to `await` at the top-level,
# provide an async function to fetch the tools
async def get_notion_tools():
    return await client.get_tools()
