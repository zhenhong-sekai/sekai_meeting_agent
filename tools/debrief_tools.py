import os
import logging
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.tools import tool

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Initialize LangChain client
client = ChatOpenAI(
    model="gpt-4o",  # Using standard GPT-4 model
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://yunwu.ai/v1",
)




from typing import Dict, TypedDict

class SummaryResponse(TypedDict):
    summary: str
    key_points: list[str]
    participants: list[str]
    duration_estimate: str

@tool("create_summary")
async def create_summary(transcript: str) -> Dict:
    """
    Create a structured summary of the transcript.
    
    Args:
        transcript (str): The meeting transcript text to summarize
        
    Returns:
        Dict: A structured summary containing:
            - summary: A concise summary of the meeting
            - key_points: List of main points discussed
            - participants: List of meeting participants
            - duration_estimate: Estimated meeting duration
    """
    print("Creating summary of transcript")
    try:
        logger.info("Creating summary of transcript")
        result = await client.ainvoke(
            input=[
                {
                    "role": "system", 
                    "content": """You are a helpful assistant that creates structured meeting summaries.
                    Always return a JSON object with the following fields:
                    - summary: A concise summary of the key discussion points
                    - key_points: List of the main points discussed
                    - participants: List of people who spoke in the meeting
                    - duration_estimate: Estimated meeting duration based on transcript length and content
                    """
                },
                {
                    "role": "user", 
                    "content": f"""Analyze this transcript and provide a structured summary:
                    
                    {transcript}
                    
                    Return the response as a JSON object with summary, key_points (list), participants (list), and duration_estimate fields."""
                }
            ]
        )
        
        # Parse the response into structured format
        try:
            # The response might be in JSON format or natural language
            if isinstance(result.content, dict):
                structured_response = result.content
            else:
                # Try to extract JSON-like structure from the text
                import json
                import re
                
                # Find JSON-like structure in the text
                json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
                if json_match:
                    structured_response = json.loads(json_match.group())
                else:
                    # Fallback: Create basic structure from the text
                    structured_response = {
                        "summary": result.content,
                        "key_points": ["Summary provided as plain text"],
                        "participants": ["Unknown"],
                        "duration_estimate": "Unknown"
                    }
            
            logger.info("✅ Structured summary created successfully")
            return structured_response
            
        except Exception as e:
            logger.warning(f"Failed to parse structured response: {e}")
            # Fallback to basic structure
            return {
                "summary": result.content,
                "key_points": ["Summary provided as plain text"],
                "participants": ["Unknown"],
                "duration_estimate": "Unknown"
            }
    except Exception as e:
        logger.error(f"❌ Failed to create summary: {str(e)}")
        raise

class FeedbackResponse(TypedDict):
    overall_rating: int  # 1-10 rating
    positive_points: list[str]
    areas_for_improvement: list[str]
    specific_suggestions: list[str]
    engagement_metrics: Dict[str, int]  # e.g. {"participation_balance": 7, "discussion_flow": 8}

@tool("create_feedback")
async def create_feedback(transcript: str) -> Dict:
    """
    Create structured feedback for the transcript.
    
    Args:
        transcript (str): The meeting transcript text to analyze
        
    Returns:
        Dict: A structured feedback containing:
            - overall_rating: Meeting effectiveness rating (1-10)
            - positive_points: List of what went well
            - areas_for_improvement: List of what could be better
            - specific_suggestions: List of actionable suggestions
            - engagement_metrics: Dict of various engagement metrics
    """
    print("Creating feedback for transcript")
    try:
        logger.info("Creating feedback for transcript")
        result = await client.ainvoke(
            input=[
                {
                    "role": "system", 
                    "content": """You are an expert meeting analyst that provides structured feedback.
                    Always return a JSON object with the following fields:
                    - overall_rating: A rating from 1-10 on meeting effectiveness
                    - positive_points: List of what went well in the meeting
                    - areas_for_improvement: List of aspects that could be better
                    - specific_suggestions: List of actionable recommendations
                    - engagement_metrics: Dictionary with metrics like participation_balance, discussion_flow, etc.
                    
                    Base your analysis on factors like:
                    - Participant engagement and balance
                    - Meeting structure and flow
                    - Time management
                    - Discussion quality
                    - Decision-making effectiveness
                    """
                },
                {
                    "role": "user", 
                    "content": f"""Analyze this transcript and provide structured feedback:
                    
                    {transcript}
                    
                    Return the response as a JSON object with all the required fields."""
                }
            ]
        )
        
        # Parse the response into structured format
        try:
            if isinstance(result.content, dict):
                structured_response = result.content
            else:
                # Try to extract JSON-like structure from the text
                import json
                import re
                
                json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
                if json_match:
                    structured_response = json.loads(json_match.group())
                else:
                    # Fallback: Create basic structure
                    structured_response = {
                        "overall_rating": 5,
                        "positive_points": ["Feedback provided as plain text"],
                        "areas_for_improvement": ["Unable to parse structured feedback"],
                        "specific_suggestions": ["Review the feedback text: " + result.content],
                        "engagement_metrics": {
                            "participation_balance": 5,
                            "discussion_flow": 5
                        }
                    }
            
            logger.info("✅ Structured feedback created successfully")
            return structured_response
            
        except Exception as e:
            logger.warning(f"Failed to parse structured feedback: {e}")
            # Fallback to basic structure
            return {
                "overall_rating": 5,
                "positive_points": ["Feedback provided as plain text"],
                "areas_for_improvement": ["Unable to parse structured feedback"],
                "specific_suggestions": ["Review the feedback text: " + result.content],
                "engagement_metrics": {
                    "participation_balance": 5,
                    "discussion_flow": 5
                }
            }
    except Exception as e:
        logger.error(f"❌ Failed to create feedback: {str(e)}")
        raise

class TodoItem(TypedDict):
    task: str
    assignee: str
    due_date: str
    priority: str  # "high", "medium", "low"
    status: str  # "pending", "in_progress", "completed"
    context: str  # Any relevant context or notes

class TodoResponse(TypedDict):
    action_items: list[TodoItem]
    follow_ups: list[TodoItem]
    decisions: list[str]
    dependencies: Dict[str, list[str]]  # task -> list of dependent tasks

@tool("create_todo")
async def create_todo(transcript: str) -> Dict:
    """
    Create a structured todo list from the transcript.
    
    Args:
        transcript (str): The meeting transcript text to extract tasks from
        
    Returns:
        Dict: A structured todo list containing:
            - action_items: List of immediate tasks with assignees and priorities
            - follow_ups: List of future tasks or follow-up items
            - decisions: List of decisions that led to tasks
            - dependencies: Dictionary mapping tasks to their dependencies
    """
    print("Creating todo list from transcript")
    try:
        logger.info("Creating todo list from transcript")
        result = await client.ainvoke(
            input=[
                {
                    "role": "system", 
                    "content": """You are an expert project manager that extracts structured action items from meeting transcripts.
                    Always return a JSON object with the following fields:
                    - action_items: List of immediate tasks, each with:
                        - task: The task description
                        - assignee: Who is responsible
                        - due_date: When it should be done
                        - priority: "high", "medium", or "low"
                        - status: "pending", "in_progress", or "completed"
                        - context: Any relevant notes or context
                    - follow_ups: List of future tasks in the same format
                    - decisions: List of key decisions that led to tasks
                    - dependencies: Dictionary mapping tasks to lists of dependent tasks
                    
                    Guidelines:
                    - Extract clear, actionable items
                    - Identify responsible parties
                    - Set reasonable deadlines
                    - Note task dependencies
                    - Capture context from discussions
                    """
                },
                {
                    "role": "user", 
                    "content": f"""Extract structured action items from this transcript:
                    
                    {transcript}
                    
                    Return the response as a JSON object with all the required fields."""
                }
            ]
        )
        
        # Parse the response into structured format
        try:
            if isinstance(result.content, dict):
                structured_response = result.content
            else:
                # Try to extract JSON-like structure from the text
                import json
                import re
                
                json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
                if json_match:
                    structured_response = json.loads(json_match.group())
                else:
                    # Fallback: Create basic structure
                    structured_response = {
                        "action_items": [{
                            "task": "Review unstructured todo list",
                            "assignee": "Team",
                            "due_date": "ASAP",
                            "priority": "medium",
                            "status": "pending",
                            "context": result.content
                        }],
                        "follow_ups": [],
                        "decisions": ["Todo list was provided in unstructured format"],
                        "dependencies": {}
                    }
            
            logger.info("✅ Structured todo list created successfully")
            return structured_response
            
        except Exception as e:
            logger.warning(f"Failed to parse structured todo list: {e}")
            # Fallback to basic structure
            return {
                "action_items": [{
                    "task": "Review unstructured todo list",
                    "assignee": "Team",
                    "due_date": "ASAP",
                    "priority": "medium",
                    "status": "pending",
                    "context": result.content
                }],
                "follow_ups": [],
                "decisions": ["Todo list was provided in unstructured format"],
                "dependencies": {}
            }
    except Exception as e:
        logger.error(f"❌ Failed to create todo list: {str(e)}")
        raise