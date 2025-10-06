import sqlite3
import logging
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/honeyshield.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_name TEXT NOT NULL,
                sender_profile_url TEXT,
                message_content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                risk_score INTEGER DEFAULT 0,
                risk_level TEXT DEFAULT 'Low',
                keywords_found TEXT,
                analysis_notes TEXT
            )
        ''')
        
        # Threats table for high-risk interactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_profile_url TEXT UNIQUE,
                first_detected DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_detected DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_messages INTEGER DEFAULT 1,
                max_risk_score INTEGER DEFAULT 0,
                mitre_techniques TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Database setup completed")
    
    def log_message(self, sender_name, sender_profile_url, message_content, risk_score, keywords, notes):
        """Log a new message with analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "High"
        elif risk_score >= 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        cursor.execute('''
            INSERT INTO messages 
            (sender_name, sender_profile_url, message_content, risk_score, risk_level, keywords_found, analysis_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (sender_name, sender_profile_url, message_content, risk_score, risk_level, keywords, notes))
        
        # Update threats table if high risk
        if risk_score >= 40:
            cursor.execute('''
                INSERT OR REPLACE INTO threats 
                (sender_profile_url, last_detected, total_messages, max_risk_score)
                VALUES (?, datetime('now'), 
                    COALESCE((SELECT total_messages FROM threats WHERE sender_profile_url = ?), 0) + 1,
                    MAX(?, COALESCE((SELECT max_risk_score FROM threats WHERE sender_profile_url = ?), 0)))
            ''', (sender_profile_url, sender_profile_url, risk_score, sender_profile_url))
        
        conn.commit()
        conn.close()
    
    def get_recent_messages(self, limit=50):
        """Retrieve recent messages for dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM messages 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        messages = cursor.fetchall()
        conn.close()
        return messages
    
    def get_threat_stats(self):
        """Get threat statistics for dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_messages,
                SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END) as high_risk,
                SUM(CASE WHEN risk_level = 'Medium' THEN 1 ELSE 0 END) as medium_risk,
                COUNT(DISTINCT sender_profile_url) as unique_senders
            FROM messages
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        return stats