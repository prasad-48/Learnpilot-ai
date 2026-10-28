import sqlite3
import json
from typing import Dict, Any

DB_PATH = "tutor.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            grade_level TEXT,
            age INTEGER,
            learning_style TEXT,
            language TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mastery (
            student_id TEXT,
            topic TEXT,
            score INTEGER,
            last_reviewed TEXT,
            PRIMARY KEY (student_id, topic)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            session_date TEXT DEFAULT CURRENT_TIMESTAMP,
            agent_invoked TEXT,
            task TEXT,
            response_json TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def upsert_student(profile: Dict[str, Any]):
    """Upsert student profile data into SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        REPLACE INTO students (student_id, name, grade_level, age, learning_style, language)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        profile.get('student_id'),
        profile.get('name'),
        profile.get('grade_level'),
        profile.get('age'),
        profile.get('learning_style'),
        profile.get('language')
    ))
    conn.commit()
    conn.close()

def update_topic_mastery(student_id: str, topic: str, score: int):
    """Update a specific concept mastery score for a student."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        REPLACE INTO mastery (student_id, topic, score, last_reviewed)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (student_id, topic, score))
    conn.commit()
    conn.close()

def get_student_mastery(student_id: str) -> Dict[str, int]:
    """Retrieve all topic mastery scores for a specific student."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT topic, score FROM mastery WHERE student_id = ?', (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def log_session(student_id: str, agent_invoked: str, task: str, response: Dict):
    """Log an interaction session with the EduPilot agents."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO session_logs (student_id, agent_invoked, task, response_json)
        VALUES (?, ?, ?, ?)
    ''', (student_id, agent_invoked, task, json.dumps(response)))
    conn.commit()
    conn.close()

# Initialize when imported
init_db()
