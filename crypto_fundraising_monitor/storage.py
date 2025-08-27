"""
Storage module for Crypto Fundraising Monitor
"""
import sqlite3
import logging
from typing import List, Set, Optional
from datetime import datetime
from .models import FundraisingProject
from .config import DB_PATH

logger = logging.getLogger(__name__)


class ProjectStorage:
    """SQLite storage for tracking sent projects"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create projects table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        amount_usd INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index for faster lookups
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_unique_id ON projects(unique_id)
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def get_sent_project_ids(self) -> Set[str]:
        """Get set of project IDs that have already been sent"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT unique_id FROM projects')
                rows = cursor.fetchall()
                return {row[0] for row in rows}
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get sent project IDs: {e}")
            return set()
    
    def mark_project_sent(self, project: FundraisingProject):
        """Mark a project as sent"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO projects (unique_id, name, amount_usd, date)
                    VALUES (?, ?, ?, ?)
                ''', (project.unique_id, project.name, project.amount_usd, project.date))
                
                conn.commit()
                logger.debug(f"Marked project as sent: {project.name}")
                
        except sqlite3.IntegrityError:
            # Project already exists, this is fine
            logger.debug(f"Project already marked as sent: {project.name}")
        except sqlite3.Error as e:
            logger.error(f"Failed to mark project as sent: {e}")
    
    def get_new_projects(self, all_projects: List[FundraisingProject]) -> List[FundraisingProject]:
        """Filter out projects that have already been sent"""
        sent_ids = self.get_sent_project_ids()
        new_projects = [p for p in all_projects if p.unique_id not in sent_ids]
        
        logger.info(f"Found {len(new_projects)} new projects out of {len(all_projects)} total")
        return new_projects
    
    def cleanup_old_records(self, days_to_keep: int = 30):
        """Clean up old project records"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM projects 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days_to_keep))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old project records")
                    
        except sqlite3.Error as e:
            logger.error(f"Failed to cleanup old records: {e}")
    
    def get_stats(self) -> dict:
        """Get storage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total projects
                cursor.execute('SELECT COUNT(*) FROM projects')
                total_projects = cursor.fetchone()[0]
                
                # Projects sent today
                cursor.execute('''
                    SELECT COUNT(*) FROM projects 
                    WHERE DATE(sent_at) = DATE('now')
                ''')
                today_projects = cursor.fetchone()[0]
                
                # Projects sent this week
                cursor.execute('''
                    SELECT COUNT(*) FROM projects 
                    WHERE sent_at >= datetime('now', '-7 days')
                ''')
                week_projects = cursor.fetchone()[0]
                
                return {
                    'total_projects': total_projects,
                    'today_projects': today_projects,
                    'week_projects': week_projects
                }
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        # SQLite connections are automatically closed when using context manager
        pass 