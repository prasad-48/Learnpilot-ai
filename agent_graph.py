import json
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from llm_config import get_orchestrator_llm, get_reasoning_llm
from education_tutor_prompts import (
    ORCHESTRATOR_PROMPT,
    PROGRESS_TRACKER_PROMPT,
    PARENT_REPORTER_PROMPT,
    build_agent_prompt_with_student
)
from crew_agents import run_lesson_personalizer, run_quiz_generator, run_doubt_resolver
from langchain_core.messages import SystemMessage, HumanMessage
import rag_pipeline

# ---- State Definition ----
class TutorState(Dict[str, Any]):
    task_input: str
    student_profile: Dict[str, Any]
    classification: Optional[Dict[str, Any]]
    final_response: Optional[Dict[str, Any]]

# ---- Nodes ----
def orchestrator_node(state: TutorState) -> TutorState:
    """
    Classifies the task and routes to the appropriate specialist agent.
    """
    task = state.get("task_input", "")
    profile = state.get("student_profile", {})
    
    llm = get_orchestrator_llm()
    messages = [
        SystemMessage(content=ORCHESTRATOR_PROMPT),
        HumanMessage(content=f"Classify this incoming task and return exactly the required JSON format: '{task}'")
    ]
    
    try:
        response = llm.invoke(messages)
        clean_json = response.content.replace('```json', '').replace('```', '').strip()
        classification = json.loads(clean_json)
        
        # Determine the next agent based on task type. Map to valid graph nodes.
        task_type = classification.get("task_type", "doubt")
        next_agent = "doubt_resolver" # fallback
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
    except Exception as e:
        print(f"Orchestrator Parsing Error: {e}")
        state["classification"] = {"next_agent": "doubt_resolver"} # Fallback

    return state

def lesson_personalizer_node(state: TutorState) -> TutorState:
    profile = state.get("student_profile", {})
    task = state.get("task_input", "")
    result = run_lesson_personalizer(profile, task)
    state["final_response"] = {
        "agent": "LessonPersonalizer",
        "output": result
    }
    return state

def quiz_generator_node(state: TutorState) -> TutorState:
    profile = state.get("student_profile", {})
    task = state.get("task_input", "")
    result = run_quiz_generator(profile, task)
    state["final_response"] = {
        "agent": "QuizGenerator",
        "output": result
    }
    return state

def doubt_resolver_node(state: TutorState) -> TutorState:
    profile = state.get("student_profile", {})
    task = state.get("task_input", "")
    
    # Retrieve dynamic, real curriculum context from our Vector Database
    retrieved_context = rag_pipeline.retrieve_context(task, n_results=2)
    
    result = run_doubt_resolver(profile, task, retrieved_context)
    state["final_response"] = {
        "agent": "DoubtResolver",
        "output": result,
        "rag_context_used": retrieved_context
    }
    return state

def progress_tracker_node(state: TutorState) -> TutorState:
    profile = state.get("student_profile", {})
    task = state.get("task_input", "")
    llm = get_reasoning_llm()
    prompt = build_agent_prompt_with_student(PROGRESS_TRACKER_PROMPT, profile)
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Process this progress request and return the structured JSON: '{task}'")
    ]
    try:
        response = llm.invoke(messages)
        clean_json = response.content.replace('```json', '').replace('```', '').strip()
        result = json.loads(clean_json)
    except Exception as e:
        result = {"error": "Progress parsing error", "details": str(e)}

    state["final_response"] = {
        "agent": "ProgressTracker",
        "output": result
    }
    return state

def parent_reporter_node(state: TutorState) -> TutorState:
    profile = state.get("student_profile", {})
    task = state.get("task_input", "")
    llm = get_reasoning_llm()
    prompt = build_agent_prompt_with_student(PARENT_REPORTER_PROMPT, profile)
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Generate a parent report based on this request and return JSON: '{task}'")
    ]
    try:
        response = llm.invoke(messages)
        clean_json = response.content.replace('```json', '').replace('```', '').strip()
        result = json.loads(clean_json)
    except Exception as e:
        result = {"error": "Parent report parsing error", "details": str(e)}

    state["final_response"] = {
        "agent": "ParentReporter",
        "output": result
    }
    return state

# ---- Routing Logic ----
def route_task(state: TutorState) -> str:
    classification = state.get("classification", {})
    return classification.get("next_agent", "doubt_resolver")

# ---- Graph Construction ----
def build_tutor_graph():
    workflow = StateGraph(TutorState)
    
    # Add nodes
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("lesson_personalizer", lesson_personalizer_node)
    workflow.add_node("quiz_generator", quiz_generator_node)
    workflow.add_node("doubt_resolver", doubt_resolver_node)
    workflow.add_node("progress_tracker", progress_tracker_node)
    workflow.add_node("parent_reporter", parent_reporter_node)
    
    # Set entry point
    workflow.set_entry_point("orchestrator")
    
    # Conditional Edges from orchestrator to defined agents
    workflow.add_conditional_edges(
        "orchestrator",
        route_task,
        {
            "lesson_personalizer": "lesson_personalizer",
            "quiz_generator": "quiz_generator",
            "doubt_resolver": "doubt_resolver",
            "progress_tracker": "progress_tracker",
            "parent_reporter": "parent_reporter"
        }
    )
    
    # All specialists return to END
    workflow.add_edge("lesson_personalizer", END)
    workflow.add_edge("quiz_generator", END)
    workflow.add_edge("doubt_resolver", END)
    workflow.add_edge("progress_tracker", END)
    workflow.add_edge("parent_reporter", END)
    
    return workflow.compile()

tutor_graph = build_tutor_graph()
