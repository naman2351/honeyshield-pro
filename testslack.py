#!/usr/bin/env python3
"""
Test Slack Notifications for Honeyshield
"""

import os
import sys

# Add src to path
sys.path.append('src')

from src.alert_manager import AlertManager
from src.slack_notifier import SlackNotifier

def test_slack_connection():
    """Test if Slack is properly configured"""
    print("🔧 Testing Slack Configuration...")
    print("=" * 50)
    
    slack = SlackNotifier()
    
    if not slack.is_configured():
        print("❌ Slack not configured!")
        print("\n📝 Please set the SLACK_WEBHOOK_URL environment variable:")
        print("export SLACK_WEBHOOK_URL='your_webhook_url_here'")
        print("\n💡 How to get webhook URL:")
        print("1. Go to https://api.slack.com/apps")
        print("2. Create an app and enable Incoming Webhooks")
        print("3. Add webhook to your workspace")
        print("4. Copy the webhook URL")
        return False
    
    print("✅ Slack webhook URL found")
    success, message = slack.test_connection()
    print(message)
    return success

def send_test_alerts():
    """Send test alerts of different severities to Slack"""
    print("\n🚨 Sending Test Alerts to Slack...")
    print("=" * 50)
    
    alert_manager = AlertManager()
    
    test_alerts = [
        {
            'severity': 'CRITICAL',
            'source_platform': 'LinkedIn',
            'sender_name': 'Security Impersonator',
            'sender_profile': 'https://linkedin.com/in/fake-security',
            'message_content': 'URGENT: Your account shows suspicious activity from China. Account will be suspended in 1 hour. Verify immediately: http://linkedin-security-verify.com',
            'risk_score': 96,
            'threat_type': 'Account Takeover Attempt',
            'indicators': 'Extreme urgency, Suspicious links, Geographic anomalies',
            'recommended_action': '🚨 IMMEDIATE: Do not click links. Block sender and contact security team.',
            'ml_confidence': 0.94
        },
        {
            'severity': 'HIGH', 
            'source_platform': 'LinkedIn',
            'sender_name': 'Investment Scammer',
            'sender_profile': 'https://linkedin.com/in/fake-investor',
            'message_content': 'Exclusive crypto investment with 500% returns! Limited spots. Contact Telegram: @WealthManager for details.',
            'risk_score': 82,
            'threat_type': 'Financial Scam',
            'indicators': 'Unrealistic returns, Platform migration, Financial promises',
            'recommended_action': '🔴 HIGH: Mark as scam. Do not engage or share information.',
            'ml_confidence': 0.87
        },
        {
            'severity': 'MEDIUM',
            'source_platform': 'LinkedIn', 
            'sender_name': 'Recruiter Phish',
            'sender_profile': 'https://linkedin.com/in/suspicious-recruiter',
            'message_content': 'Your profile matches our executive role. We need to verify your identity. Please provide personal email and phone number.',
            'risk_score': 65,
            'threat_type': 'Information Harvesting',
            'indicators': 'Personal data request, Vague job offer',
            'recommended_action': '🟡 MEDIUM: Verify company legitimacy before responding.',
            'ml_confidence': 0.72
        }
    ]
    
    for i, alert_data in enumerate(test_alerts, 1):
        print(f"\n📨 Sending alert {i}/3 ({alert_data['severity']} severity)...")
        alert_id = alert_manager.create_alert(alert_data)
        print(f"✅ Alert {alert_id} sent to Slack!")
    
    print(f"\n🎉 All test alerts sent successfully!")
    print("📱 Check your Slack channel for the alerts")
    print("📊 Alerts also saved to dashboard database")

def main():
    """Main test function"""
    print("🚨 Honeyshield Slack Notifier Setup")
    print("=" * 50)
    
    # Test connection first
    if test_slack_connection():
        # Send test alerts
        send_test_alerts()
        
        print("\n" + "=" * 50)
        print("✅ Setup Complete!")
        print("💡 Your Honeyshield system will now automatically send alerts to Slack")
        print("🔧 You can also run: python inject_test_alert.py")

if __name__ == "__main__":
    main()