LearnPilot AI --- Setup Guide
This guide explains how to install and run LearnPilot AI on a new
Windows computer. The commands use PowerShell. The repository is:

GitHub: https://github.com/prasad-48/Learnpilot-ai
1. What you need
- Git
- Python installed and available as python in PowerShell
- A Google Gemini API key
- A terminal and a modern web browser
Check that Python and Git are available:
python --version
git --version
If python is not recognized, install Python and enable the option that
adds Python to PATH, then reopen PowerShell.
2. Download the project
Choose a folder where you want to keep the project, then run:
cd $HOME\Desktop
git clone https://github.com/prasad-48/Learnpilot-ai.git
cd Learnpilot-ai
If you already downloaded the repository, open PowerShell in the project
root---the folder containing main.py and requirements.txt.
3. Create and activate a Python virtual environment
From the project root:
python -m venv venv
.\venv\Scripts\Activate.ps1
When activation succeeds, PowerShell usually shows (venv) at the start
of the prompt.

If PowerShell blocks activation, you can avoid changing the execution
policy by running the environment's Python executable directly in the
later commands, for example:
.\venv\Scripts\python.exe -m pip install -r requirements.txt
4. Install Python dependencies
With the virtual environment activated:
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Wait for the installation to finish. If installation fails, read the
first actual error in the output and check that your Python version is
compatible with the packages in requirements.txt.
5. Configure the Gemini API key
Create a local .env file from the example:
Copy-Item .env.example .env
notepad .env
Set the value to your own valid Gemini API key:
GOOGLE_API_KEY=your_actual_google_api_key
Replace the placeholder with your key. Do not include extra quotes
unless the project configuration explicitly requires them. Save the
file.

Security: Never share your real API key, upload .env, or paste the
key into an issue or screenshot. .env is intended to remain local and
is ignored by Git.
6. Start the backend
Open PowerShell in the project root, activate the environment if needed,
and run:
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
Keep this terminal open.

Check these URLs in your browser:
- API health check: http://127.0.0.1:8000/health
- Interactive API documentation: http://127.0.0.1:8000/docs
If the health endpoint responds successfully and the docs page opens,
the backend is running.
7. Start the frontend
Open a second PowerShell terminal. Change to the project folder and
run:
cd "$HOME\Desktop\Learnpilot-ai\frontend"
python -m http.server 5500
If you cloned the project into a different folder, adjust the cd path
to match your actual location.

Keep this terminal open and visit:

http://127.0.0.1:5500/

The frontend is static HTML, CSS, and JavaScript, so it is served
separately from the FastAPI backend.
8. Verify the project
1. Confirm the backend health check at http://127.0.0.1:8000/health.
2. Open the API documentation at http://127.0.0.1:8000/docs.
3. Open the frontend at http://127.0.0.1:5500/.
4. Try a simple tutoring request.
5. If the frontend loads but the AI request fails, check the backend
   terminal and the Gemini API key/quota configuration.
AI responses depend on a valid API key and available Gemini quota. A
running web server does not guarantee that the external AI service is
currently available.
9. MCP server
The project includes an MCP server in mcp_server.py using standard
input/output transport. The helper script check_mcp.py can be used to
check that the MCP server initializes and registers the invoke_tutor
tool.

From the project root, with dependencies installed:
.\venv\Scripts\python.exe check_mcp.py
MCP clients generally need the absolute path to the Python interpreter
in the virtual environment and the absolute path to mcp_server.py.
Follow the configuration format required by your specific MCP client.

test_mcp.py performs a sample tutor invocation. It may call the live
Gemini API and can fail if the API key is invalid or quota is exhausted.
10. Local data and troubleshooting
- SQLite and ChromaDB may create local runtime data when the
  application runs.
- Do not commit .env, virtual-environment files, API keys, or local
  runtime databases.
- For common setup errors and fixes, read
  SETUP_ISSUES_AND_FIXES.md.
Useful commands
Run from the project root:
# Check Python dependencies
.\venv\Scripts\python.exe -m pip check

# Check Python files for syntax/bytecode compilation errors
.\venv\Scripts\python.exe -m compileall .

# Check MCP initialization and tool registration
.\venv\Scripts\python.exe check_mcp.py
Stop a running server with Ctrl+C in the terminal where it is running.
Notes
- These instructions describe a local development setup, not a
  production deployment.
- Keep the backend and frontend terminals open while using the
  application.
- API keys and Gemini quota are controlled by Google and are separate
  from this repository.
- Review the repository's license and attribution requirements before
  redistributing the code.