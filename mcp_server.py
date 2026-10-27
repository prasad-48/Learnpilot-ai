
import json
import sys
from contextlib import redirect_stdout

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from agent_graph import tutor_graph
import database


# Initialize MCP server.
# stdout must remain available for MCP JSON-RPC messages.
mcp = FastMCP("Education_Tutor_MCP")


@mcp.tool()
async def invoke_tutor(
    task: str = Field(description="The educational request, such as explain fractions"),
    student_id: str = Field(description="Unique identifier for the student"),
    student_name: str = Field(description="Student's name"),
    grade_level: str = Field(description="Grade level, such as Grade 8"),
    age: int = Field(description="Student's age"),
    learning_style: str = "reading",
    language: str = "English",
) -> str:
    """
    Submit an educational task to the EduPilot Orchestrator.

    Automatically routes the request to the appropriate specialist:
    Lesson Personalizer, Quiz Generator, Progress Tracker,
    Doubt Resolver, or Parent Reporter.
    """

    # Validate required values.
    if not task or not task.strip():
        return json.dumps({
            "status": "error",
            "message": "Task cannot be empty."
        })

    if not student_id or not student_id.strip():
        return json.dumps({
            "status": "error",
            "message": "Student ID cannot be empty."
        })

    if not student_name or not student_name.strip():
        return json.dumps({
            "status": "error",
            "message": "Student name cannot be empty."
        })

    if age <= 0:
        return json.dumps({
            "status": "error",
            "message": "Age must be a positive integer."
        })

    try:
        # Retrieve the student's existing mastery levels.
        mastery_levels = database.get_student_mastery(student_id)

        # Build the student profile.
        student_profile = {
            "student_id": student_id,
            "name": student_name,
            "grade_level": grade_level,
            "age": age,
            "learning_style": learning_style,
            "language": language,
            "mastery_levels": mastery_levels,
        }

        # Save or update the student profile.
        database.upsert_student(student_profile)

        # Prepare the initial LangGraph state.
        state = {
            "task_input": task.strip(),
            "student_profile": student_profile,
            "classification": {},
            "final_response": None,
        }

        # Redirect ordinary Python stdout output from the graph
        # to stderr so it does not corrupt MCP's JSON-RPC stream.
        with redirect_stdout(sys.stderr):
            final_state = await tutor_graph.ainvoke(state)

        classification = final_state.get("classification") or {}
        agent_invoked = classification.get("next_agent", "unknown")
        response = final_state.get("final_response") or {}

        # Log the interaction.
        database.log_session(
            student_id,
            agent_invoked,
            task.strip(),
            response,
        )

        # Update mastery when the Progress Tracker is invoked.
        if agent_invoked == "progress_tracker":
            output = response.get("output") or {}
            mastery_map = output.get("mastery_map") or {}

            for subject, topics in mastery_map.items():
                if not isinstance(topics, dict):
                    continue

                for topic_name, details in topics.items():
                    if not isinstance(details, dict):
                        continue

                    score = details.get("score", 0)
                    database.update_topic_mastery(
                        student_id,
                        topic_name,
                        score,
                    )

        return json.dumps({
            "status": "success",
            "agent_invoked": agent_invoked,
            "response": response,
        }, indent=2, ensure_ascii=False, default=str)

    except Exception as exc:
        # Keep the tool response readable for the MCP client.
        # Do not print the exception to stdout.
        return json.dumps({
            "status": "error",
            "message": str(exc),
        }, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # MCP stdio transport owns stdout; do not redirect it globally.
    mcp.run(transport="stdio")
