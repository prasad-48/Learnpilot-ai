
import traceback
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from agent_graph import tutor_graph
import database


app = FastAPI(
    title="MCP Education Tutor API",
    description="Central orchestration point for educational AI agents",
    version="1.0.0",
)

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
    task: str = Field(min_length=1)
    student: StudentProfile
    context: Optional[Dict[str, Any]] = None

    @field_validator("task")
    @classmethod
    def task_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Task cannot be empty or whitespace.")
        return value


# ---- API Endpoints ----
@app.post("/api/v1/tutor/solve")
async def solve_tutor_task(request: TaskRequest):
    """Route a student's task through the AI tutor orchestration graph."""

    try:
        student_dict = request.student.model_dump()
        student_id = student_dict["student_id"]

        student_dict["mastery_levels"] = database.get_student_mastery(
            student_id
        )
        database.upsert_student(student_dict)

        state = {
            "task_input": request.task,
            "student_profile": student_dict,
            "classification": {},
            "final_response": None,
        }

        final_state = await tutor_graph.ainvoke(state)

        agent_invoked = final_state.get(
            "classification", {}
        ).get("next_agent", "unknown")

        response = final_state.get("final_response", {})

        database.log_session(
            student_id, agent_invoked, request.task, response
        )

        if agent_invoked == "progress_tracker":
            output = response.get("output", {})
            mastery_map = output.get("mastery_map", {})

            for subject, topics in mastery_map.items():
                for topic_name, details in topics.items():
                    score = details.get("score", 0)
                    database.update_topic_mastery(
                        student_id, topic_name, score
                    )

        return {
            "status": "success",
            "agent_invoked": agent_invoked,
            "response": response,
        }

    except Exception as e:
        error_message = str(e)
        traceback.print_exc()

        # Gemini quota / rate-limit errors
        if (
            "RESOURCE_EXHAUSTED" in error_message
            or "429" in error_message
            or "quota" in error_message.lower()
        ):
            raise HTTPException(
                status_code=429,
                detail={
                    "message": (
                        "The AI service has reached its usage quota. "
                        "Please try again when your Gemini quota resets, "
                        "or configure a billing-enabled API key."
                    ),
                    "error_type": "AI_QUOTA_EXCEEDED",
                },
            ) from e

        raise HTTPException(
            status_code=500,
            detail={
                "message": "An error occurred while processing your task.",
                "error_type": "INTERNAL_SERVER_ERROR",
            },
        ) from e


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
