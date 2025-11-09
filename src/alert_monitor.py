import time
import logging
from datetime import datetime
from .ml_first_engine import MLFirstAnalysisEngine
from .alert_manager import AlertManager
from .profile_manager import LinkedInManager
from .message_monitor import MessageMonitor

class AlertMonitor:
    def __init__(self):
        self.engine = MLFirstAnalysisEngine()
        self.alert_manager = AlertManager()
        
        # Load ML model
        self.engine.load_model("models/advanced_phishing_detector.pkl")
    
    def process_message_as_alert(self, message_data):
        """Process message and create security alert if needed"""
        # ML Analysis
        analysis_result = self.engine.analyze_message(message_data['messageContent'])
        
        # Only create alert for medium+ risk
        if analysis_result['final_score'] >= 40:
            alert_data = {
                'severity': analysis_result['risk_level'],
                'source_platform': 'LinkedIn',
                'sender_name': message_data['senderName'],
                'sender_profile': message_data.get('senderUrl', ''),
                'message_content': message_data['messageContent'],
                'risk_score': analysis_result['final_score'],
                'threat_type': analysis_result['threat_classification']['primary_types'][0] if analysis_result['threat_classification']['primary_types'] else 'Unknown',
                'indicators': ', '.join(analysis_result['key_indicators']),
                'recommended_action': analysis_result['recommended_action'],
                'ml_confidence': analysis_result['ml_analysis']['confidence']
            }
            
            alert_id = self.alert_manager.create_alert(alert_data)
            
            # Log the alert
            logging.info(f"🚨 ALERT {alert_id}: {analysis_result['risk_level']} threat from {message_data['senderName']}")
            
            return alert_id, analysis_result
        
        return None, analysis_result
    
    def monitor_cycle(self):
        """Run one monitoring cycle creating alerts"""
        linkedin_manager = LinkedInManager()
        
        try:
            if linkedin_manager.login():
                message_monitor = MessageMonitor(linkedin_manager)
                messages = message_monitor.scrape_messages()
                
                alerts_created = 0
                for message in messages:
                    alert_id, analysis = self.process_message_as_alert(message)
                    if alert_id:
                        alerts_created += 1
                        print(f"🚨 {analysis['risk_level']} ALERT - {message['senderName']} - Score: {analysis['final_score']}")
                
                print(f"✅ Monitoring complete: {alerts_created} alerts created from {len(messages)} messages")
                
        finally:
            linkedin_manager.close()