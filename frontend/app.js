
const chatForm = document.getElementById('chat-form');
const taskInput = document.getElementById('task-input');
const chatContainer = document.getElementById('chat-container');
const sendBtn = document.getElementById('send-btn');

// Student profile inputs
const sId = document.getElementById('student-id');
const sName = document.getElementById('student-name');
const grade = document.getElementById('grade-level');
const age = document.getElementById('age');
const styleSelect = document.getElementById('learning-style');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const task = taskInput.value.trim();

    if (!task) {
        addMessage('Please enter a task before sending.', 'system');
        return;
    }

    addMessage(task, 'user');
    taskInput.value = '';

    const loadId = 'msg-' + Date.now();
    addMessage(
        "LearnPilot AI Orchestrator is generating<span class='loading-dots'></span>",
        'system',
        loadId,
        'LearnPilot AI Orchestrator'
    );

    taskInput.disabled = true;
    sendBtn.disabled = true;

    try {
        const payload = {
            task,
            student: {
                student_id: sId.value.trim(),
                name: sName.value.trim(),
                grade_level: grade.value,
                age: Number.parseInt(age.value, 10),
                learning_style: styleSelect.value,
                language: 'English'
            }
        };

        const res = await fetch(
            'https://learnpilot-ai-iig1.onrender.com/api/v1/tutor/solve',
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }
        );

        let data;

        try {
            data = await res.json();
        } catch {
            throw new Error(`Server returned HTTP ${res.status} with an unreadable response.`);
        }

        const loader = document.getElementById(loadId);
        if (loader) loader.remove();

        // Handle HTTP errors and backend error responses.
        if (!res.ok || data.status === 'error' || data.error_type) {
            let message =
                data.detail?.message ||
                data.detail ||
                data.message ||
                'An unexpected error occurred.';

            if (data.error_type === 'AI_QUOTA_EXCEEDED') {
                message =
                    'The AI service quota is exhausted. Please retry after your quota resets or configure a billing-enabled API key.';
            } else if (res.status === 429) {
                message =
                    typeof message === 'string'
                        ? message
                        : 'The AI service is rate-limited. Please try again later.';
            }

            if (typeof message !== 'string') {
                message = JSON.stringify(message, null, 2);
            }

            addMessage(
                `Request failed (HTTP ${res.status}): ${message}`,
                'system',
                null,
                'System Error'
            );
            return;
        }

        if (data.status === 'success') {
            const responseText =
                typeof data.response === 'object'
                    ? JSON.stringify(data.response, null, 2)
                    : String(data.response ?? '');

            const displayAgent = String(data.agent_invoked || 'LearnPilot AI')
                .replace(/_/g, ' ')
                .replace(/\b\w/g, c => c.toUpperCase());

            addMessage(responseText, 'system', null, displayAgent, true);
        } else {
            const message =
                data.detail?.message ||
                data.detail ||
                data.message ||
                'The server returned an unexpected response.';

            addMessage(
                typeof message === 'string' ? message : JSON.stringify(message),
                'system',
                null,
                'System Error'
            );
        }
    } catch (err) {
        document.getElementById(loadId)?.remove();

        addMessage(
            `Connection error: ${err.message}. Check that the backend is running at http://127.0.0.1:8000.`,
            'system',
            null,
            'System Error'
        );
    } finally {
        taskInput.disabled = false;
        sendBtn.disabled = false;
        taskInput.focus();
    }
});

function addMessage(text, type, id = null, agent = null, isJson = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}-message fade-in`;

    if (id) msgDiv.id = id;

    const avatar = type === 'system' ? 'ðŸ¤–' : 'ðŸ‘¤';
    const avatarClass = type === 'system' ? 'avatar-system' : 'avatar-user';

    let contentHtml = '';

    if (type === 'system' && agent) {
        contentHtml += `<span class="agent-tag">${escapeHtml(agent)}</span>`;
    }

    if (isJson) {
        contentHtml += `<pre>${escapeHtml(String(text))}</pre>`;
    } else {
        contentHtml += `<p>${escapeHtml(String(text))}</p>`;
    }

    msgDiv.innerHTML = `
        <div class="${avatarClass}">${avatar}</div>
        <div class="bubble">
            ${contentHtml}
        </div>
    `;

    chatContainer.appendChild(msgDiv);

    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
}

function escapeHtml(unsafe) {
    return String(unsafe ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
