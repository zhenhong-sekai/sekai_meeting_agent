from typing import Dict
from src.tools.zoom_tools import zoom_find_transcript
from src.config.settings import settings
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
from langchain_openai import ChatOpenAI
from pathlib import Path
import httpx
from loguru import logger
from utils.get_transcript import load_transcript

client = ChatOpenAI(
    model="gpt-4o-mini", 
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)

class ZoomAgentOutput(BaseModel):
    transcript_path: str
    step_summary: str

zoom_agent = create_react_agent(
    model=client,
    tools=[zoom_find_transcript],
    prompt=(
        "You are a helpful assistant that can find transcript URLs of Zoom meetings. "
        "You can use the zoom_find_transcript tool to get the transcript URL of a Zoom meeting. "
        "Your job is done when you find the transcript URL of a Zoom meeting and return it to the user. Then it's up to user to download the transcript. "
        "For the step_summary field, describe what you accomplished for the user (e.g., 'Found transcript URL for meeting X' or 'Located recording for meeting Y'), "
        "not the actual content or URL details."
    ),
    response_format=ZoomAgentOutput,
)

import json
from typing import Dict

DOWNLOAD_DIR = Path("zoom_transcripts")
DOWNLOAD_DIR.mkdir(exist_ok=True)



# === Download transcript file ===
async def download_file(download_url: str, filename: Path, token: str):
    url_with_token = f"{download_url}?access_token={token}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url_with_token)
        resp.raise_for_status()
        filename.write_bytes(resp.content)
        logger.info(f"✅ Downloaded transcript: {filename}")
    return filename


async def zoom_agent_node(state: Dict) -> Dict:
    print("="*50)
    print("🤖 ZOOM AGENT")
    print("="*50)

    meeting_name = state.get("meeting_name", "Unknown meeting")
    transcript = state.get("transcript") or f"Transcript placeholder for {meeting_name}"

    next_step = state.get("next_step", "Unknown next step")
    result = await zoom_agent.ainvoke(
        {"messages": [{"role": "user", "content": f"This is your current task: {next_step}"}]},
    )

    # --- Extract transcript_path from result ---
    transcript_url = result['structured_response'].transcript_path
    step_summary = result['structured_response'].step_summary


    # Fallback if nothing was found
    transcript_url = transcript_url or state.get("transcript_path") or "/tmp/placeholder.txt"
    print("[ZOOM AGENT] Summary:", step_summary)
    return {
        **state,
        "transcript_path": transcript_url,
        "step_summary": [step_summary]
    }


