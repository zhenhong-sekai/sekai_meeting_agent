from typing import Dict
import pandas as pd
from typing import List
from difflib import SequenceMatcher
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain.tools import Tool
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
import time
from openai import OpenAI
from src.tools.notion_tools import get_notion_tools
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.config.settings import settings

client = ChatOpenAI(
    model="gpt-4o",
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)

class NotionAgentOutput(BaseModel):
    notion_parent_id: str
    step_summary: str


import asyncio
from typing import Dict

async def notion_agent_node(state: Dict) -> Dict:
    print("="*50)
    print("🤖 NOTION AGENT")
    print("="*50)
    # Run the async get_notion_tools once synchronously
    notion_tools = await get_notion_tools()

    # Create the agent
    notion_agent = create_react_agent(
        model=client,
        tools=notion_tools,
        prompt="You are a helpful assistant that can create pages in Notion. Always call for search tool to find the relevant page ids/details first. Then call create tool to create the page if needed. "
               "For the step_summary field, describe what you accomplished for the user (e.g., 'Created Notion page for meeting results' or 'Published meeting summary to Notion'), "
               "not the actual page content or Notion page details.",
        # debug=True,
        response_format=NotionAgentOutput,
    )
    user_message = state.get("last_user_message")
    # Run the agent synchronously
    result = await notion_agent.ainvoke(
        {"messages": [{"role": "user", "content": f"Current task: {state.get('next_step')},summary: {state.get('summary')},todo: {state.get('todo')},feedback: {state.get('feedback')}"}]}
    )
    notion_parent_id = result['structured_response'].notion_parent_id
    step_summary = result['structured_response'].step_summary
    print("[NOTION AGENT] Step Summary:", step_summary)
    updated = {
        **state,
        "notion_parent_id": notion_parent_id,
        "route": "end",  # Always end after notion
        "step_summary": [step_summary]
    }
    return updated
