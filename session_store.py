#!/usr/bin/env python3
"""
Session Store for vibe.ai
Provides advanced storage and retrieval capabilities for sessions
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import shutil
import gzip


@dataclass
class SessionQuery:
    """Query parameters for searching sessions"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    title_contains: Optional[str] = None
    tags: Optional[List[str]] = None
    file_path_contains: Optional[str] = None
    command_contains: Optional[str] = None
    min_duration: Optional[int] = None  # seconds
    max_duration: Optional[int] = None  # seconds
    has_errors: Optional[bool] = None
    limit: int = 100


class SessionStore:
    """Advanced session storage with search and analytics"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.home() / ".vibe" / "sessions"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.base_dir / "sessions.db"
        self.archive_dir = self.base_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for session metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds INTEGER,
                file_path TEXT,
                total_events INTEGER,
                files_modified INTEGER,
                commands_executed INTEGER,
                api_calls INTEGER,
                has_errors BOOLEAN,
                is_archived BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_tags (
                session_id TEXT,
                tag TEXT,
                PRIMARY KEY (session_id, tag),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Events table (for quick searching)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TIMESTAMP,
                event_type TEXT,
                description TEXT,
                details TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_files (
                session_id TEXT,
                file_path TEXT,
                action TEXT,
                first_modified TIMESTAMP,
                last_modified TIMESTAMP,
                modification_count INTEGER,
                PRIMARY KEY (session_id, file_path),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Commands table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                command TEXT,
                timestamp TIMESTAMP,
                return_code INTEGER,
                has_error BOOLEAN,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_title ON sessions(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_session_id ON session_events(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON session_events(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON session_files(file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_commands_command ON session_commands(command)")
        
        conn.commit()
        conn.close()
    
    def save_session(self, session_data: Dict[str, Any], file_path: Path):
        """Save session to store and update database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Calculate metrics
            duration = None
            if session_data.get("end_time") and session_data.get("start_time"):
                start = datetime.fromisoformat(session_data["start_time"])
                end = datetime.fromisoformat(session_data["end_time"])
                duration = int((end - start).total_seconds())
            
            # Count errors
            has_errors = any(e["event_type"] == "error_occurred" 
                           for e in session_data.get("events", []))
            
            # Insert or update session
            cursor.execute("""
                INSERT OR REPLACE INTO sessions 
                (id, title, description, start_time, end_time, duration_seconds,
                 file_path, total_events, files_modified, commands_executed,
                 api_calls, has_errors)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data["id"],
                session_data.get("title", ""),
                session_data.get("description", ""),
                session_data.get("start_time"),
                session_data.get("end_time"),
                duration,
                str(file_path),
                len(session_data.get("events", [])),
                len(session_data.get("files_modified", {})),
                len(session_data.get("commands_executed", [])),
                len(session_data.get("api_calls", [])),
                has_errors
            ))
            
            # Clear and insert tags
            cursor.execute("DELETE FROM session_tags WHERE session_id = ?", 
                         (session_data["id"],))
            for tag in session_data.get("tags", []):
                cursor.execute("INSERT INTO session_tags (session_id, tag) VALUES (?, ?)",
                             (session_data["id"], tag))
            
            # Insert events (sample for searching)
            cursor.execute("DELETE FROM session_events WHERE session_id = ?",
                         (session_data["id"],))
            for event in session_data.get("events", [])[:100]:  # Store first 100
                cursor.execute("""
                    INSERT INTO session_events 
                    (session_id, timestamp, event_type, description, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_data["id"],
                    event["timestamp"],
                    event["event_type"],
                    event["description"],
                    json.dumps(event.get("details", {}))
                ))
            
            # Insert files
            cursor.execute("DELETE FROM session_files WHERE session_id = ?",
                         (session_data["id"],))
            for file_path, modifications in session_data.get("files_modified", {}).items():
                if modifications:
                    cursor.execute("""
                        INSERT INTO session_files 
                        (session_id, file_path, action, first_modified, 
                         last_modified, modification_count)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        session_data["id"],
                        file_path,
                        modifications[0]["action"],
                        modifications[0]["timestamp"],
                        modifications[-1]["timestamp"],
                        len(modifications)
                    ))
            
            # Insert commands
            cursor.execute("DELETE FROM session_commands WHERE session_id = ?",
                         (session_data["id"],))
            for cmd in session_data.get("commands_executed", [])[:50]:  # Store first 50
                cursor.execute("""
                    INSERT INTO session_commands 
                    (session_id, command, timestamp, return_code, has_error)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_data["id"],
                    cmd["command"],
                    cmd["timestamp"],
                    cmd.get("return_code"),
                    bool(cmd.get("error"))
                ))
            
            conn.commit()
        finally:
            conn.close()
    
    def search_sessions(self, query: SessionQuery) -> List[Dict[str, Any]]:
        """Search sessions based on query parameters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build SQL query
        sql = """
            SELECT DISTINCT s.* 
            FROM sessions s
            WHERE 1=1
        """
        params = []
        
        if query.start_date:
            sql += " AND s.start_time >= ?"
            params.append(query.start_date.isoformat())
        
        if query.end_date:
            sql += " AND s.start_time <= ?"
            params.append(query.end_date.isoformat())
        
        if query.title_contains:
            sql += " AND s.title LIKE ?"
            params.append(f"%{query.title_contains}%")
        
        if query.min_duration is not None:
            sql += " AND s.duration_seconds >= ?"
            params.append(query.min_duration)
        
        if query.max_duration is not None:
            sql += " AND s.duration_seconds <= ?"
            params.append(query.max_duration)
        
        if query.has_errors is not None:
            sql += " AND s.has_errors = ?"
            params.append(query.has_errors)
        
        # Handle tags
        if query.tags:
            sql += f" AND s.id IN (SELECT session_id FROM session_tags WHERE tag IN ({','.join(['?']*len(query.tags))}))"
            params.extend(query.tags)
        
        # Handle file path search
        if query.file_path_contains:
            sql += " AND s.id IN (SELECT session_id FROM session_files WHERE file_path LIKE ?)"
            params.append(f"%{query.file_path_contains}%")
        
        # Handle command search
        if query.command_contains:
            sql += " AND s.id IN (SELECT session_id FROM session_commands WHERE command LIKE ?)"
            params.append(f"%{query.command_contains}%")
        
        sql += " ORDER BY s.start_time DESC LIMIT ?"
        params.append(query.limit)
        
        cursor.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            session_dict = dict(zip(columns, row))
            
            # Get tags
            cursor.execute("SELECT tag FROM session_tags WHERE session_id = ?",
                         (session_dict["id"],))
            session_dict["tags"] = [row[0] for row in cursor.fetchall()]
            
            results.append(session_dict)
        
        conn.close()
        return results
    
    def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT file_path FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        file_path = Path(row[0])
        if file_path.exists():
            with open(file_path) as f:
                return json.load(f)
        
        # Check archive
        archive_path = self.archive_dir / f"{session_id}.json.gz"
        if archive_path.exists():
            with gzip.open(archive_path, 'rt') as f:
                return json.load(f)
        
        return None
    
    def archive_old_sessions(self, days: int = 30):
        """Archive sessions older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, file_path 
            FROM sessions 
            WHERE end_time < ? AND is_archived = FALSE
        """, (cutoff_date.isoformat(),))
        
        sessions_to_archive = cursor.fetchall()
        
        for session_id, file_path in sessions_to_archive:
            source_path = Path(file_path)
            if source_path.exists():
                # Compress and move to archive
                archive_path = self.archive_dir / f"{session_id}.json.gz"
                
                with open(source_path, 'rb') as f_in:
                    with gzip.open(archive_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove original
                source_path.unlink()
                
                # Update database
                cursor.execute("""
                    UPDATE sessions 
                    SET is_archived = TRUE, file_path = ?
                    WHERE id = ?
                """, (str(archive_path), session_id))
        
        conn.commit()
        conn.close()
        
        return len(sessions_to_archive)
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get session statistics for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(duration_seconds) as total_duration,
                AVG(duration_seconds) as avg_duration,
                SUM(files_modified) as total_files,
                SUM(commands_executed) as total_commands,
                SUM(api_calls) as total_api_calls,
                SUM(CASE WHEN has_errors THEN 1 ELSE 0 END) as sessions_with_errors
            FROM sessions
            WHERE start_time >= ?
        """, (cutoff_date.isoformat(),))
        
        stats = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))
        
        # Most active days
        cursor.execute("""
            SELECT 
                DATE(start_time) as day,
                COUNT(*) as session_count,
                SUM(duration_seconds) as total_duration
            FROM sessions
            WHERE start_time >= ?
            GROUP BY DATE(start_time)
            ORDER BY session_count DESC
            LIMIT 10
        """, (cutoff_date.isoformat(),))
        
        stats["most_active_days"] = [
            dict(zip([desc[0] for desc in cursor.description], row))
            for row in cursor.fetchall()
        ]
        
        # Most modified files
        cursor.execute("""
            SELECT 
                file_path,
                COUNT(DISTINCT session_id) as session_count,
                SUM(modification_count) as total_modifications
            FROM session_files sf
            JOIN sessions s ON sf.session_id = s.id
            WHERE s.start_time >= ?
            GROUP BY file_path
            ORDER BY total_modifications DESC
            LIMIT 20
        """, (cutoff_date.isoformat(),))
        
        stats["most_modified_files"] = [
            dict(zip([desc[0] for desc in cursor.description], row))
            for row in cursor.fetchall()
        ]
        
        # Most used commands
        cursor.execute("""
            SELECT 
                SUBSTR(command, 1, INSTR(command || ' ', ' ') - 1) as command_name,
                COUNT(*) as usage_count
            FROM session_commands sc
            JOIN sessions s ON sc.session_id = s.id
            WHERE s.start_time >= ?
            GROUP BY command_name
            ORDER BY usage_count DESC
            LIMIT 20
        """, (cutoff_date.isoformat(),))
        
        stats["most_used_commands"] = [
            dict(zip([desc[0] for desc in cursor.description], row))
            for row in cursor.fetchall()
        ]
        
        # Popular tags
        cursor.execute("""
            SELECT 
                tag,
                COUNT(*) as usage_count
            FROM session_tags st
            JOIN sessions s ON st.session_id = s.id
            WHERE s.start_time >= ?
            GROUP BY tag
            ORDER BY usage_count DESC
            LIMIT 20
        """, (cutoff_date.isoformat(),))
        
        stats["popular_tags"] = [
            dict(zip([desc[0] for desc in cursor.description], row))
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return stats
    
    def cleanup_incomplete_sessions(self):
        """Clean up incomplete or corrupted sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find sessions without end time older than 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        cursor.execute("""
            SELECT id, file_path
            FROM sessions
            WHERE end_time IS NULL AND start_time < ?
        """, (cutoff.isoformat(),))
        
        incomplete_sessions = cursor.fetchall()
        
        for session_id, file_path in incomplete_sessions:
            # Mark as ended
            cursor.execute("""
                UPDATE sessions
                SET end_time = start_time, 
                    description = description || ' [Auto-closed due to inactivity]'
                WHERE id = ?
            """, (session_id,))
        
        conn.commit()
        conn.close()
        
        return len(incomplete_sessions)


if __name__ == "__main__":
    # Test the session store
    store = SessionStore()
    
    # Search recent sessions
    query = SessionQuery(
        start_date=datetime.now() - timedelta(days=7),
        title_contains="vibe"
    )
    
    results = store.search_sessions(query)
    print(f"Found {len(results)} sessions")
    
    # Get statistics
    stats = store.get_statistics(days=30)
    print(f"\nStatistics for last 30 days:")
    print(f"Total sessions: {stats['total_sessions']}")
    print(f"Total duration: {stats['total_duration']/3600:.1f} hours")
    
    # Archive old sessions
    archived = store.archive_old_sessions(days=30)
    print(f"\nArchived {archived} old sessions")