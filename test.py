import sqlite3
import uuid
import os

def inject_test_alert():
    """Inject a test alert that will show up immediately in the dashboard"""
    
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/honeyshield.db')
    cursor = conn.cursor()

    alert_data = (
        'ALT-' + uuid.uuid4().hex[:8].upper(),
        'CRITICAL',
        'LinkedIn',
        'Security Impersonator',
        'https://linkedin.com/in/fake-security-team',
        'URGENT SECURITY ALERT: Your account shows suspicious activity from multiple countries. Immediate verification required to prevent permanent suspension. Click here: http://linkedin-verify-account-now.com/secure?id=48291',
        94,
        'Account Takeover Attempt', 
        'Extreme urgency, Suspicious links, Multiple geographic locations, Authority pressure',
        '🚨 IMMEDIATE ACTION REQUIRED: Do not click any links. Block this sender immediately and contact security team.',
        0.91
    )

    cursor.execute('''
        INSERT INTO security_alerts 
        (alert_id, severity, source_platform, sender_name, sender_profile, message_content, risk_score, threat_type, indicators, recommended_action, ml_confidence, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
    ''', alert_data)

    conn.commit()
    conn.close()
    print('🚨 TEST ALERT INJECTED SUCCESSFULLY!')
    print('📊 Go to your dashboard and click "Refresh" to see the new alert!')
    print('💡 You can click on the alert to view full details and recommended actions.')

if __name__ == "__main__":
    inject_test_alert()