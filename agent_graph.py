import json
from typing import Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

from llm_config import get_orchestrator_llm, get_reasoning_llm
from education_tutor_prompts import (
    ORCHESTRATOR_PROMPT,
    PROGRESS_TRACKER_PROMPT,
    PARENT_REPORTER_PROMPT,
    build_agent_prompt_with_student,
)
from crew_agents import (
    run_lesson_personalizer,
    run_quiz_generator,
    run_doubt_resolver,
)
import rag_pipeline


# ---- State Definition ----
class TutorState(dict):
    task_input: str
    student_profile: dict[str, Any]
    classification: Optional[dict[str, Any]]
    final_response: Optional[dict[str, Any]]


# ---- Helper Functions ----
def response_content_to_text(content: Any) -> str:
    """Convert an LLM response's content to plain text."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for block in content:
            if isinstance(block, dict):
                text_parts.append(str(block.get("text", "")))
            else:
                text_parts.append(str(block))

        return "\n".join(text_parts)

    return str(content)


def parse_json_response(content: Any) -> dict[str, Any]:
    """Parse JSON returned by an LLM, including fenced JSON."""
    clean_json = response_content_to_text(content).strip()

    if clean_json.startswith("```"):
        lines = clean_json.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        clean_json = "\n".join(lines).strip()

    # Extract a JSON object if the model adds surrounding text.
    if not clean_json.startswith("{"):
        start = clean_json.find("{")
        end = clean_json.rfind("}")

        if start != -1 and end > start:
            clean_json = clean_json[start:end + 1]

    result = json.loads(clean_json)

    if not isinstance(result, dict):
        raise ValueError("Expected the LLM to return a JSON object.")

    return result


# ---- Orchestrator Node ----
async def orchestrator_node(state: TutorState) -> TutorState:
    """Classify the task and route it to the appropriate specialist."""
    task = state.get("task_input", "")
    llm = get_orchestrator_llm()

    messages = [
        SystemMessage(content=ORCHESTRATOR_PROMPT),
        HumanMessage(
            content=(
                "Classify this incoming task and return exactly the required "
                f"JSON format: '{task}'"
            )
        ),
    ]

    try:
        response = await llm.ainvoke(messages)
        classification = parse_json_response(response.content)

        task_type = str(
            classification.get("task_type", "doubt")
        ).lower()

        next_agent = "doubt_resolver"

        if "lesson" in task_type:
            next_agent = "lesson_personalizer"
        elif "quiz" in task_type:
            next_agent = "quiz_generator"
        elif "progress" in task_type:
            next_agent = "progress_tracker"
        elif "report" in task_type:
            next_agent = "parent_reporter"
        elif "doubt" in task_type:
            next_agent = "doubt_resolver"

        classification["next_agent"] = next_agent
        state["classification"] = classification

    except Exception as exc:
        print(f"Orchestrator Error: {exc}")

        state["classification"] = {
            "task_type": "doubt",
            "next_agent": "doubt_resolver",
        }

    return state


# ---- Lesson Personalizer Node ----
async def lesson_personalizer_node(state: TutorState) -> TutorState:
    profile = state.get("student_profile", {})
    task = state.get("task_input", "")

    result = await run_lesson_personalizer(profile, task)

    state["final_response"] = {
        "agent": "LessonPersonalizer",
        "output": result,
    }

    return state


# ---- Quiz Generator Node ----
async def quiz_generator_node(state: TutorState) -> TutorState:
    profile = state.get("student_profile", {})
    task = state.get("task_input", "")

    result = await run_quiz_generator(profile, task)

    state["final_response"] = {
        "agent": "QuizGenerator",
        "output": result,
    }

    return state


# ---- Doubt Resolver Node ----
async def doubt_resolver_node(state: TutorState) -> TutorState:
    profile = state.get("student_profile", {})
    task = state.get("task_input", "")

    # Retrieve curriculum context from the local vector database.
    retrieved_context = rag_pipeline.retrieve_context(
        task,
        n_results=2,
    )

    result = await run_doubt_resolver(
        profile,
        task,
        retrieved_context,
    )

    state["final_response"] = {
        "agent": "DoubtResolver",
        "output": result,
        "rag_context_used": retrieved_context,
    }

    return state


# ---- Progress Tracker Node ----
async def progress_tracker_node(state: TutorState) -> TutorState:
    profile = state.get("student_profile", {})
    task = state.get("task_input", "")

    llm = get_reasoning_llm()
    prompt = build_agent_prompt_with_student(
        PROGRESS_TRACKER_PROMPT,
        profile,
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(
            content=(
                "Process this progress request and return the structured "
                f"JSON: '{task}'"
            )
        ),
    ]

    try:
        response = await llm.ainvoke(messages)
        result = parse_json_response(response.content)

    except Exception as exc:
        print(f"Progress Tracker Error: {exc}")
        result = {
            "error": "Progress parsing error",
            "details": str(exc),
        }

    state["final_response"] = {
        "agent": "ProgressTracker",
        "output": result,
    }

    return state


# ---- Parent Reporter Node ----
async def parent_reporter_node(state: TutorState) -> TutorState:
    profile = state.get("student_profile", {})
    task = state.get("task_input", "")

    llm = get_reasoning_llm()
    prompt = build_agent_prompt_with_student(
        PARENT_REPORTER_PROMPT,
        profile,
    )

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(
            content=(
                "Generate a parent report based on this request and "
                f"return JSON: '{task}'"
            )
        ),
    ]

    try:
        response = await llm.ainvoke(messages)
        result = parse_json_response(response.content)

    except Exception as exc:
        print(f"Parent Reporter Error: {exc}")
        result = {
            "error": "Parent report parsing error",
            "details": str(exc),
        }

    state["final_response"] = {
        "agent": "ParentReporter",
        "output": result,
    }

    return state


# ---- Routing Logic ----
def route_task(state: TutorState) -> str:
    classification = state.get("classification") or {}
    next_agent = classification.get(
        "next_agent",
        "doubt_resolver",
    )

    valid_agents = {
        "lesson_personalizer",
        "quiz_generator",
        "doubt_resolver",
        "progress_tracker",
        "parent_reporter",
    }

    if next_agent not in valid_agents:
        return "doubt_resolver"

    return next_agent


# ---- Graph Construction ----
def build_tutor_graph():
    workflow = StateGraph(TutorState)

    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("lesson_personalizer", lesson_personalizer_node)
    workflow.add_node("quiz_generator", quiz_generator_node)
    workflow.add_node("doubt_resolver", doubt_resolver_node)
    workflow.add_node("progress_tracker", progress_tracker_node)
    workflow.add_node("parent_reporter", parent_reporter_node)

    workflow.set_entry_point("orchestrator")

    workflow.add_conditional_edges(
        "orchestrator",
        route_task,
        {
            "lesson_personalizer": "lesson_personalizer",
            "quiz_generator": "quiz_generator",
            "doubt_resolver": "doubt_resolver",
            "progress_tracker": "progress_tracker",
            "parent_reporter": "parent_reporter",
        },
    )

    workflow.add_edge("lesson_personalizer", END)
    workflow.add_edge("quiz_generator", END)
    workflow.add_edge("doubt_resolver", END)
    workflow.add_edge("progress_tracker", END)
    workflow.add_edge("parent_reporter", END)

    return workflow.compile()


tutor_graph = build_tutor_graph()
