# LearnPilot AI

An AI-powered tutoring application combining multi-agent orchestration, retrieval-augmented generation (RAG), and student progress tracking.

## Features

- FastAPI backend for tutor requests
- LangGraph-based tutoring workflow
- CrewAI specialist agents
- Google Gemini model integration
- Model Context Protocol (MCP) server
- SQLite persistence for student and mastery data
- Lightweight HTML, CSS, and JavaScript frontend

## Technology Stack

Python, FastAPI, LangGraph, CrewAI, Google Gemini, MCP, SQLite, ChromaDB, HTML, CSS, and JavaScript.

## Project Structure

```text
.
├── main.py
├── agent_graph.py
├── crew_agents.py
├── education_tutor_prompts.py
├── llm_config.py
├── mcp_server.py
├── database.py
├── rag_pipeline.py
├── requirements.txt
├── .env.example
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js
```

## Prerequisites

- Python compatible with the dependencies in `requirements.txt`
- A Google Gemini API key

## Setup

### 1. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Add your API key to `.env`:

```text
GOOGLE_API_KEY=your_actual_google_api_key
```

Never commit `.env` or expose your API key publicly.

### 4. Start the backend

From the project root:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API documentation: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

### 5. Start the frontend

Open another PowerShell terminal:

```powershell
cd frontend
python -m http.server 5500
```

Open http://127.0.0.1:5500/ in your browser.

## MCP Integration

The project includes an MCP server in `mcp_server.py` using standard input/output transport. Configure the server in your MCP-compatible client using the absolute paths to the Python interpreter and server script.

## Configuration and Limitations

- AI-generated responses require a valid Gemini API key and available API quota.
- SQLite and ChromaDB may create local runtime data.
- Keep credentials, local databases, and generated files out of version control.
- Verify the complete AI workflow after configuring the model provider.

## License

Before publishing, confirm the applicable license and attribution requirements for the source code and add the appropriate license information.
