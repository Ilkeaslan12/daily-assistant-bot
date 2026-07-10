// Determine API base URL based on environment
const API_BASE_URL = window.location.hostname === "localhost" 
    ? "http://127.0.0.1:8000" 
    : "https://your-vercel-app-url.vercel.app"; // Update this after deployment

const sessionId = "session-" + Math.floor(Math.random() * 1000);
let isRecording = false;
let mediaRecorder;
let audioChunks = [];

async function sendMessage() {
    const input = document.getElementById("user-input");
    const chatContainer = document.getElementById("chat-container");
    const text = input.value.trim();
    
    if (!text) return;

    chatContainer.classList.remove("empty-state");
    addMessageRow(text, "user");
    input.value = "";

    const loadingId = addMessageRow("Thinking...", "ai");

    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, message: text, user_name: "User" })
        });
        
        const data = await response.json();
        document.getElementById(loadingId).remove();
        
        if (data.status === "success") {
            addMessageRow(data.reply, "ai");
        } else {
            addMessageRow("Error: " + data.reply, "ai");
        }
    } catch (e) {
        document.getElementById(loadingId).remove();
        addMessageRow("Connection error. Please ensure the server is running.", "ai");
    }
}

function addMessageRow(text, sender) {
    const chatContainer = document.getElementById("chat-container");
    const rowDiv = document.createElement("div");
    rowDiv.className = "message-row";
    rowDiv.id = "msg-" + Date.now();

    const avatarDiv = document.createElement("div");
    avatarDiv.className = sender === "ai" ? "avatar ai-avatar" : "avatar user-avatar";
    avatarDiv.innerText = sender === "ai" ? "AI" : "ME"; 

    const textDiv = document.createElement("div");
    textDiv.className = "message-content";
    textDiv.innerText = text;

    rowDiv.appendChild(avatarDiv);
    rowDiv.appendChild(textDiv);
    chatContainer.appendChild(rowDiv);
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    return rowDiv.id;
}

async function toggleRecording() {
    const micBtn = document.getElementById("mic-btn");
    const chatContainer = document.getElementById("chat-container");
    
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => audioChunks.push(event.data);

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/ogg' });
                
                chatContainer.classList.remove("empty-state");
                const loadingId = addMessageRow("Processing audio...", "ai");
                
                const formData = new FormData();
                formData.append("session_id", sessionId);
                formData.append("voice_file", audioBlob, "voice.ogg");

                try {
                    const response = await fetch(`${API_BASE_URL}/api/voice`, {
                        method: "POST",
                        body: formData
                    });
                    
                    const data = await response.json();
                    document.getElementById(loadingId).remove();
                    
                    if (data.status === "success") {
                        addMessageRow("🎤 " + data.recognized_text, "user");
                        addMessageRow(data.reply, "ai");
                    } else {
                        addMessageRow("Error: " + data.reply, "ai");
                    }
                } catch (e) {
                    document.getElementById(loadingId).remove();
                    addMessageRow("Voice processing failed.", "ai");
                }
            };

            mediaRecorder.start();
            isRecording = true;
            micBtn.classList.add("recording");
        } catch (err) {
            alert("Microphone access denied.");
        }
    } else {
        mediaRecorder.stop();
        isRecording = false;
        micBtn.classList.remove("recording");
    }
}