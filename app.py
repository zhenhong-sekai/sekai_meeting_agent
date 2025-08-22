import streamlit as st
import asyncio
from graph import compiled_graph
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Meeting Agent",
    page_icon="🤖",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .agent-message {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .zoom-message {
        background-color: #f0f8ff;
    }
    .debrief-message {
        background-color: #f0fff0;
    }
    .notion-message {
        background-color: #fff0f5;
    }
    .final-message {
        background-color: #e6ffe6;
        border: 2px solid #4CAF50;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-size: 1.1em;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 Meeting Agent Interface")

# Description
st.markdown("""
This interface helps you interact with the Meeting Agent pipeline. You can:
- Get transcripts from Zoom recordings
- Generate summaries, todos, and feedback
- Save results to Notion
""")

# Main query input
user_query = st.text_area("Enter your query:", 
    placeholder="Example: Help me get transcript of meet recording named 'AI Sharing分享' and summarize it",
    height=100)

# Initialize session state for messages if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
# Track if the pipeline has ended
if 'pipeline_ended' not in st.session_state:
    st.session_state.pipeline_ended = False

# Submit button
if st.button("Submit Query", type="primary"):
    if not user_query:
        st.warning("Please enter a query first.")
    else:
        # Clear previous messages
        st.session_state.messages = []
        
        # Create a placeholder for streaming updates
        messages_container = st.empty()
        
        async def process_query():
            try:
                # Reset pipeline state
                st.session_state.pipeline_ended = False
                
                async for update in compiled_graph.astream({
                    "last_user_message": user_query
                }):
                    # Each `update` is a dict { node_name: {state_update...} }
                    for node, payload in update.items():
                        if isinstance(payload, dict):
                            # Check if this is the end of the pipeline
                            if "route" in payload and payload["route"] == "end":
                                st.session_state.pipeline_ended = True
                            
                            # Handle messages
                            if "messages" in payload:
                                for msg in payload["messages"]:
                                    message = f"[{node}] {msg.content}"
                                    st.session_state.messages.append({
                                        "node": node,
                                        "content": msg.content,
                                        "is_final": st.session_state.pipeline_ended and msg == payload["messages"][-1]
                                    })
                            # Handle other updates
                            else:
                                message = f"[{node}] → {payload}"
                                st.session_state.messages.append({
                                    "node": node,
                                    "content": str(payload),
                                    "is_final": st.session_state.pipeline_ended
                                })
                            
                            # Update the display
                            messages_html = ""
                            for msg in st.session_state.messages:
                                node_class = f"{msg['node'].lower()}-message"
                                if msg.get('is_final'):
                                    node_class += " final-message"
                                messages_html += f"""
                                <div class="agent-message {node_class}">
                                    <strong>{msg['node']}</strong>: {msg['content']}
                                </div>
                                """
                            messages_container.markdown(messages_html, unsafe_allow_html=True)
                            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        
        # Run the async function
        with st.spinner("Processing your query..."):
            asyncio.run(process_query())

# Display a divider
st.divider()

# Footer
st.markdown("""
    <div style='text-align: center; color: grey; padding: 20px;'>
        Made with ❤️ by the Meeting Agent Team
    </div>
""", unsafe_allow_html=True)