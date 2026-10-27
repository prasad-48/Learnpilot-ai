
import os
from dotenv import load_dotenv
from crewai import LLM
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def _get_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        raise ValueError(
            "GOOGLE_API_KEY is missing. Add your actual Gemini API key to .env."
        )
    return api_key


# CrewAI specialist agents
def get_gemini_llm(temperature=0.2):
    return LLM(
        model="gemini/gemini-3.6-flash",
        api_key=_get_api_key(),
        temperature=temperature,
    )


# LangChain model for LangGraph nodes using ainvoke()
def get_orchestrator_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=_get_api_key(),
    )


def get_creative_llm():
    return get_gemini_llm(temperature=0.7)


def get_reasoning_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=_get_api_key(),
    )
