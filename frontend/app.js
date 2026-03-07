const chatForm = document.getElementById('chat-form');
const taskInput = document.getElementById('task-input');
const chatContainer = document.getElementById('chat-container');
const sendBtn = document.getElementById('send-btn');

// Student Profile inputs
const sId = document.getElementById('student-id');
const sName = document.getElementById('student-name');
const grade = document.getElementById('grade-level');
const age = document.getElementById('age');
const styleSelect = document.getElementById('learning-style');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const task = taskInput.value.trim();
    if(!task) return;

    // 1. Add User Message
    addMessage(task, 'user');
    taskInput.value = '';

    // 2. Add Loading Message
    const loadId = 'msg-' + Date.now();
    addMessage("EduPilot Orchestrator is generating<span class='loading-dots'></span>", 'system', loadId, 'EduPilot Orchestrator');
    
    // Disable input
    taskInput.disabled = true;
    sendBtn.disabled = true;

    // 3. Make API Call to FastAPI
    try {
        const payload = {
            task: task,
            student: {
                student_id: sId.value,
                name: sName.value,
                grade_level: grade.value,
                age: parseInt(age.value),
                learning_style: styleSelect.value,
                language: "English"
            }
        };

        const res = await fetch('http://127.0.0.1:8000/api/v1/tutor/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        
        // Remove loading
        const loader = document.getElementById(loadId);
        if(loader) loader.remove();

        if (data.status === 'success') {
            // Format response as JSON string for display nicely
            const responseText = typeof data.response === 'object' 
                ? JSON.stringify(data.response, null, 2) 
                : data.response;
            
            // Reformat agent name for display
            let displayAgent = data.agent_invoked.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
            
            addMessage(responseText, 'system', null, displayAgent, true);
        } else {
            addMessage("An error occurred processing the task.", 'system');
        }

    } catch (err) {
        document.getElementById(loadId)?.remove();
        addMessage(`Connection Error: Make sure main.py is running! (${err.message})`, 'system', null, 'System Error');
    } finally {
        taskInput.disabled = false;
        sendBtn.disabled = false;
        taskInput.focus();
    }
});

function addMessage(text, type, id = null, agent = null, isJson = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}-message fade-in`;
    if(id) msgDiv.id = id;

    const avatar = type === 'system' ? '🤖' : '👤';
    const avatarClass = type === 'system' ? 'avatar-system' : 'avatar-user';

    let contentHtml = '';
    
    // Add agent pill for system answers
    if (type === 'system' && agent) {
        contentHtml += `<span class="agent-tag">${agent}</span>`;
    }

    if (isJson) {
        contentHtml += `<pre>${escapeHtml(text)}</pre>`;
    } else {
        contentHtml += `<p>${text}</p>`;
    }

    msgDiv.innerHTML = `
        <div class="${avatarClass}">${avatar}</div>
        <div class="bubble">
            ${contentHtml}
        </div>
    `;

    chatContainer.appendChild(msgDiv);
    // Smooth scroll
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
}

function escapeHtml(unsafe) {
    if(!unsafe) return "";
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}
