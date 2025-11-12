import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any
import os
import streamlit as st

def get_db_path():
    """Get database path that works in both local and cloud environments"""
    # Use /tmp directory for Streamlit Cloud which has write permissions
    return '/tmp/bot_ecosystem.db'

def init_db():
    """Initialize SQLite database with error handling for Streamlit Cloud"""
    try:
        db_path = get_db_path()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                type TEXT,
                description TEXT,
                priority TEXT,
                complexity INTEGER,
                status TEXT,
                created_at TEXT,
                completed_at TEXT,
                data TEXT
            )
        ''')
        
        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                report_type TEXT,
                content TEXT,
                generated_at TEXT,
                period_start TEXT,
                period_end TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        st.success("Database initialized successfully!")
        
    except Exception as e:
        st.error(f"Database initialization warning: {str(e)}")
        # Don't raise the error, just continue with the app
        # The database operations will use fallback mechanisms

def save_task(task: Dict):
    """Save task to database with error handling"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tasks 
            (id, type, description, priority, complexity, status, created_at, completed_at, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.get('id'),
            task.get('type'),
            task.get('description'),
            task.get('priority'),
            task.get('complexity'),
            task.get('status'),
            task.get('created_at'),
            task.get('completed_at'),
            json.dumps(task)
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving task: {str(e)}")
        return False

def get_tasks(limit: int = 100) -> List[Dict]:
    """Get tasks from database with error handling"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT data FROM tasks ORDER BY created_at DESC LIMIT ?', (limit,))
        tasks = [json.loads(row[0]) for row in cursor.fetchall()]
        
        conn.close()
        return tasks
    except Exception as e:
        st.error(f"Error loading tasks: {str(e)}")
        return []

def save_report(report: Dict):
    """Save report to database with error handling"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reports (id, report_type, content, generated_at, period_start, period_end)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            str(datetime.now().timestamp()),
            report.get('report_type'),
            json.dumps(report),
            datetime.now().isoformat(),
            report.get('date') or report.get('week_start'),
            report.get('date') or report.get('week_end')
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving report: {str(e)}")
        return False

def get_reports(limit: int = 50) -> List[Dict]:
    """Get reports from database with error handling"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT content FROM reports ORDER BY generated_at DESC LIMIT ?', (limit,))
        reports = [json.loads(row[0]) for row in cursor.fetchall()]
        
        conn.close()
        return reports
    except Exception as e:
        st.error(f"Error loading reports: {str(e)}")
        return []

# Initialize database when module is imported
init_db()
