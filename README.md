<div align="center">
  
# 🚀 EduPilot: Next-Gen AI Tutor Ecosystem
**A Production-Ready, Multi-Agent Orchestration Engine built on the Model Context Protocol (MCP)**

*Delivering hyper-personalized, adaptive, and interactive learning experiences at scale.*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph-FF4F00.svg)](https://python.langchain.com/docs/langgraph/)
[![CrewAI](https://img.shields.io/badge/Agents-CrewAI-FF6347.svg)](https://www.crewai.com/)
[![FastMCP](https://img.shields.io/badge/SDK-FastMCP-000000.svg)](https://modelcontextprotocol.io/)

</div>

---

## 🌎 The Vision

Traditional education scales poorly. Static curricula fail to adapt, and single-prompt LLMs lack the memory, pedagogical structure, and safety required for true learning. 

**EduPilot** solves this by leveraging a **decentralized Multi-Agent architecture**. Instead of relying on a single omniscient LLM, we use **LangGraph** to act as a routing supervisor state-machine. It dynamically intercepts natural language intents and routes tasks to highly specialized, goal-oriented **CrewAI** expert agents. The result? A fully autonomous digital tutor that maintains permanent state, consults real textbooks via Vector RAG, and serves everything seamlessly over the newly minted **Model Context Protocol (MCP)**.

---

## ⚡ The Tech Stack

We don't do monolithic architectures here. This is a modular, event-driven orchestration stack:

- **Orchestration Layer**: `LangGraph` (Supervisor State Machine)
- **Agent Intelligence**: `CrewAI` & `LangChain` (Lesson Planner, Doubt Resolver, Quiz Generator)
- **Knowledge Retrieval & RAG**: `ChromaDB` (Local Embeddings for ultra-low latency contextual retrieval)
- **State & Memory Persistence**: `SQLite` (Native Offline Storage for longitudinal mastery mapping)
- **API & Extensibility**: `FastAPI` (REST endpoints) + `FastMCP` (Claude Desktop Integration)
- **Frontend App**: Zero-dependency Vanilla HTML/CSS/JS (Glassmorphism Dark Mode)

---

## 🧠 The Agent Force

| Microservice Agent | Primary Responsibility | Associated Capabilities |
| --- | --- | --- |
| 👑 **The Orchestrator** | **Traffic Controller:** Ingests the task limitlessly, classifies the semantic intent, fetches SQLite mastery memory, and routes to the correct Crew. | `Routing`, `State Augmentation`, `Guardrails` |
| 🧑‍🏫 **Lesson Personalizer** | **Dynamic Curriculum:** Composes 5E-Model tailored lesson plans dynamically adjusted for the student's *exact* learning style (Visual, Auditory, Kinesthetic) and age. | `Bloom's Taxonomy Scaling`, `Adaptive Difficulty` |
| 🛡️ **Doubt Resolver** | **RAG Explainer:** Triggers a Vector DB retrieval across curriculum textbooks to answer questions accurately without hallucinating non-school-board facts. | `ChromaDB`, `Pinecone`, `Misconception Bridging` |
| 📝 **Quiz Generator** | **Assessment:** Generates precise, misconception-targeted distractors for MCQs. | `Formative Assessment` |
| 📊 **Progress Tracker** | **Memory Core:** Parses session outputs and permanently updates student mastery levels (0-100) inside the persistent SQLite memory layer. | `Spaced Repetition Data`, `Database Hydration` |

---

## 📦 Quick Start Installation

Get up and running in your local dev environment in under 60 seconds.

**1. Clone & Set up the Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
```

**2. Hydrate Dependencies**
```bash
pip install -r requirements.txt
```

**3. Inject Environment Keys**
Copy `.env.example` to `.env` and configure your foundation model provider (Anthropic is recommended for reasoning, OpenAI for generation):
```env
ANTHROPIC_API_KEY="sk-ant-..."
OPENAI_API_KEY="sk-proj-..."
```

---

## 🎯 Running The Platform

EduPilot is designed to run anywhere. Choose your preferred interaction method:

### Method A: The Interactive Web App (Recommended)
Boot the REST backend:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Then simply double-click **`frontend/index.html`** on your local machine to launch our completely decoupled, zero-build-step, ultra-premium chat interface.

### Method B: Native MCP Integration (Claude Desktop)
Because EduPilot is an official **MCP Server**, you can pipe the agent orchestrator directly into Claude!

Simply modify your `claude_desktop_config.json` file:
```json
{
  "mcpServers": {
    "edu-pilot-agent": {
      "command": "C:/path/to/venv/Scripts/python.exe",
      "args": ["C:/path/to/mcp_server.py"]
    }
  }
}
```
*Note: Make sure to point to the absolute path of the `python.exe` inside your virtual environment so dependencies resolve properly!*

### Method C: The MCP Inspector
Want to hit the bare-metal MCP tools locally?
```bash
npx @modelcontextprotocol/inspector .\venv\Scripts\python.exe mcp_server.py
```

---

*Built with ❤️ for the future of AGI-driven education.*
