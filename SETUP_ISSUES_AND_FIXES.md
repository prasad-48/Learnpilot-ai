LearnPilot AI --- Setup Issues and Fixes
This document records issues encountered during setup/testing and
provides practical checks for people setting up the project on another
computer.
Issues confirmed during our setup
1. The Gemini API key was incorrect
Symptom

The app could start, but the tutor request did not complete
successfully. Testing the model with a simple prompt helped isolate the
problem.

Cause

The value configured for GOOGLE_API_KEY was incorrect.

Fix
1. Open the .env file in the project root.
2. Replace the key with a valid Gemini API key.
3. Save the file.
4. Stop and restart the backend so it reloads its environment.
5. Test the model again with a simple prompt before trying a full
   tutoring request.
To check whether the project configuration sees a key without printing
the secret, run from the project root:
.\venv\Scripts\python.exe -c "from llm_config import GOOGLE_API_KEY; print('API key loaded:', bool(GOOGLE_API_KEY))"
If this import/variable name does not match the current version of
llm_config.py, inspect that file and use the project's actual
configuration variable. Never print or share the key itself.

Lesson: API key loaded: True only confirms that a non-empty value
was loaded. It does not prove that the key is valid or has quota.
2. Gemini returned HTTP 429 because the free-tier quota was exhausted
Symptom

A live tutor request failed with an HTTP 429 response.

Cause

The Gemini free-tier daily quota had been exhausted during testing. This
is a model-provider quota/rate-limit response, not by itself proof of a
bug in the local application.

Fix / next steps
1. Check the Google AI Studio / Gemini API usage and quota for the key.
2. Confirm that the selected model is available to the account and
   project.
3. Wait for the quota to reset, or use an eligible plan/project with
   sufficient quota.
4. Retry a small request before testing a longer tutoring workflow.
Do not keep retrying rapidly; that will not restore a daily quota. The
application can be installed correctly while live AI responses remain
unavailable due to provider quota.
Common setup problems and how to diagnose them
The following are preventive troubleshooting notes; they are not all
confirmed as errors that occurred during our setup.
3. The .env file is missing or the key is not loaded
Symptoms
- The app reports a missing API key.
- The model client cannot authenticate.
- A valid key is present in a different file or folder but the
  application does not see it.
Checks
- Make sure .env is in the project root beside main.py, not inside
  frontend/.
- Make sure the variable name is exactly GOOGLE_API_KEY.
- Confirm that .env was created from .env.example and the
  placeholder was replaced.
- Restart the backend after changing environment values.
- Do not commit .env; use .env.example for a safe placeholder
  template.
4. python or pip is not recognized
Cause

Python may not be installed, may not be on PATH, or the terminal may
have been opened before Python was installed.

Fix
python --version
py --version
Install Python if neither command works, enable the PATH option during
installation, and reopen PowerShell. Once the virtual environment
exists, prefer .\venv\Scripts\python.exe -m pip ... to ensure packages
install into the correct environment.
5. PowerShell refuses to activate the virtual environment
Symptom

Running .\venv\Scripts\Activate.ps1 is blocked by an execution-policy
message.

Workaround

You do not have to activate the environment to use its interpreter:
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
This avoids changing the machine's PowerShell execution policy.
6. The frontend opens, but tutor requests fail
Checks
1. Confirm the backend is running in its own terminal.
2. Open http://127.0.0.1:8000/health.
3. Inspect the backend terminal immediately after submitting a request.
4. Check the browser developer console for network errors.
5. Verify the frontend's API URL in frontend/app.js matches the
   backend host and port (127.0.0.1:8000 in the default local setup).
6. Check the API key and Gemini quota.
A page loading successfully only confirms that the frontend server is
serving files; it does not verify the API or model provider.
7. Port 8000 or 5500 is already in use
Symptom

The backend or frontend server reports that it cannot bind to the
requested port.

Fix

Stop the other process using that port, or choose another free port. If
you change the backend port, update the frontend API URL to match it.
Keep the frontend and backend URLs consistent.
8. MCP server does not initialize or the tool is not discovered
Checks

Run the included diagnostic from the project root:
.\venv\Scripts\python.exe check_mcp.py
Confirm dependencies are installed and that the script reports the
invoke_tutor tool. When configuring an MCP client, use absolute paths
to the virtual-environment Python executable and mcp_server.py. MCP
clients must support the server's standard input/output transport.
9. The sample MCP tutor test fails
Run:
.\venv\Scripts\python.exe test_mcp.py
This test may invoke the live Gemini model. If it fails, check the API
key and quota first, then inspect the complete traceback. A quota
failure does not necessarily mean MCP initialization or tool
registration is broken. Be aware that a live test may write local
application data.
10. Dependency installation or import errors
Run these checks from the project root:
.\venv\Scripts\python.exe -m pip check
.\venv\Scripts\python.exe -m compileall .
- pip check reports incompatible or missing installed package
  requirements.
- compileall checks Python source files for syntax/bytecode
  compilation errors.
- Neither command proves that the external Gemini API is available or
  that every user workflow works.
If installation fails, capture the first meaningful error, Python
version, and package name. Avoid blindly upgrading individual libraries
because that can introduce dependency conflicts.
11. Local database/vector-store files appear
SQLite and ChromaDB may create local files as the app runs. These are
runtime data, not source files. Keep local databases, vector-store data,
virtual environments, and secrets out of Git. The repository's
.gitignore is intended to help, but always inspect git status before
committing.
Quick diagnostic checklist
- [ ] Python is installed and compatible with requirements.txt.
- [ ] Virtual environment exists and dependencies installed.
- [ ] .env exists in the project root.
- [ ] GOOGLE_API_KEY is set to a valid key and kept private.
- [ ] Backend starts and /health responds.
- [ ] Frontend is served from port 5500 and opens in the browser.
- [ ] Frontend API URL points to the running backend.
- [ ] Gemini quota is available for live tutoring requests.
- [ ] check_mcp.py initializes and discovers invoke_tutor.
- [ ] No .env, API key, virtual environment, or local database is
  staged for Git.
What our test results did and did not establish
During the project preparation, Python compilation and dependency checks
passed, the FastAPI health endpoint worked, frontend files were served
successfully, and MCP initialization/tool discovery passed. SQLite
integrity and read/write checks also passed during diagnostics.

A live tutor request later returned HTTP 429 because the Gemini
free-tier quota was exhausted. Therefore, a successful local setup
should still be followed by a fresh end-to-end tutoring test when the
configured Gemini account has available quota.