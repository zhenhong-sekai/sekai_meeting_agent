from typing import Dict
from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command
from typing_extensions import TypedDict
from src.agents.zoom_agent import zoom_agent_node
from src.agents.notion_agent import notion_agent_node
from src.config.settings import settings
from openai import OpenAI
from src.tools.debrief_tools import create_summary, create_feedback, create_todo
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from utils.get_transcript import load_transcript
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage

client = ChatOpenAI(
    model="gpt-4o", 
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)

class DebriefAgentOutput(BaseModel):
    summary: str
    todo: str
    feedback: str
    step_summary: str

debrief_agent = create_react_agent(
    model=client,
    tools=[create_summary, create_feedback, create_todo],
    prompt=(
        "You are a helpful assistant that can create summaries, feedback, and todos from a transcript. "
        "Use the create_summary tool to generate meeting summaries, "
        "create_todo tool to extract action items, and "
        "create_feedback tool to provide constructive feedback. "
        "Always analyze the user's request to determine which tools to use. "
        "For the step_summary field, describe what you accomplished for the user (e.g., 'Generated meeting summary' or 'Extracted action items from transcript'), "
        "not the actual content of the summary, todo, or feedback."
    ),
    debug=True,
    response_format=DebriefAgentOutput,
)

async def debrief_agent_node(state: Dict) -> Dict:
    print("="*50)
    print("🤖 DEBRIEF AGENT")
    print("="*50)
    
    user_message = state.get("last_user_message", "")
    transcript_path = state.get("transcript_path")
    transcript = load_transcript(transcript_path) if transcript_path else "No transcript provided"

    # # === First call: figure out intent ===
    # intent_prompt = [
    #     {"role": "system", "content": "You are a classifier. Return ONLY one of: summary, todo, feedback, all."},
    #     {"role": "user", "content": f"User message: {user_message}"}
    # ]
    # intent_result = await client.ainvoke(intent_prompt)
    # intent = intent_result.content.strip().lower()
    # print("[DEBRIEF AGENT] Detected intent:", intent)

    # === Second call: do the work ===
    # task = ""
    # if intent == "summary":
    #     task = "Create a summary of the transcript."
    # elif intent == "todo":
    #     task = "Extract a todo list from the transcript."
    # elif intent == "feedback":
    #     task = "Provide constructive feedback about the meeting."
    # else:
    #     task = "Produce all three: summary, todo, feedback."

    current_step = state.get("next_step", "")
    output_prompt = [
        {"role": "system", "content": "You are a helpful assistant for meeting debriefs. Return JSON."},
        {"role": "user", "content": f"Current task: {current_step}\n\n\n Transcript:\n{transcript}"}
    ]

    result = await client.ainvoke(
        output_prompt,
        response_format=DebriefAgentOutput  # ensures structured output
    )
    print("Result: ", result)

    # Get the parsed structured output
    parsed: DebriefAgentOutput = result.additional_kwargs["parsed"]

    print("[DEBRIEF AGENT] Step Summary:", parsed.step_summary)
    print("[DEBRIEF AGENT] Summary:", parsed.summary)

    return {
        **state,
        "summary": parsed.summary,
        "todo": parsed.todo,
        "feedback": parsed.feedback,
        "step_summary": [parsed.step_summary]
    }