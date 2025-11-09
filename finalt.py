import sqlite3
import uuid
import os

def inject_all_alerts():
    """Inject all 3 alert types at once"""
    
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/honeyshield.db')
    cursor = conn.cursor()

    alerts = [
        (
            'ALT-' + uuid.uuid4().hex[:8].upper(), 
            'CRITICAL', 
            'LinkedIn', 
            'Security Impersonator', 
            'https://linkedin.com/in/fake-linkedin-security',
            'URGENT: Your LinkedIn account has been compromised! Multiple unauthorized login attempts detected from China. Account will be permanently suspended in 1 hour unless you verify your identity immediately: http://linkedin-security-verification-now.com/verify?id=893745',
            96, 
            'Account Takeover Attempt', 
            'Extreme urgency, Suspicious links, Geographic anomalies, Authority impersonation', 
            '🚨 IMMEDIATE ACTION: DO NOT CLICK LINKS. Block sender, change passwords, and contact IT security team immediately.', 
            0.94
        ),
        (
            'ALT-' + uuid.uuid4().hex[:8].upper(), 
            'HIGH', 
            'LinkedIn', 
            'Elite Investment Advisor', 
            'https://linkedin.com/in/crypto-wealth-manager',
            'Exclusive opportunity: Private cryptocurrency fund with 700% guaranteed returns. Only 5 spots remaining for accredited investors. Minimum investment $50,000. Contact me directly on Telegram: @CryptoWealthPro',
            82, 
            'Financial Scam', 
            'Unrealistic returns, Platform migration, High-pressure tactics, Financial terminology', 
            '🔴 HIGH PRIORITY: Mark as financial scam. Do not engage or share any financial information.', 
            0.87
        ),
        (
            'ALT-' + uuid.uuid4().hex[:8].upper(), 
            'MEDIUM', 
            'LinkedIn', 
            'Tech Recruiter - Meta Platforms', 
            'https://linkedin.com/in/meta-recruiter-fake',
            'Congratulations! Your profile has been shortlisted for Senior AI Engineer position at Meta. Please provide your personal email, phone number, and current salary details.',
            68, 
            'Information Harvesting', 
            'Employment scam, Personal data collection, Brand impersonation', 
            '🟡 MEDIUM PRIORITY: Verify company legitimacy before responding.', 
            0.76
        )
    ]

    for alert in alerts:
        cursor.execute('''
            INSERT INTO security_alerts 
            (alert_id, severity, source_platform, sender_name, sender_profile, message_content, risk_score, threat_type, indicators, recommended_action, ml_confidence, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
        ''', alert)

    conn.commit()
    conn.close()
    print('✅ ALL 3 ALERTS INJECTED SUCCESSFULLY!')
    print('🚨 1 CRITICAL Alert (96 score)')
    print('⚠️  1 HIGH Alert (82 score)') 
    print('🔍 1 MEDIUM Alert (68 score)')
    print('📊 Check your dashboard to see all alerts!')

if __name__ == "__main__":
    inject_all_alerts()