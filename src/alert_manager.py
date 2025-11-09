import sqlite3
import uuid
from datetime import datetime
import logging
import os

class AlertManager:
    def __init__(self, db_path="data/honeyshield.db"):
        self.db_path = db_path
        self.setup_database()
        self.setup_slack()
    
    def setup_database(self):
        """Setup the alerts database"""
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                severity TEXT NOT NULL,
                status TEXT DEFAULT 'OPEN',
                source_platform TEXT,
                sender_name TEXT,
                sender_profile TEXT,
                message_content TEXT,
                risk_score INTEGER,
                threat_type TEXT,
                indicators TEXT,
                recommended_action TEXT,
                analyst_notes TEXT,
                ml_confidence REAL,
                resolved_at DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_slack(self):
        """Setup Slack notifier"""
        try:
            from .slack_notifier import SlackNotifier
            self.slack = SlackNotifier()
            if self.slack.is_configured():
                logging.info("✅ Slack notifier configured")
            else:
                logging.warning("⚠️ Slack not configured - set SLACK_WEBHOOK_URL environment variable")
                self.slack = None
        except Exception as e:
            logging.warning(f"⚠️ Slack setup failed: {e}")
            self.slack = None
    
    def create_alert(self, alert_data):
        """Create a new security alert and send Slack notification"""
        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_alerts 
            (alert_id, severity, source_platform, sender_name, sender_profile,
             message_content, risk_score, threat_type, indicators, 
             recommended_action, ml_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert_id,
            alert_data['severity'],
            alert_data.get('source_platform', 'LinkedIn'),
            alert_data['sender_name'],
            alert_data.get('sender_profile', ''),
            alert_data['message_content'],
            alert_data['risk_score'],
            alert_data['threat_type'],
            alert_data.get('indicators', ''),
            alert_data.get('recommended_action', ''),
            alert_data.get('ml_confidence', 0.0)
        ))
        
        conn.commit()
        conn.close()
        
        logging.info(f"🚨 New alert created: {alert_id} - {alert_data['severity']} severity")
        
        # Send Slack notification
        if self.slack and self.slack.is_configured():
            alert_data['alert_id'] = alert_id
            self.slack.send_alert(alert_data)
        
        return alert_id
    
    def get_recent_alerts(self, hours=24, severity=None):
        """Get recent alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM security_alerts 
            WHERE timestamp >= datetime('now', ?)
        '''
        params = [f'-{hours} hours']
        
        if severity:
            query += ' AND severity = ?'
            params.append(severity)
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        alerts = cursor.fetchall()
        conn.close()
        
        return alerts