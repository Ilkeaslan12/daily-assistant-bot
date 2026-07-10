import sqlite3

# Initialize database connection
conn = sqlite3.connect('chat_history.db', check_same_thread=False)
cursor = conn.cursor()

def create_tables():
    """Initializes necessary database tables if they do not exist."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_name TEXT,
            user_question TEXT,
            bot_response TEXT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_type TEXT,
            request_detail TEXT,
            api_response TEXT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_summaries (
            session_id TEXT PRIMARY KEY,
            summary TEXT
        )
    ''')
    conn.commit()

def get_summary(session_id: str) -> str:
    """Retrieves the summary for a specific session."""
    cursor.execute("SELECT summary FROM session_summaries WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    return row[0] if row else ""

def get_message_count(session_id: str) -> int:
    """Returns the total number of messages in a session."""
    cursor.execute("SELECT COUNT(*) FROM messages WHERE session_id = ?", (session_id,))
    return cursor.fetchone()[0]

def get_messages_for_summary(session_id: str, limit: int = 5) -> list:
    """Fetches messages for summarization purposes."""
    cursor.execute('''
        SELECT user_question, bot_response 
        FROM messages 
        WHERE session_id = ? 
        ORDER BY id ASC LIMIT ?
    ''', (session_id, limit))
    return cursor.fetchall()

def save_summary(session_id: str, new_summary: str):
    """Saves or updates a session summary."""
    cursor.execute("INSERT OR REPLACE INTO session_summaries (session_id, summary) VALUES (?, ?)", (session_id, new_summary))
    conn.commit()

def get_past_messages(session_id: str, limit: int = 3) -> list:
    """Fetches the most recent messages for context."""
    cursor.execute('''
        SELECT user_question, bot_response 
        FROM messages 
        WHERE session_id = ? 
        ORDER BY id DESC LIMIT ?
    ''', (session_id, limit))
    return cursor.fetchall()

def save_api_request(request_type: str, detail: str, response: str):
    """Logs external API requests for tracking."""
    cursor.execute('''
        INSERT INTO api_requests (request_type, request_detail, api_response)
        VALUES (?, ?, ?)
    ''', (request_type, detail, response))
    conn.commit()

def save_chat_message(session_id: str, user_name: str, user_question: str, bot_response: str):
    """Saves a new chat message to the history."""
    cursor.execute('''
        INSERT INTO messages (session_id, user_name, user_question, bot_response)
        VALUES (?, ?, ?, ?)
    ''', (session_id, user_name, user_question, bot_response))
    conn.commit()