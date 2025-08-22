from pathlib import Path
from loguru import logger

def load_transcript(transcript_url: str) -> str:
    """
    Load transcript from local zoom_transcripts folder.
    transcript_url example: 'zoom_transcripts/85720082470_AI_Sharing分享_TRANSCRIPT.txt'
    """
    path = Path(transcript_url)

    if not path.exists():
        logger.error(f"❌ Transcript file not found: {path}")
        return f"[Transcript unavailable: {path}]"

    text = path.read_text(encoding="utf-8")
    logger.info(f"✅ Loaded transcript: {path}")
    return text
