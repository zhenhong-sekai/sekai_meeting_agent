from typing import Literal, Optional
import operator

from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command
from typing_extensions import TypedDict
from src.agents.zoom_agent import zoom_agent_node
from src.agents.debrief_agent import debrief_agent_node
from src.agents.notion_agent import notion_agent_node
from src.agents.supervisor_agent import supervisor_agent_node
from src.config.settings import settings
from openai import OpenAI
import asyncio
from langchain_openai import ChatOpenAI
from typing_extensions import Annotated
from langgraph.graph.message import add_messages
from typing import List
 
client = ChatOpenAI(
    model=settings.MODEL_NAME,
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
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
    step_summary: Annotated[List[str], operator.add]
    next_step: Optional[str]



def log_final_summary(state: AgentState) -> AgentState:
    """Log the final step_summary at the end of the pipeline"""
    step_summary = state.get("step_summary", [])
    
    # Console logging
    print("\n" + "="*80)
    print("🎯 FINAL PIPELINE SUMMARY")
    print("="*80)
    print(f"Total steps completed: {len(step_summary)}")
    print("\n📋 Step Summary History:")
    for i, summary in enumerate(step_summary, 1):
        print(f"  {i}. {summary}")
    print("="*80)
    print("✅ Pipeline completed successfully!")
    print("="*80 + "\n")
    
    # Create a summary message for the API response
    summary_text = f"Pipeline completed with {len(step_summary)} steps:\n"
    for i, summary in enumerate(step_summary, 1):
        summary_text += f"{i}. {summary}\n"
    
    return {
        **state,
        "final_summary": summary_text,
        "step_summary": step_summary  # Keep the existing step_summary
    }

main_graph = StateGraph(AgentState)

main_graph.add_node("supervisor", supervisor_agent_node)
main_graph.add_node("zoom", zoom_agent_node)
main_graph.add_node("debrief", debrief_agent_node)
main_graph.add_node("notion", notion_agent_node)
main_graph.add_node("log_summary", log_final_summary)

main_graph.add_edge(START, "supervisor")

# Define the routing targets for each node
targets = {
    "zoom": "zoom",
    "debrief": "debrief",
    "notion": "notion",
    "end": "log_summary"
}

main_graph.add_conditional_edges(
    "supervisor",
    lambda state: state["route"],  # just pick the route we set in supervisor_agent_node
    targets
)
# After each agent completes, go back to supervisor for next routing decision
main_graph.add_edge("zoom", "supervisor")
main_graph.add_edge("debrief", "supervisor")
main_graph.add_edge("notion", "supervisor")

# Add edge from logging node to END
main_graph.add_edge("log_summary", END)


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
