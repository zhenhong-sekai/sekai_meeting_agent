from typing import Literal, Optional

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command
from typing_extensions import TypedDict
from zoom_agent import zoom_agent_node
from debrief_agent import debrief_agent_node
from notion_agent import notion_agent_node
from dotenv import load_dotenv
import os
from openai import OpenAI
import asyncio
from langchain_openai import ChatOpenAI
load_dotenv()

client = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://yunwu.ai/v1",
)


class AgentState(TypedDict, total=False):
    last_user_message: str
    meeting_name: Optional[str]
    transcript_path: Optional[str]
    transcript: Optional[str]
    summary: Optional[str]
    todo: Optional[str]
    feedback: Optional[str]
    notion_parent_id: Optional[str]
    route: Optional[Literal["zoom", "debrief", "notion", "end"]]
    next_step: Optional[str]

def routing_function(state: AgentState) -> Literal["zoom", "debrief", "notion", "end"]:
    text = (state.get("last_user_message") or "").lower()

    print("AT ROUTING FUNCTION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("Check have transcript", bool(state.get('transcript') or state.get('transcript_path')))
    print("Check have debrief", bool(state.get('summary') and state.get('todo') and state.get('feedback')))
    print("Check meeting name", state.get('meeting_name') or '')
    print("Check last user message", text)
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are a router for a meeting agent graph. "
                "Your task is to return ONLY one of these exact lowercase tokens: zoom | debrief | notion | end"
            )
        },
        {
            "role": "user",
            "content": f"""Descriptions:
    - 'zoom': Handles Zoom recordings or transcripts. Only returns url, leave it to the user to download the transcript.
    - 'debrief': Produces summaries, todos, and feedback from transcripts.
    - 'notion': Publishes results (summary, todos, feedback) to Notion. 
    ⚠️ Only choose 'notion' if the user explicitly requests saving, publishing, or sending results to Notion.
    - 'end': Terminates the workflow. 
    ⚠️ Default choice after 'debrief' unless the user clearly asked for Notion.

    User message: {text}

    Next step: {state.get('next_step') or ''}

    Current workflow state:
    - Transcript status: {"Transcript already loaded and available" if (state.get('transcript') or state.get('transcript_path')) else "No transcript has been loaded yet"}
    - Summary status: {"Summary has been generated" if state.get('summary') else "Summary not generated yet"}
    - Todo status: {"Todo list has been generated" if state.get('todo') else "Todo list not generated yet"}
    - Feedback status: {"Feedback has been generated" if state.get('feedback') else "Feedback not generated yet"}
    - Meeting name: {state.get('meeting_name') or "No meeting name provided"}
    - Notion parent ID: {"Notion page created" if state.get('notion_parent_id') else "No Notion page created yet"}
    
    Examples:
    - User: "help me download transcript of meeting X"
    State: Transcript already loaded and available
    Answer: end   (because transcript is already present)

    - User: "summarise meeting Y"
    State: Transcript available
    Answer: debrief
    
    Instruction:
    Return exactly one token: zoom | debrief | notion | end
    """
        }
    ]



    print("messages", messages)
    decision = client.invoke(
        input=messages,
    )


    decision = decision.content.strip().lower()
    print("decision", decision)
    return decision

def router_node(state: AgentState) -> AgentState:
    text = (state.get("last_user_message") or "").lower()
    completion = client.invoke(
        input=[
            {"role": "system", "content": "You are a router for a meeting agent graph. Your task is to return ONLY one of these exact lowercase tokens: zoom | debrief | notion | end"},
            {"role": "user", "content": f"""Descriptions:
- 'zoom': Handles Zoom recordings or transcripts.
- 'debrief': Produces summaries, todos, and feedback.
- 'notion': Publishes results to Notion.
- 'end': Terminates the workflow.
- If the user explicitly mentions one of these nodes, return that node.

User message: {text}
Have transcript: {bool(state.get('transcript') or state.get('transcript_path'))}
Summary created: {bool(state.get('summary'))}
Todo created: {bool(state.get('todo'))}
Feedback created: {bool(state.get('feedback'))}
Meeting name: {state.get('meeting_name') or ''}

Answer with exactly one token: zoom | debrief | notion | end"""}
        ]
    )
    decision = completion.content.strip().lower()
    print("decision", decision)
    return {**state, "route": decision}

main_graph = StateGraph(AgentState)

main_graph.add_node("router", router_node)
main_graph.add_node("zoom", zoom_agent_node)
main_graph.add_node("debrief", debrief_agent_node)
main_graph.add_node("notion", notion_agent_node)

main_graph.add_edge(START, "router")

# Define the routing targets for each node
targets = {
    "zoom": "zoom",
    "debrief": "debrief",
    "notion": "notion",
    "end": END
}

main_graph.add_conditional_edges(
    "router",
    lambda state: state["route"],  # just pick the route we set in router_node
    targets
)
# main_graph.add_conditional_edges("r", routing_function, targets)
main_graph.add_conditional_edges("zoom", routing_function, targets)
main_graph.add_conditional_edges("debrief", routing_function, targets)
main_graph.add_conditional_edges("notion", routing_function, targets)


compiled_graph = main_graph.compile()



if __name__ == "__main__":
    async def run():
        async for update in compiled_graph.astream({
            "last_user_message": "Help me get transcipt of meet recording named AI Sharing分享 and summarise it"
        }):
            # Each `update` is a dict { node_name: {state_update...} }
            for node, payload in update.items():
                if "messages" in payload:
                    for msg in payload["messages"]:
                        if isinstance(msg, AIMessage):
                            print(f"[AI@{node}]", msg.content)
                else:
                    print(f"[{node}] → {payload}")

    asyncio.run(run())
