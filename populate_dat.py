import sqlite3
import os
from datetime import datetime, timedelta
import random

def populate_test_data():
    """Populate the database with test data"""
    
    # Ensure database exists
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/honeyshield.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
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
    
    # Sample test messages
    test_messages = [
        {
            'sender': 'LinkedIn Security (FAKE)',
            'url': 'https://linkedin.com/in/fake-security',
            'message': 'URGENT: Your account will be suspended. Click here to verify: http://fake-link.com',
            'score': 95,
            'level': 'High',
            'keywords': 'urgent, verify, suspended',
            'notes': 'Critical phishing attempt detected'
        },
        {
            'sender': 'Business Opportunity',
            'url': 'https://linkedin.com/in/investment-scam',
            'message': 'Exclusive investment with 500% returns. Contact me on WhatsApp for details.',
            'score': 75,
            'level': 'High', 
            'keywords': 'investment, returns, WhatsApp',
            'notes': 'Financial scam attempt'
        },
        {
            'sender': 'Recruiter John',
            'url': 'https://linkedin.com/in/legit-recruiter',
            'message': 'Hi, I came across your profile and would like to discuss potential opportunities.',
            'score': 15,
            'level': 'Low',
            'keywords': 'opportunities, discuss',
            'notes': 'Legitimate professional message'
        },
        {
            'sender': 'Government Contract',
            'url': 'https://linkedin.com/in/fake-gov',
            'message': 'We have a confidential government project. Need your bank details for payment.',
            'score': 85,
            'level': 'High',
            'keywords': 'government, confidential, bank details',
            'notes': 'Authority impersonation scam'
        }
    ]
    
    # Insert test data
    for msg in test_messages:
        cursor.execute('''
            INSERT INTO messages 
            (sender_name, sender_profile_url, message_content, risk_score, risk_level, keywords_found, analysis_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            msg['sender'], 
            msg['url'], 
            msg['message'], 
            msg['score'], 
            msg['level'], 
            msg['keywords'], 
            msg['notes']
        ))
    
    conn.commit()
    conn.close()
    
    print("✅ Test data populated successfully!")
    print("📊 You can now run the dashboard to see the data.")

if __name__ == "__main__":
    populate_test_data()