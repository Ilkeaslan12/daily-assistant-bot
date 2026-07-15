import psycopg2

# Supabase'den kopyaladığın linki buraya yapıştır
DB_URL = "postgresql://postgres:[aW7AOZ6pmR83YeLA]@db.qtztimeicupjpsxfpukm.supabase.co:5432/postgres"

def get_connection():
    """Her işlemde veritabanına taze ve güvenli bir bağlantı açar."""
    return psycopg2.connect(DB_URL)

def create_tables():
    """Tabloları Supabase üzerinde oluşturur."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # PostgreSQL için AUTOINCREMENT yerine SERIAL kullanılır
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT,
                    user_name TEXT,
                    user_question TEXT,
                    bot_response TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_requests (
                    id SERIAL PRIMARY KEY,
                    request_type TEXT,
                    request_detail TEXT,
                    api_response TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # PostgreSQL parametre olarak ? yerine %s kullanır
            cursor.execute("SELECT summary FROM session_summaries WHERE session_id = %s", (session_id,))
            row = cursor.fetchone()
            return row[0] if row else ""

def get_message_count(session_id: str) -> int:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM messages WHERE session_id = %s", (session_id,))
            return cursor.fetchone()[0]

def get_messages_for_summary(session_id: str, limit: int = 5) -> list:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT user_question, bot_response 
                FROM messages 
                WHERE session_id = %s 
                ORDER BY id ASC LIMIT %s
            ''', (session_id, limit))
            return cursor.fetchall()

def save_summary(session_id: str, new_summary: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # PostgreSQL için INSERT OR REPLACE karşılığı
            cursor.execute('''
                INSERT INTO session_summaries (session_id, summary) 
                VALUES (%s, %s) 
                ON CONFLICT (session_id) 
                DO UPDATE SET summary = EXCLUDED.summary
            ''', (session_id, new_summary))
            conn.commit()

def get_past_messages(session_id: str, limit: int = 3) -> list:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT user_question, bot_response 
                FROM messages 
                WHERE session_id = %s 
                ORDER BY id DESC LIMIT %s
            ''', (session_id, limit))
            return cursor.fetchall()

def save_api_request(request_type: str, detail: str, response: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO api_requests (request_type, request_detail, api_response)
                VALUES (%s, %s, %s)
            ''', (request_type, detail, response))
            conn.commit()

def save_chat_message(session_id: str, user_name: str, user_question: str, bot_response: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO messages (session_id, user_name, user_question, bot_response)
                VALUES (%s, %s, %s, %s)
            ''', (session_id, user_name, user_question, bot_response))
            conn.commit()