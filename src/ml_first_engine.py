import yaml
import logging
from datetime import datetime
from typing import Dict, Any, List
from .ml_phishing_detector import MLPhishingDetector

class MLFirstAnalysisEngine:
    """
    Advanced analysis engine that relies solely on ML detection
    No fallback to rule-based systems - pure ML approach
    """
    
    def __init__(self, model_path: str = None):
        self.load_config()
        self.ml_detector = MLPhishingDetector()
        
        if model_path:
            self.load_model(model_path)
        else:
            # Model will need to be trained before use
            self.model_loaded = False
    
    def load_config(self):
        """Load analysis configuration"""
        with open('config/config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
    
    def load_model(self, model_path: str):
        """Load pre-trained ML model - REQUIRED before analysis"""
        try:
            self.ml_detector.load_model(model_path)
            self.model_loaded = True
            logging.info("✅ ML model loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to load ML model: {e}. Model must be trained first.")
    
    def analyze_message(self, message_content: str, sender_info: Dict = None) -> Dict[str, Any]:
        """
        Analyze message using pure ML approach
        Returns comprehensive analysis with ML-driven insights
        """
        if not self.model_loaded:
            raise RuntimeError("ML model must be loaded before analysis. Run load_model() first.")
        
        # ML-based analysis (primary detection method)
        ml_probability, ml_explanation = self.ml_detector.predict(message_content)
        
        # Convert to final risk score (0-100)
        final_score = int(ml_probability * 100)
        
        # Comprehensive analysis report
        analysis_report = {
            'final_score': final_score,
            'risk_level': ml_explanation['risk_level'],
            'ml_analysis': {
                'probability': ml_probability,
                'explanation': ml_explanation,
                'confidence': ml_explanation['confidence']
            },
            'key_indicators': ml_explanation['key_indicators'],
            'behavioral_patterns': ml_explanation['behavioral_patterns'],
            'feature_analysis': ml_explanation['feature_analysis'],
            'temporal_context': self._get_temporal_context(),
            'recommended_action': self._get_recommended_action(ml_explanation['risk_level']),
            'threat_classification': self._classify_threat_type(ml_explanation),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return analysis_report
    
    def _get_temporal_context(self) -> Dict[str, Any]:
        """Add temporal analysis context"""
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        # Business hours vs off-hours context
        if 9 <= current_hour <= 17 and current_day < 5:
            time_context = "business_hours"
        else:
            time_context = "off_hours"
        
        return {
            "hour_of_day": current_hour,
            "day_of_week": current_day,
            "time_context": time_context,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_recommended_action(self, risk_level: str) -> str:
        """Get ML-informed recommended actions"""
        actions = {
            "CRITICAL": "🚨 IMMEDIATE ACTION REQUIRED: Block sender, report to security team, and investigate potential breach",
            "HIGH": "🔴 HIGH PRIORITY: Isolate conversation, monitor for patterns, and prepare incident response",
            "MEDIUM": "🟡 MEDIUM PRIORITY: Flag for review, monitor engagement, and gather additional context",
            "LOW": "🟢 LOW PRIORITY: Continue normal monitoring with standard precautions"
        }
        return actions.get(risk_level, "Monitor with standard security protocols")
    
    def _classify_threat_type(self, ml_explanation: Dict) -> Dict[str, Any]:
        """Classify the type of threat based on ML analysis"""
        indicators = ml_explanation['key_indicators']
        patterns = ml_explanation['behavioral_patterns']
        
        threat_types = []
        confidence = 0.0
        
        # Threat type classification based on indicators
        if any('urgency' in indicator.lower() for indicator in indicators):
            threat_types.append("Urgency-Based Phishing")
            confidence += 0.3
        
        if any('authority' in indicator.lower() for indicator in indicators):
            threat_types.append("Authority Impersonation")
            confidence += 0.3
        
        if any('financial' in indicator.lower() for indicator in indicators):
            threat_types.append("Financial Scam")
            confidence += 0.2
        
        if any('platform migration' in indicator.lower() for indicator in indicators):
            threat_types.append("Platform Migration Attack")
            confidence += 0.2
        
        if any('personal information' in indicator.lower() for indicator in indicators):
            threat_types.append("Information Harvesting")
            confidence += 0.2
        
        # Normalize confidence
        confidence = min(confidence, 1.0)
        
        return {
            "primary_types": threat_types[:2] if threat_types else ["Unclassified Social Engineering"],
            "secondary_types": threat_types[2:] if len(threat_types) > 2 else [],
            "confidence": confidence,
            "techniques_detected": patterns
        }
    
    def batch_analyze(self, messages: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple messages efficiently"""
        if not self.model_loaded:
            raise RuntimeError("ML model must be loaded before analysis")
        
        results = []
        for message in messages:
            try:
                analysis = self.analyze_message(message)
                results.append(analysis)
            except Exception as e:
                logging.error(f"Failed to analyze message: {e}")
                results.append({
                    'error': str(e),
                    'final_score': 0,
                    'risk_level': 'UNKNOWN'
                })
        
        return results