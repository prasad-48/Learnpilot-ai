import asyncio
import json
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from agent_graph import tutor_graph
import database

# Initialize FastMCP Server
mcp = FastMCP("Education_Tutor_MCP")

@mcp.tool()
async def invoke_tutor(
    task: str,
    student_id: str,
    student_name: str,
    grade_level: str,
    age: int,
    learning_style: str = "reading",
    language: str = "English"
) -> str:
    """
    Submits an educational task to the EduPilot Orchestrator. 
    It classifies the request and routes the task automatically to the correct specialized agent 
    (Lesson Personalizer, Quiz Generator, Progress Tracker, Doubt Resolver, or Parent Reporter).
    
    Args:
        task: The educational request (e.g. "teach me fractions", "generate a quiz about photosynthesis")
        student_id: Unique identifier for the student
        student_name: Student's first name
        grade_level: Grade level (e.g. "Grade 7")
        age: Age of the student
        learning_style: Preferred learning style ("visual", "auditory", "reading", "kinesthetic")
        language: Language for instruction
    """
    # Fetch real mastery levels from our SQLite database
    mastery_levels = database.get_student_mastery(student_id)
    
    # Build student profile dictionary
    student_profile = {
        "student_id": student_id,
        "name": student_name,
        "grade_level": grade_level,
        "age": age,
        "learning_style": learning_style,
        "language": language,
        "mastery_levels": mastery_levels
    }
    
    # Save the profile to DB
    database.upsert_student(student_profile)
    
    # Prepare the initial LangGraph state
    state = {
        "task_input": task,
        "student_profile": student_profile,
        "classification": {},
        "final_response": None
    }
    
    try:
        # Run synchronous LangGraph execution
        final_state = tutor_graph.invoke(state)
        
        agent_invoked = final_state.get("classification", {}).get("next_agent", "unknown")
        response = final_state.get("final_response", {})
        
        result = {
            "status": "success",
            "agent_invoked": agent_invoked,
            "response": response
        }
        
        # Log this entire interaction into SQLite
        database.log_session(student_id, agent_invoked, task, response)
        
        # If the progress tracker was invoked, update topic mastery globally
        if agent_invoked == "progress_tracker":
            output = response.get("output", {})
            mastery_map = output.get("mastery_map", {})
            for subject, topics in mastery_map.items():
                for topic_name, details in topics.items():
                    score = details.get("score", 0)
                    database.update_topic_mastery(student_id, topic_name, score)
                    
        return json.dumps(result, indent=2)
    except Exception as e:
        error_res = {
            "status": "error",
            "message": str(e)
        }
        return json.dumps(error_res, indent=2)


if __name__ == "__main__":
    # Start the MCP server using stdout transport natively supported by FastMCP
    mcp.run(transport='stdio')
