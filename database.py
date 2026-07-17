import os
from supabase import Client, create_client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL environment variable bulunamadı.")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_ROLE_KEY environment variable bulunamadı."
    )


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)


def get_past_messages(
    session_id: str,
    limit: int = 3,
) -> list[tuple[str, str]]:
    """
    chat_logs tablosundaki son konuşmaları getirir.

    Mevcut tabloda session_id alanı bulunmadığı için
    tüm kullanıcıların son mesajları arasından getirir.
    """
    response = (
        supabase.table("chat_logs")
        .select("user_message,bot_response")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    rows = response.data or []

    return [
        (
            row.get("user_message", ""),
            row.get("bot_response", ""),
        )
        for row in rows
    ]


def save_chat_message(
    session_id: str,
    user_name: str,
    user_question: str,
    bot_response: str,
):
    """
    Kullanıcı mesajını ve bot cevabını chat_logs tablosuna kaydeder.

    session_id ve user_name mevcut tabloda bulunmadığı için
    yalnızca mevcut sütunlar kaydedilir.
    """
    supabase.table("chat_logs").insert(
        {
            "user_message": user_question,
            "bot_response": bot_response,
        }
    ).execute()


def save_error(
    error_message: str,
    error_type: str = "UnknownError",
    session_id: str | None = None,
    agent_name: str | None = None,
):
    """
    Hataları error_logs tablosuna kaydeder.
    """
    details = []

    if agent_name:
        details.append(f"Agent: {agent_name}")

    if session_id:
        details.append(f"Session: {session_id}")

    details.append(str(error_message))

    complete_message = " | ".join(details)

    try:
        supabase.table("error_logs").insert(
            {
                "error_type": error_type,
                "error_message": complete_message[:5000],
            }
        ).execute()

    except Exception as logging_error:
        print(
            "Hata kaydı Supabase'e yazılamadı:",
            logging_error,
        )


def get_admin_dashboard() -> dict:
    """
    Admin paneli için mesaj ve hata verilerini getirir.
    """
    chat_response = (
        supabase.table("chat_logs")
        .select(
            "id,created_at,user_message,bot_response",
            count="exact",
        )
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )

    error_response = (
        supabase.table("error_logs")
        .select(
            "id,created_at,error_type,error_message",
            count="exact",
        )
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )

    chat_logs = chat_response.data or []
    error_logs = error_response.data or []

    return {
        "status": "success",
        "statistics": {
            "total_messages": chat_response.count or len(chat_logs),
            "total_errors": error_response.count or len(error_logs),
        },
        "recent_chats": chat_logs,
        "recent_errors": error_logs,
    }