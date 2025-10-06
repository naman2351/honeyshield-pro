import yaml
import re
from textblob import TextBlob
import logging

class AnalysisEngine:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load analysis configuration"""
        with open('config/config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
    
    def calculate_risk_score(self, message_content, sender_info=None):
        """Calculate risk score for a message"""
        risk_score = 0
        detected_keywords = []
        analysis_notes = []
        
        # Keyword analysis
        keyword_score, keywords = self.analyze_keywords(message_content)
        risk_score += keyword_score
        detected_keywords.extend(keywords)
        
        # Sentiment analysis
        sentiment_score = self.analyze_sentiment(message_content)
        risk_score += sentiment_score
        
        # Relationship escalation detection
        escalation_score = self.detect_relationship_escalation(message_content)
        risk_score += escalation_score
        if escalation_score > 0:
            analysis_notes.append("Rapid relationship escalation detected")
        
        # Private info request detection
        private_info_score = self.detect_private_info_request(message_content)
        risk_score += private_info_score
        if private_info_score > 0:
            analysis_notes.append("Potential private information request")
        
        # Ensure score doesn't exceed 100
        risk_score = min(risk_score, 100)
        
        return {
            'risk_score': risk_score,
            'keywords': ', '.join(detected_keywords) if detected_keywords else 'None',
            'analysis_notes': '; '.join(analysis_notes) if analysis_notes else 'No significant alerts'
        }
    
    def analyze_keywords(self, text):
        """Analyze text for suspicious keywords"""
        score = 0
        detected = []
        
        text_lower = text.lower()
        
        for keyword in self.config['analysis']['suspicious_keywords']:
            if keyword.lower() in text_lower:
                score += self.config['scoring']['keyword_weight']
                detected.append(keyword)
        
        for phrase in self.config['analysis']['high_risk_phrases']:
            if phrase.lower() in text_lower:
                score += self.config['scoring']['keyword_weight'] * 2
                detected.append(phrase)
        
        return score, detected
    
    def analyze_sentiment(self, text):
        """Analyze sentiment and score urgency/positivity"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Very positive or very negative sentiments might indicate manipulation
            if abs(polarity) > 0.5:
                return self.config['scoring']['sentiment_weight']
            return 0
        except:
            return 0
    
    def detect_relationship_escalation(self, text):
        """Detect attempts to rapidly escalate relationship"""
        escalation_patterns = [
            r'immediately',
            r'as soon as possible',
            r'urgent',
            r'right away',
            r'let.me.(call|meet).you',
            r'we.need.to.talk',
        ]
        
        text_lower = text.lower()
        for pattern in escalation_patterns:
            if re.search(pattern, text_lower):
                return self.config['scoring']['relationship_escalation_weight']
        
        return 0
    
    def detect_private_info_request(self, text):
        """Detect requests for private information"""
        private_info_patterns = [
            r'phone.number',
            r'whatsapp',
            r'telegram',
            r'personal.email',
            r'home.address',
            r'send.me.your',
            r'give.me.your'
        ]
        
        text_lower = text.lower()
        for pattern in private_info_patterns:
            if re.search(pattern, text_lower):
                return self.config['scoring']['request_private_info_weight']
        
        return 0
    
    def map_to_mitre(self, risk_data):
        """Map detected behaviors to MITRE ATT&CK techniques"""
        techniques = []
        
        if risk_data['risk_score'] >= 40:
            techniques.append("T1589.001 - Gather Victim Identity Information")
        
        if "private information request" in risk_data['analysis_notes'].lower():
            techniques.append("T1594 - Search Victim-Owned Websites")
        
        if risk_data['risk_score'] >= 70:
            techniques.append("T1585 - Establish Accounts")
            techniques.append("T1588 - Obtain Capabilities")
        
        return ", ".join(techniques) if techniques else "TBD - Further analysis needed"