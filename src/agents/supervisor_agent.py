from typing import Dict, Literal
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from src.config.settings import settings
from typing import List

client = ChatOpenAI(
    model="o3",
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)

class SupervisorAgentOutput(BaseModel):
    route: Literal["zoom", "debrief", "notion", "end"]
    next_step: str
    reasoning: str
    step_summary: str

supervisor_agent = create_react_agent(
    model=client,
    tools=[],
    prompt=(
        "You are a supervisor agent that acts as a router and decision maker for a meeting agent workflow. "
        "Your job is to analyze the current state and user request to determine the next step and which agent should handle it. "
        "You have access to the step_summary list, user's last message, and current workflow state. "
        "Make intelligent routing decisions based on what has been completed and what the user is requesting. "
        "You are responsible for generating the next_step field, which should clearly describe what the next agent will do for the user. "
        "For the step_summary field, describe what you accomplished for the user (e.g., 'Determined next step: route to debrief agent' or 'Analyzed workflow state and routed to zoom agent'), "
        "not the detailed reasoning or internal decision process."
    ),
    response_format=SupervisorAgentOutput,
)

async def supervisor_agent_node(state: Dict) -> Dict:
    print("="*50)
    print("🤖 SUPERVISOR AGENT")
    print("="*50)
    
    # Extract relevant information from state
    last_user_message = state.get("last_user_message", "")
    step_summary = state.get("step_summary", [])
    meeting_name = state.get("meeting_name", "")
    transcript_path = state.get("transcript_path", "")
    transcript = state.get("transcript", "")
    summary = state.get("summary", "")
    todo = state.get("todo", "")
    feedback = state.get("feedback", "")
    notion_parent_id = state.get("notion_parent_id", "")
    next_step = state.get("next_step", "")
    
    # Create a comprehensive context for the supervisor
    context = f"""
Current Workflow State:
- User's instruction: {last_user_message}
- Meeting name: {meeting_name or "Not specified"}
- Transcript available: {"Yes" if (transcript_path or transcript) else "No"}
- Summary generated: {"Yes" if summary else "No"}
- Todo list generated: {"Yes" if todo else "No"}
- Feedback generated: {"Yes" if feedback else "No"}
- Notion page created: {"Yes" if notion_parent_id else "No"}


Step Summary History:
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(step_summary)])}

Available Routes and Next Steps:
- 'zoom': Handle Zoom recordings/transcripts. Use when user needs transcript URL or transcript processing.
  Next step examples: "Find transcript URL for the meeting", "Locate Zoom recording for meeting X"
- 'debrief': Generate summaries, todos, and feedback from transcripts. Use when transcript is available and user wants analysis.
  Next step examples: "Generate meeting summary and extract action items", "Create summary and feedback from transcript"
- 'notion': Publish results to Notion. Use when user explicitly requests saving/publishing to Notion.
  Next step examples: "Create Notion page with meeting results", "Publish summary and todos to Notion"
- 'end': Terminate workflow. Use when all requested tasks are complete or user wants to end.
  Next step examples: "Complete workflow - all tasks finished", "End workflow - user request fulfilled"

Routing Rules:
1. If user asks for transcript/recording and none is available → 'zoom'
2. If transcript is available and user wants summary/todo/feedback → 'debrief'
3. If user explicitly mentions Notion/saving/publishing → 'notion'
4. If all requested tasks are complete → 'end'
5. If user asks to end/stop → 'end'
6. Default after debrief unless Notion is explicitly requested → 'end'

Please analyze the current state and user request to determine the appropriate next step.
"""
    
    # Create the user message for the supervisor
    user_message = f"""
User Instruction: {last_user_message}

{context}

Based on the current state and user request, determine:
1. Which route to take (zoom/debrief/notion/end)
2. What the next step should be - clearly describe what the next agent will accomplish for the user, and also include relevant context for the next agent to know what to do. Make sure to include the user's instruction in the next step.
3. Your reasoning for this decision

Return a structured response with your routing decision and next step description.
"""
    
    # Invoke the supervisor agent
    result = await supervisor_agent.ainvoke(
        {"messages": [{"role": "user", "content": user_message}]}
    )
    
    # Extract the structured response
    structured_response = result['structured_response']
    route = structured_response.route
    next_step = structured_response.next_step
    reasoning = structured_response.reasoning
    
    print("[SUPERVISOR AGENT] Summary:")
    print(f"[SUPERVISOR AGENT] Route: {route}")
    print(f"[SUPERVISOR AGENT] Step Summary: {step_summary}")
    
    supervisor_summary = structured_response.step_summary
    return {
        **state,
        "route": route,
        "next_step": next_step,
        "step_summary": [supervisor_summary]
    }
