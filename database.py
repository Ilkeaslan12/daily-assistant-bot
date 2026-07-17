import os
from supabase import Client, create_client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL environment variable bulunamadı.")

if not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_ROLE_KEY environment variable bulunamadı."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_tables():

    return None


def get_summary(session_id: str) -> str:

    return ""


def get_message_count(session_id: str) -> int:

    response = (
        supabase.table("chat_logs")
        .select("id", count="exact")
        .execute()
    )

    return response.count or 0


def get_messages_for_summary(
    session_id: str,
    limit: int = 5,
) -> list[tuple[str, str]]:
    response = (
        supabase.table("chat_logs")
        .select("user_message,bot_response")
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )

    return [
        (
            row.get("user_message", ""),
            row.get("bot_response", ""),
        )
        for row in (response.data or [])
    ]


def save_summary(session_id: str, new_summary: str):

    return None


def get_past_messages(
    session_id: str,
    limit: int = 3,
) -> list[tuple[str, str]]:
    response = (
        supabase.table("chat_logs")
        .select("user_message,bot_response")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return [
        (
            row.get("user_message", ""),
            row.get("bot_response", ""),
        )
        for row in (response.data or [])
    ]


def save_api_request(
    request_type: str,
    detail: str,
    response: str,
):

    return None


def save_chat_message(
    session_id: str,
    user_name: str,
    user_question: str,
    bot_response: str,
):
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
        print(f"Hata kaydı Supabase'e yazılamadı: {logging_error}")


def get_admin_dashboard() -> dict:
    chat_response = (
        supabase.table("chat_logs")
        .select("*")
        .order("created_at", desc=True)
        .limit(1000)
        .execute()
    )

    error_response = (
        supabase.table("error_logs")
        .select("*")
        .order("created_at", desc=True)
        .limit(500)
        .execute()
    )

    chat_logs = chat_response.data or []
    error_logs = error_response.data or []

    return {
        "total_messages": len(chat_logs),
        "total_errors": len(error_logs),
        "recent_messages": chat_logs[:30],
        "recent_errors": error_logs[:30],
    }