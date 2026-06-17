import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "max_memory.db")

def init_db():
    """Create the memories table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_memory(category: str, content: str):
    """Save a new memory. Avoids saving duplicate content."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Prevent exact duplicates
    cursor.execute("SELECT id FROM memories WHERE content = ?", (content,))
    if cursor.fetchone():
        conn.close()
        return  # Already exists, skip

    cursor.execute(
        "INSERT INTO memories (category, content, created_at) VALUES (?, ?, ?)",
        (category, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def fetch_relevant_memories(topic: str) -> list[str]:
    """Fetch memories where content or category matches the topic keywords."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Split topic into keywords and search each one
    keywords = topic.lower().split()
    results = []
    seen = set()

    for keyword in keywords:
        if len(keyword) < 3:  # Skip short words like "a", "is", "the"
            continue
        cursor.execute(
            "SELECT category, content FROM memories WHERE LOWER(content) LIKE ? OR LOWER(category) LIKE ?",
            (f"%{keyword}%", f"%{keyword}%")
        )
        rows = cursor.fetchall()
        for category, content in rows:
            if content not in seen:
                results.append(f"[{category}] {content}")
                seen.add(content)

    conn.close()
    return results[:8]

def get_all_memories() -> list[dict]:
    """Return all memories — useful for a future memory viewer."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, content, created_at FROM memories ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "category": r[1], "content": r[2], "created_at": r[3]} for r in rows]

def delete_memory(memory_id: int):
    """Delete a memory by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
