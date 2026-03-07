import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Load environment variables from .env if present
load_dotenv()

def get_orchestrator_llm():
    """
    Returns the LLM for the Orchestrator. 
    Prompt recommends claude-3-5-sonnet or gpt-4o.
    """
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o", temperature=0.2)
    elif os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(model_name="claude-3-5-sonnet-20240620", temperature=0.2)
    else:
        # Fallback for local testing without keys (Will fail if invoked)
        return ChatOpenAI(model="gpt-4o", openai_api_key="mock_key")

def get_creative_llm():
    """
    For highly generative tasks like Lesson Personalization.
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(model_name="claude-3-5-sonnet-20240620", temperature=0.7)
    elif os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o", temperature=0.7)
    return ChatOpenAI(model="gpt-4o", openai_api_key="mock_key")

def get_reasoning_llm():
    """
    For analytic / rules-based tasks like Quiz Generation and Evaluating Progress.
    """
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o", temperature=0.4)
    return ChatOpenAI(model="gpt-4o", openai_api_key="mock_key")
