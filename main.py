from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import os
import shutil
import traceback

from database import (
    get_past_messages,
    save_chat_message,
    save_error,
)

from ai_models import generate_bot_response, transcribe_audio


app = FastAPI(title="AI Assistant API")


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
    system_prompt = (
        "You are a senior software engineer. "
        "ONLY answer programming and tech questions."
    )

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    history = get_past_messages(
        session_id=session_id,
        limit=3,
    )

    for question, answer in reversed(history):
        messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": current_message,
        }
    )

    return messages


@app.get("/api/health")
async def health_check():
    return {
        "status": "success",
        "message": "API is running.",
    }


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        api_messages = build_context(
            session_id=request.session_id,
            current_message=request.message,
        )

        bot_reply = generate_bot_response(api_messages)

        save_chat_message(
            session_id=request.session_id,
            user_name=request.user_name,
            user_question=request.message,
            bot_response=bot_reply,
        )

        return {
            "status": "success",
            "reply": bot_reply,
        }

    except Exception as error:
        traceback.print_exc()

        save_error(
            error_message=str(error),
            error_type=type(error).__name__,
            session_id=request.session_id,
            agent_name="chat-agent",
        )

        return {
            "status": "error",
            "reply": "An internal error occurred.",
        }


@app.post("/api/voice")
async def voice_endpoint(
    session_id: str = Form(...),
    voice_file: UploadFile = File(...),
):
    file_path = f"/tmp/temp_{session_id}.ogg"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                voice_file.file,
                buffer,
            )

        user_text = transcribe_audio(file_path)

        api_messages = build_context(
            session_id=session_id,
            current_message=user_text,
        )

        bot_reply = generate_bot_response(api_messages)

        save_chat_message(
            session_id=session_id,
            user_name="Voice User",
            user_question=user_text,
            bot_response=bot_reply,
        )

        return {
            "status": "success",
            "recognized_text": user_text,
            "reply": bot_reply,
        }

    except Exception as error:
        traceback.print_exc()

        save_error(
            error_message=str(error),
            error_type=type(error).__name__,
            session_id=session_id,
            agent_name="voice-agent",
        )

        return {
            "status": "error",
            "reply": "Error processing audio.",
        }

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)