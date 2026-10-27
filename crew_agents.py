
import json
from crewai import Agent, Task, Crew, Process

from llm_config import get_creative_llm, get_gemini_llm
from education_tutor_prompts import (
    LESSON_PERSONALIZER_PROMPT,
    QUIZ_GENERATOR_PROMPT,
    DOUBT_RESOLVER_PROMPT,
    build_agent_prompt_with_student,
)


def parse_agent_result(result) -> dict:
    """Parse the agent's output into a JSON dictionary."""
    result_str = str(result)

    try:
        clean_json = (
            result_str
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )
        return json.loads(clean_json)
    except (json.JSONDecodeError, TypeError) as exc:
        return {
            "error": "Failed to parse JSON",
            "raw_output": result_str,
            "details": str(exc),
        }


async def run_lesson_personalizer(
    student_profile: dict,
    task_input: str,
) -> dict:
    llm = get_creative_llm()
    prompt = build_agent_prompt_with_student(
        LESSON_PERSONALIZER_PROMPT, student_profile
    )

    agent = Agent(
        role="Lesson Personalizer",
        goal=(
            "Design and deliver personalized lesson experiences tailored "
            "to the student's unique learning profile."
        ),
        backstory=prompt,
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    task = Task(
        description=(
            f"Create a personalized lesson for this request: '{task_input}'. "
            "Follow the adaptive lesson design protocol and return the exact "
            "JSON structure defined in your instructions without markdown."
        ),
        expected_output="A JSON object matching the specified output format.",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = await crew.kickoff_async()
    return parse_agent_result(result)


async def run_quiz_generator(
    student_profile: dict,
    task_input: str,
) -> dict:
    llm = get_gemini_llm()
    prompt = build_agent_prompt_with_student(
        QUIZ_GENERATOR_PROMPT, student_profile
    )

    agent = Agent(
        role="Quiz Generator",
        goal=(
            "Create topic-based quizzes and assessments that measure mastery "
            "and identify misconceptions."
        ),
        backstory=prompt,
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    task = Task(
        description=(
            f"Generate a quiz for this request: '{task_input}'. "
            "Follow Bloom's Taxonomy standards and return the exact JSON "
            "structure without markdown wrappers."
        ),
        expected_output="A valid JSON object matching the specified format.",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
    )

    result = await crew.kickoff_async()
    return parse_agent_result(result)


async def run_doubt_resolver(
    student_profile: dict,
    task_input: str,
    retrieved_context: list | None = None,
) -> dict:
    llm = get_creative_llm()
    prompt = build_agent_prompt_with_student(
        DOUBT_RESOLVER_PROMPT, student_profile
    )

    context_str = "No specific RAG context provided for this query."
    if retrieved_context:
        context_str = "\n".join(str(item) for item in retrieved_context)

    agent = Agent(
        role="Doubt Resolver",
        goal=(
            "Resolve student questions, explain concepts, and correct "
            "misconceptions using the provided context."
        ),
        backstory=prompt,
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    task = Task(
        description=(
            f"Resolve this student doubt: '{task_input}'.\n\n"
            f"Retrieved curriculum context:\n{context_str}\n\n"
            "Return the exact JSON output format without markdown."
        ),
        expected_output="A valid JSON object matching the specified format.",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
    )

    result = await crew.kickoff_async()
    return parse_agent_result(result)
