import json
from crewai import Agent, Task, Crew, Process
from llm_config import get_creative_llm, get_reasoning_llm
from education_tutor_prompts import (
    LESSON_PERSONALIZER_PROMPT,
    QUIZ_GENERATOR_PROMPT,
    DOUBT_RESOLVER_PROMPT,
    build_agent_prompt_with_student
)

def run_lesson_personalizer(student_profile: dict, task_input: str) -> dict:
    llm = get_creative_llm()
    prompt = build_agent_prompt_with_student(LESSON_PERSONALIZER_PROMPT, student_profile)

    agent = Agent(
        role="Lesson Personalizer",
        goal="Design and deliver personalized lesson experiences tailored to the student's unique learning profile.",
        backstory=prompt,
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task = Task(
        description=f"Create a personalized lesson for the following request: '{task_input}'. Ensure you follow the adaptive lesson design protocol and return the exact JSON structure defined in your instructions without markdown wrapping or extra text.",
        expected_output="A JSON object matching the exact format specified in the OUTPUT FORMAT section.",
        agent=agent
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    result_str = crew.kickoff()
    try:
        # Strip potential markdown formatting that LLMs sometimes add (e.g. ```json )
        clean_json = str(result_str).replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": "Failed to parse JSON", "raw_output": str(result_str), "details": str(e)}


def run_quiz_generator(student_profile: dict, task_input: str) -> dict:
    llm = get_reasoning_llm()
    prompt = build_agent_prompt_with_student(QUIZ_GENERATOR_PROMPT, student_profile)

    agent = Agent(
        role="Quiz Generator",
        goal="Create topic-based quizzes, practice sets, and formal assessments that measure mastery and identify misconceptions.",
        backstory=prompt,
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task = Task(
        description=f"Generate a quiz based on the request: '{task_input}'. Ensure you strictly follow the Bloom's Taxonomy standards and return the exact JSON structure defined in your instructions without markdown block wrappers.",
        expected_output="A valid JSON object.",
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    
    result_str = crew.kickoff()
    try:
        clean_json = str(result_str).replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": "Failed to parse JSON", "raw_output": str(result_str), "details": str(e)}


def run_doubt_resolver(student_profile: dict, task_input: str, retrieved_context: list = None) -> dict:
    llm = get_creative_llm()
    prompt = build_agent_prompt_with_student(DOUBT_RESOLVER_PROMPT, student_profile)
    
    context_str = "No specific RAG context provided for this query."
    if retrieved_context:
        context_str = "\n".join([str(c) for c in retrieved_context])

    agent = Agent(
        role="Doubt Resolver",
        goal="Resolve student questions, explain concepts, and correct misconceptions using providing context.",
        backstory=prompt,
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task = Task(
        description=f"Resolve the following student doubt: '{task_input}'. \n\nUtilize this retrieved curriculum context: \n{context_str}\n\nReturn EXACTLY the specified JSON output format with no markdown blocks.",
        expected_output="A valid JSON object.",
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    
    result_str = crew.kickoff()
    try:
        clean_json = str(result_str).replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": "Failed to parse JSON", "raw_output": str(result_str), "details": str(e)}
