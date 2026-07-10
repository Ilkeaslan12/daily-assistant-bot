from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import traceback

from database import create_tables, get_past_messages, save_chat_message
from ai_models import generate_bot_response, transcribe_audio

# Initialize database schema
create_tables()

app = FastAPI(title="AI Assistant API")

# Configure CORS for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    user_name: str = "User"

def build_context(session_id: str, current_message: str):
    system_prompt = "You are a senior software engineer. ONLY answer programming and tech questions."
    messages = [{"role": "system", "content": system_prompt}]
    
    history = get_past_messages(session_id, limit=3)
    for q, a in reversed(history):
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
        
    messages.append({"role": "user", "content": current_message})
    return messages

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        api_messages = build_context(request.session_id, request.message)
        bot_reply = generate_bot_response(api_messages)
        
        save_chat_message(request.session_id, request.user_name, request.message, bot_reply)
        
        return {"status": "success", "reply": bot_reply}
    except Exception:
        traceback.print_exc()
        return {"status": "error", "reply": "An internal error occurred."}

@app.post("/api/voice")
async def voice_endpoint(session_id: str = Form(...), voice_file: UploadFile = File(...)):
    try:
        file_path = f"temp_{session_id}.ogg"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(voice_file.file, buffer)
        
        user_text = transcribe_audio(file_path)
        os.remove(file_path)
        
        api_messages = build_context(session_id, user_text)
        bot_reply = generate_bot_response(api_messages)
        
        save_chat_message(session_id, "Voice User", user_text, bot_reply)
        
        return {"status": "success", "recognized_text": user_text, "reply": bot_reply}
    except Exception:
        traceback.print_exc()
        return {"status": "error", "reply": "Error processing audio."}