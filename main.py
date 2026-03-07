from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from agent_graph import tutor_graph
import database

app = FastAPI(
    title="MCP Education Tutor API", 
    description="Central orchestration point for educational AI agents",
    version="1.0.0"
)

# Allow CORS for the Vanilla JS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Request Models ----
class StudentProfile(BaseModel):
    student_id: str
    name: str
    grade_level: str
    age: int
    learning_style: str = "reading"
    language: str = "English"

class TaskRequest(BaseModel):
    task: str
    student: StudentProfile
    context: Optional[Dict[str, Any]] = None

# ---- API Endpoints ----
@app.post("/api/v1/tutor/solve")
async def solve_tutor_task(request: TaskRequest):
    """
    Submits a task (e.g., "I need a lesson", "give me a quiz") to the Orchestrator,
    which routes to the specific CrewAI agent inside the LangGraph.
    """
    # Hydrate student profile with database mastery records
    student_dict = request.student.model_dump()
    student_id = student_dict["student_id"]
    
    student_dict["mastery_levels"] = database.get_student_mastery(student_id)
    
    # Save the profile to DB
    database.upsert_student(student_dict)

    # Prepare the initial state
    state = {
        "task_input": request.task,
        "student_profile": student_dict,
        "classification": {},
        "final_response": None
    }
    
    # Run graph execution
    try:
        final_state = tutor_graph.invoke(state)
        
        agent_invoked = final_state.get("classification", {}).get("next_agent", "unknown")
        response = final_state.get("final_response", {})
        
        # Log this entire interaction into SQLite
        database.log_session(student_id, agent_invoked, request.task, response)
        
        # If the progress tracker was invoked, update topic mastery globally
        if agent_invoked == "progress_tracker":
            output = response.get("output", {})
            mastery_map = output.get("mastery_map", {})
            for subject, topics in mastery_map.items():
                for topic_name, details in topics.items():
                    score = details.get("score", 0)
                    database.update_topic_mastery(student_id, topic_name, score)
                    
        return {
            "status": "success",
            "agent_invoked": agent_invoked,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
