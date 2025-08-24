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
    next_step: str
    step_summary: str

zoom_agent = create_react_agent(
    model=client,
    tools=[zoom_find_transcript],
    prompt=(
        "You are a helpful assistant that can find transcript URLs of Zoom meetings. "
        "You can use the zoom_find_transcript tool to get the transcript URL of a Zoom meeting. "
        "Your job is done when you find the transcript URL of a Zoom meeting and return it to the user.THen its up to user to download the transcript."
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
    print("At ZOOM AGENT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("state", state)

    meeting_name = state.get("meeting_name", "Unknown meeting")
    transcript = state.get("transcript") or f"Transcript placeholder for {meeting_name}"

    print("last_user_message", state.get("last_user_message"))
    result = await zoom_agent.ainvoke(
        {"messages": [{"role": "user", "content": f"{state.get('last_user_message')}"}]},
    )

    # print("result", result)

    # --- Extract transcript_path from result ---
    transcript_url = result['structured_response'].transcript_path
    next_step = result['structured_response'].next_step
    step_summary = result['structured_response'].step_summary
    print("NEXT STEP", next_step)
    print("TRANSCRIPT URL", transcript_url)
    # if "messages" in result:
    #     for msg in result["messages"]:
    #         # ToolMessages usually contain the JSON with the transcript path
    #         if hasattr(msg, "content") and isinstance(msg.content, str):
    #             try:
    #                 data = json.loads(msg.content)
    #                 if "transcript_path" in data:
    #                     transcript_url = data["transcript_path"]
    #                     break
    #             except Exception:
    #                 pass

    # Fallback if nothing was found
    transcript_url = transcript_url or state.get("transcript_path") or "/tmp/placeholder.txt"
    # transcript =  load_transcript(transcript_url)
    # print("transcript", transcript)
    print("transcript_url", transcript_url)
    print("STEP SUMMARY", step_summary)
    return {
        **state,
        "transcript_path": transcript_url,
        "next_step": next_step,
        "step_summary": [step_summary]
    }


