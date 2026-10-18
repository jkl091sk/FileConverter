import asyncio, sqlite3
from datetime import datetime, timezone
from config import config
from database.models import UserSettings

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
 user_id INTEGER PRIMARY KEY,
 language TEXT NOT NULL DEFAULT 'en',
 image_quality INTEGER NOT NULL DEFAULT 90,
 audio_quality TEXT NOT NULL DEFAULT 'medium',
 preserve_filenames INTEGER NOT NULL DEFAULT 1,
 preserve_metadata INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS history (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER NOT NULL,
 original_format TEXT NOT NULL,
 output_format TEXT NOT NULL,
 original_filename TEXT NOT NULL,
 output_filename TEXT NOT NULL,
 file_size INTEGER NOT NULL,
 conversion_date TEXT NOT NULL,
 status TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_history_user_date ON history(user_id, conversion_date DESC);
"""

def _connect():
    c = sqlite3.connect(config.database_path, timeout=30)
    c.row_factory = sqlite3.Row
    return c

async def init_db():
    def work():
        config.database_path.parent.mkdir(parents=True, exist_ok=True)
        with _connect() as db:
            db.executescript(SCHEMA)
    await asyncio.to_thread(work)

async def ensure_user(user_id: int):
    def work():
        with _connect() as db:
            db.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
            db.commit()
    await asyncio.to_thread(work)

async def get_settings(user_id: int) -> UserSettings:
    await ensure_user(user_id)
    def work():
        with _connect() as db:
            r = db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
            return UserSettings(r["user_id"], r["language"], r["image_quality"], r["audio_quality"],
                                bool(r["preserve_filenames"]), bool(r["preserve_metadata"]))
    return await asyncio.to_thread(work)

async def update_setting(user_id: int, field: str, value):
    allowed = {"language","image_quality","audio_quality","preserve_filenames","preserve_metadata"}
    if field not in allowed:
        raise ValueError("Invalid setting")
    await ensure_user(user_id)
    def work():
        with _connect() as db:
            db.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
            db.commit()
    await asyncio.to_thread(work)

async def add_history(user_id, original_format, output_format, original_filename, output_filename, file_size, status):
    def work():
        with _connect() as db:
            db.execute("""INSERT INTO history(user_id,original_format,output_format,original_filename,output_filename,file_size,conversion_date,status)
                          VALUES(?,?,?,?,?,?,?,?)""",
                       (user_id, original_format, output_format, original_filename, output_filename, file_size,
                        datetime.now(timezone.utc).isoformat(), status))
            db.commit()
    await asyncio.to_thread(work)

async def recent_history(user_id: int, limit=10):
    def work():
        with _connect() as db:
            return db.execute("SELECT * FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit)).fetchall()
    return await asyncio.to_thread(work)

async def stats(user_id: int):
    def work():
        with _connect() as db:
            r = db.execute("""SELECT COUNT(*) total,
                SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) ok,
                COALESCE(SUM(file_size),0) bytes FROM history WHERE user_id=?""", (user_id,)).fetchone()
            return dict(r)
    return await asyncio.to_thread(work)
