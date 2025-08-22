import os
import time
import urllib.parse
import httpx
import re
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

# === Zoom App Credentials ===
ZOOM_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")

# Token cache
access_token = None
token_expiry = 0

# Download directory
DOWNLOAD_DIR = Path("zoom_transcripts")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Logger
logger = logging.getLogger(__name__)


# === Helper: Get Zoom Access Token ===
async def get_access_token():
    global access_token, token_expiry
    now = time.time()
    if access_token and now < token_expiry:
        return access_token

    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ZOOM_ACCOUNT_ID}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, auth=(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET))
        resp.raise_for_status()
        data = resp.json()
        access_token = data["access_token"]
        token_expiry = now + data["expires_in"] - 60
        return access_token


# === Download transcript file ===
async def download_file(download_url: str, filename: Path, token: str):
    url_with_token = f"{download_url}?access_token={token}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url_with_token)
        resp.raise_for_status()
        filename.write_bytes(resp.content)
        logger.info(f"✅ Downloaded transcript: {filename}")
    return filename


# === Clean transcript into "Speaker: text" ===
def process_transcript(vtt_file: Path) -> Path:
    """
    Convert Zoom WEBVTT transcript into simple 'Speaker: text' lines.
    """
    lines_out = []
    with vtt_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("WEBVTT"):
                continue
            if re.match(r"^\d+$", line):  # skip cue numbers
                continue
            if "-->" in line:  # skip timestamps
                continue
            # Keep only actual transcript lines
            lines_out.append(line)

    # Save cleaned transcript
    clean_file = vtt_file.with_suffix(".txt")
    clean_file.write_text("\n".join(lines_out), encoding="utf-8")
    logger.info(f"📝 Cleaned transcript saved to {clean_file}")
    return clean_file


# === Tool: Search Zoom Recordings by Topic and Return Transcript ===
# === Tool: Search Zoom Recordings by Topic and Return Transcript ===
@tool("zoom_find_transcript")
async def zoom_find_transcript(meeting_name: str) -> dict:
    """
    Search for a Zoom meeting by its topic, download its transcript, and return transcript text.
    Input: meeting_name (str) - part or full name of the meeting topic.
    Output: dict with meeting metadata and transcript text.
    """

    print(f"[zoom_find_transcript] Searching transcript for meeting: {meeting_name}")
    token = await get_access_token()
    print("[zoom_find_transcript] ✅ Got access token")

    # List account recordings
    url = "https://api.zoom.us/v2/accounts/me/recordings"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"Authorization": f"Bearer {token}"}, params={"page_size": 30})
        resp.raise_for_status()
        data = resp.json()
    print(f"[zoom_find_transcript] 📂 Retrieved {len(data.get('meetings', []))} meetings")

    meetings = data.get("meetings", [])
    for meeting in meetings:
        topic = meeting.get("topic", "").strip()
        meeting_id = meeting.get("id")
        uuid = meeting.get("uuid")
        print(f"[zoom_find_transcript] 🔎 Checking meeting: {topic} (id={meeting_id})")

        if meeting_name not in topic:
            continue

        print(f"[zoom_find_transcript] ✅ Match found for topic: {topic}")
        encoded_uuid = urllib.parse.quote(urllib.parse.quote(uuid, safe=""), safe="")
        url = f"https://api.zoom.us/v2/meetings/{encoded_uuid}/recordings"

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers={"Authorization": f"Bearer {token}"})
            resp.raise_for_status()
            rec_data = resp.json()
        print(f"[zoom_find_transcript] 🎥 Found {len(rec_data.get('recording_files', []))} recording files")

        files = rec_data.get("recording_files", [])
        for f in files:
            file_type = f.get("file_type")
            download_url = f.get("download_url")
            print(f"[zoom_find_transcript] ▶️ File type={file_type}, download_url={bool(download_url)}")

            if not download_url:
                continue

            if file_type in ("TRANSCRIPT", "VTT"):
                safe_topic = topic.replace(" ", "_")
                filename = DOWNLOAD_DIR / f"{meeting_id}_{safe_topic}_{file_type}.vtt"
                print(f"[zoom_find_transcript] ⬇️ Downloading transcript to {filename}")
                vtt_file = await download_file(download_url, filename, token)

                clean_file = process_transcript(vtt_file)
                print(f"[zoom_find_transcript] 🧹 Processed transcript saved at {clean_file}")
                transcript_text = clean_file.read_text(encoding="utf-8")

                print(f"[zoom_find_transcript] ✅ Returning transcript for {topic}")
                return {
                    "meeting_id": meeting_id,
                    "topic": topic,
                    "transcript_path": str(clean_file),
                }

    print(f"[zoom_find_transcript] ❌ No transcript found for meeting: {meeting_name}")
    return {"error": f"No transcript found for meeting '{meeting_name}'"}

ZOOM_TOOLS = [zoom_find_transcript]