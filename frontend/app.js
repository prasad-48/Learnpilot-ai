
const chatForm = document.getElementById('chat-form');
const taskInput = document.getElementById('task-input');
const chatContainer = document.getElementById('chat-container');
const sendBtn = document.getElementById('send-btn');

const API_URL =
    'https://learnpilot-ai-iig1.onrender.com/api/v1/tutor/solve';

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

    const loadId = `typing-${Date.now()}`;
    addTypingIndicator(loadId);

    taskInput.disabled = true;
    sendBtn.disabled = true;

    try {
        const parsedAge = Number.parseInt(age.value, 10);

        const payload = {
            task,
            student: {
                student_id: sId.value.trim(),
                name: sName.value.trim(),
                grade_level: grade.value.trim(),
                age: Number.isNaN(parsedAge) ? null : parsedAge,
                learning_style: styleSelect.value,
                language: 'English'
            },
            context: {}
        };

        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        let data;

        try {
            data = await res.json();
        } catch {
            throw new Error(
                `The server returned an unreadable response (HTTP ${res.status}).`
            );
        }

        if (!res.ok || data.status === 'error' || data.error_type) {
            let message =
                data.detail?.message ||
                data.detail ||
                data.message ||
                'An unexpected error occurred.';

            if (data.error_type === 'AI_QUOTA_EXCEEDED') {
                message =
                    'The AI service quota is exhausted. Please try again later.';
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
            const response = data.response;

            const responseText =
                typeof response === 'string'
                    ? response
                    : JSON.stringify(response ?? data, null, 2);

            const displayAgent = String(
                data.agent_invoked || 'LearnPilot AI'
            )
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
                typeof message === 'string'
                    ? message
                    : JSON.stringify(message, null, 2),
                'system',
                null,
                'System Error'
            );
        }
    } catch (err) {
        addMessage(
            `Connection error: ${err.message}. Please check your internet connection and try again.`,
            'system',
            null,
            'Connection Error'
        );
    } finally {
        document.getElementById(loadId)?.remove();

        taskInput.disabled = false;
        sendBtn.disabled = false;
        taskInput.focus();
    }
});

function addTypingIndicator(id) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message system-message fade-in typing-message';
    msgDiv.id = id;

    msgDiv.innerHTML = `
        <div class="avatar-system" aria-hidden="true">&#129302;</div>
        <div class="bubble typing-bubble" role="status" aria-live="polite">
            <span class="typing-label">LearnPilot AI is thinking</span>
            <span class="typing-dots" aria-hidden="true">
                <span></span><span></span><span></span>
            </span>
        </div>
    `;

    chatContainer.appendChild(msgDiv);
    scrollToLatest();
}

function addMessage(text, type, id = null, agent = null, isJson = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}-message fade-in`;

    if (id) msgDiv.id = id;

    // Numeric HTML entities avoid corrupted emoji characters in source files.
    const avatar = type === 'system' ? '&#129302;' : '&#128100;';
    const avatarClass =
        type === 'system' ? 'avatar-system' : 'avatar-user';

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
        <div class="${avatarClass}" aria-hidden="true">${avatar}</div>
        <div class="bubble">${contentHtml}</div>
    `;

    chatContainer.appendChild(msgDiv);
    scrollToLatest();
}

function scrollToLatest() {
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
