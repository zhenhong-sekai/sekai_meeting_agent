# src/tools/notion_tools.py
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.config.settings import settings

client = MultiServerMCPClient({
    "notion": {
        "command": "npx",
        "args": ["-y", "@notionhq/notion-mcp-server"],
        "transport": "stdio",
        "env": {
            "OPENAPI_MCP_HEADERS": (
                '{"Authorization": "Bearer ' + settings.NOTION_TOKEN + '",'
                '"Notion-Version": "2022-06-28"}'
            )
        },
    }
})

# Instead of trying to `await` at the top-level,
# provide an async function to fetch the tools
async def get_notion_tools():
    return await client.get_tools()
