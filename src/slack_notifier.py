import requests
import json
import logging
import os
from datetime import datetime

class SlackNotifier:
    def __init__(self):
        # Get webhook URL from environment variable
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
    def is_configured(self):
        """Check if Slack is properly configured"""
        return self.webhook_url and self.webhook_url.startswith('https://hooks.slack.com/services/')
    
    def send_alert(self, alert_data):
        """Send alert to Slack"""
        if not self.is_configured():
            logging.warning("⚠️ Slack not configured - set SLACK_WEBHOOK_URL environment variable")
            return False
            
        try:
            message_payload = self._create_slack_message(alert_data)
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(message_payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info("✅ Slack alert sent successfully")
                return True
            else:
                logging.error(f"❌ Slack API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Slack notification failed: {e}")
            return False
    
    def _create_slack_message(self, alert_data):
        """Create formatted Slack message with blocks"""
        
        # Color coding based on severity
        color_map = {
            'CRITICAL': '#ff0000',  # Red
            'HIGH': '#ff6b6b',      # Orange-red
            'MEDIUM': '#ffa726',    # Orange
            'LOW': '#4caf50'        # Green
        }
        
        # Emoji based on severity
        emoji_map = {
            'CRITICAL': '🚨',
            'HIGH': '⚠️',
            'MEDIUM': '🔍', 
            'LOW': 'ℹ️'
        }
        
        severity = alert_data['severity']
        color = color_map.get(severity, '#000000')
        emoji = emoji_map.get(severity, '📢')
        
        # Truncate long messages for preview
        message_preview = alert_data['message_content']
        if len(message_preview) > 200:
            message_preview = message_preview[:200] + "..."
        
        # Create Slack blocks
        blocks = [
            # Header block
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Honeyshield Security Alert {emoji}",
                    "emoji": True
                }
            },
            # Severity and basic info
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{severity}"
                    },
                    {
                        "type": "mrkdwn", 
                        "text": f"*Risk Score:*\n{alert_data['risk_score']}/100"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Threat Type:*\n{alert_data['threat_type']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Source:*\n{alert_data.get('source_platform', 'LinkedIn')}"
                    }
                ]
            },
            # Sender information
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Sender:*\n{alert_data['sender_name']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{datetime.now().strftime('%H:%M:%S')}"
                    }
                ]
            },
            # Message preview
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Message Preview:*\n```{message_preview}```"
                }
            },
            # Key indicators (if available)
        ]
        
        # Add indicators if available
        if alert_data.get('indicators') and alert_data['indicators'] != 'None':
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Detection Indicators:*\n{alert_data['indicators']}"
                }
            })
        
        # Recommended action
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Recommended Action:*\n{alert_data['recommended_action']}"
            }
        })
        
        # Alert ID and divider
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Alert ID: `{alert_data['alert_id']}` | Generated by Honeyshield Security System"
                    }
                ]
            }
        ])
        
        return {
            "blocks": blocks,
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "plain_text",
                                "text": f"{severity} severity alert detected",
                                "emoji": True
                            }
                        }
                    ]
                }
            ]
        }
    
    def test_connection(self):
        """Test if Slack connection works"""
        if not self.is_configured():
            return False, "Slack not configured - set SLACK_WEBHOOK_URL environment variable"
            
        try:
            test_payload = {
                "text": "🔧 Honeyshield connection test - your Slack is properly configured!"
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(test_payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "✅ Slack connection successful - check your channel for test message"
            else:
                return False, f"❌ Slack test failed: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"❌ Slack test failed: {e}"