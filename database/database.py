import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any
import os

def get_db_path():
    """Get database path that works in both local and cloud environments"""
    return 'bot_ecosystem.db'

def init_db():
    """Initialize SQLite database"""
    db_path = get_db_path()
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

def save_task(task: Dict):
    """Save task to database"""
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

def get_tasks(limit: int = 100) -> List[Dict]:
    """Get tasks from database"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT data FROM tasks ORDER BY created_at DESC LIMIT ?', (limit,))
    tasks = [json.loads(row[0]) for row in cursor.fetchall()]
    
    conn.close()
    return tasks

def save_report(report: Dict):
    """Save report to database"""
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

def get_reports(limit: int = 50) -> List[Dict]:
    """Get reports from database"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT content FROM reports ORDER BY generated_at DESC LIMIT ?', (limit,))
    reports = [json.loads(row[0]) for row in cursor.fetchall()]
    
    conn.close()
    return reports