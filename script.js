const API_BASE_URL =
    window.location.hostname === "localhost"
        ? "http://127.0.0.1:8000"
        : "";

const sessionId = "session-" + Math.floor(Math.random() * 1000000);

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
        const requestUrl = `${API_BASE_URL}/api/chat`;

        console.log("Chat request URL:", requestUrl);

        const response = await fetch(requestUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: text,
                user_name: "User",
            }),
        });

        const responseText = await response.text();

        console.log("Chat response status:", response.status);
        console.log("Chat response body:", responseText);

        document.getElementById(loadingId)?.remove();

        if (!response.ok) {
            addMessageRow(
                `Server error (${response.status}): ${responseText}`,
                "ai"
            );
            return;
        }

        let data;

        try {
            data = JSON.parse(responseText);
        } catch (parseError) {
            console.error("JSON parse error:", parseError);

            addMessageRow(
                "Server returned an invalid response: " + responseText,
                "ai"
            );
            return;
        }

        if (data.status === "success") {
            addMessageRow(data.reply, "ai");
        } else {
            addMessageRow(
                "Error: " + (data.reply || "Unknown server error."),
                "ai"
            );
        }
    } catch (error) {
        console.error("Chat request failed:", error);

        document.getElementById(loadingId)?.remove();

        addMessageRow(
            "Connection error: " + error.message,
            "ai"
        );
    }
}


function addMessageRow(text, sender) {
    const chatContainer = document.getElementById("chat-container");

    const rowDiv = document.createElement("div");
    rowDiv.className = "message-row";
    rowDiv.id =
        "msg-" +
        Date.now() +
        "-" +
        Math.floor(Math.random() * 10000);

    const avatarDiv = document.createElement("div");
    avatarDiv.className =
        sender === "ai"
            ? "avatar ai-avatar"
            : "avatar user-avatar";

    avatarDiv.innerText =
        sender === "ai"
            ? "AI"
            : "ME";

    const textDiv = document.createElement("div");
    textDiv.className = "message-content";
    textDiv.innerText = text;

    rowDiv.appendChild(avatarDiv);
    rowDiv.appendChild(textDiv);

    chatContainer.appendChild(rowDiv);

    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth",
    });

    return rowDiv.id;
}


async function toggleRecording() {
    const micBtn = document.getElementById("mic-btn");
    const chatContainer = document.getElementById("chat-container");

    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
            });

            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, {
                    type: "audio/ogg",
                });

                chatContainer.classList.remove("empty-state");

                const loadingId = addMessageRow(
                    "Processing audio...",
                    "ai"
                );

                const formData = new FormData();
                formData.append("session_id", sessionId);
                formData.append(
                    "voice_file",
                    audioBlob,
                    "voice.ogg"
                );

                try {
                    const requestUrl = `${API_BASE_URL}/api/voice`;

                    console.log("Voice request URL:", requestUrl);

                    const response = await fetch(requestUrl, {
                        method: "POST",
                        body: formData,
                    });

                    const responseText = await response.text();

                    console.log(
                        "Voice response status:",
                        response.status
                    );

                    console.log(
                        "Voice response body:",
                        responseText
                    );

                    document.getElementById(loadingId)?.remove();

                    if (!response.ok) {
                        addMessageRow(
                            `Server error (${response.status}): ${responseText}`,
                            "ai"
                        );
                        return;
                    }

                    let data;

                    try {
                        data = JSON.parse(responseText);
                    } catch (parseError) {
                        console.error(
                            "Voice JSON parse error:",
                            parseError
                        );

                        addMessageRow(
                            "Server returned an invalid response: " +
                                responseText,
                            "ai"
                        );
                        return;
                    }

                    if (data.status === "success") {
                        addMessageRow(
                            "🎤 " + data.recognized_text,
                            "user"
                        );

                        addMessageRow(
                            data.reply,
                            "ai"
                        );
                    } else {
                        addMessageRow(
                            "Error: " +
                                (data.reply ||
                                    "Unknown voice error."),
                            "ai"
                        );
                    }
                } catch (error) {
                    console.error(
                        "Voice request failed:",
                        error
                    );

                    document.getElementById(loadingId)?.remove();

                    addMessageRow(
                        "Voice processing failed: " +
                            error.message,
                        "ai"
                    );
                } finally {
                    stream.getTracks().forEach((track) => {
                        track.stop();
                    });
                }
            };

            mediaRecorder.start();

            isRecording = true;
            micBtn.classList.add("recording");
        } catch (error) {
            console.error(
                "Microphone access error:",
                error
            );

            alert(
                "Microphone access was denied or is unavailable."
            );
        }
    } else {
        if (
            mediaRecorder &&
            mediaRecorder.state !== "inactive"
        ) {
            mediaRecorder.stop();
        }

        isRecording = false;
        micBtn.classList.remove("recording");
    }
}


const userInput = document.getElementById("user-input");

if (userInput) {
    userInput.addEventListener("keydown", (event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();
            sendMessage();
        }
    });
}