import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import re
import json
from typing import Dict, Tuple, List
import logging

class MLPhishingDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8
        )
        self.classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.is_trained = False
        self.feature_names = []
        
    def extract_advanced_features(self, text: str) -> Dict[str, float]:
        """Extract comprehensive linguistic and behavioral features"""
        text_lower = text.lower()
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        features = {}
        
        # Text complexity metrics
        features['text_length'] = len(text)
        features['word_count'] = len(words)
        features['sentence_count'] = max(len([s for s in sentences if s.strip()]), 1)
        features['avg_sentence_length'] = features['word_count'] / features['sentence_count']
        features['avg_word_length'] = sum(len(word) for word in words) / max(features['word_count'], 1)
        
        # Psychological manipulation indicators
        urgency_patterns = r'\b(urgent|immediately|asap|quick|fast|now|instant|right away|hurry)\b'
        features['urgency_score'] = len(re.findall(urgency_patterns, text_lower))
        
        authority_patterns = r'\b(official|government|legal|compliance|required|mandatory|authorized|security|verify)\b'
        features['authority_score'] = len(re.findall(authority_patterns, text_lower))
        
        scarcity_patterns = r'\b(limited|only|exclusive|last chance|final|ending soon|never again)\b'
        features['scarcity_score'] = len(re.findall(scarcity_patterns, text_lower))
        
        social_proof_patterns = r'\b(everyone|people|others|join|many|most|popular)\b'
        features['social_proof_score'] = len(re.findall(social_proof_patterns, text_lower))
        
        # Information harvesting signals
        personal_info_patterns = r'\b(phone|number|email|address|bank|account|password|verify|confirm|details)\b'
        features['info_request_score'] = len(re.findall(personal_info_patterns, text_lower))
        
        financial_patterns = r'\b(money|payment|investment|profit|fund|cash|price|fee|cost|payment)\b'
        features['financial_score'] = len(re.findall(financial_patterns, text_lower))
        
        # Platform migration attempts
        platform_patterns = r'\b(whatsapp|telegram|signal|wechat|viber|skype|email me|call me|text me)\b'
        features['platform_migration_score'] = len(re.findall(platform_patterns, text_lower))
        
        # Structural analysis
        features['question_marks'] = text.count('?')
        features['exclamation_marks'] = text.count('!')
        features['capital_ratio'] = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        features['link_count'] = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
        
        # Readability and sophistication
        features['unique_word_ratio'] = len(set(words)) / max(features['word_count'], 1)
        features['long_word_count'] = sum(1 for word in words if len(word) > 6)
        
        # Emotional manipulation
        positive_emotion = r'\b(great|amazing|wonderful|impressive|fantastic|excellent|perfect)\b'
        negative_emotion = r'\b(urgent|suspended|terminated|legal|consequences|problem|issue)\b'
        features['positive_emotion_score'] = len(re.findall(positive_emotion, text_lower))
        features['negative_emotion_score'] = len(re.findall(negative_emotion, text_lower))
        
        return features
    
    def train(self, texts: List[str], labels: List[int], test_size: float = 0.2):
        """Train the ML model with comprehensive feature engineering"""
        print("🔄 Starting model training with advanced feature engineering...")
        
        # Extract advanced features
        advanced_features = []
        for text in texts:
            features = self.extract_advanced_features(text)
            advanced_features.append(list(features.values()))
        
        # TF-IDF features
        tfidf_features = self.vectorizer.fit_transform(texts)
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        # Combine all features
        advanced_array = np.array(advanced_features)
        combined_features = np.hstack([tfidf_features.toarray(), advanced_array])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            combined_features, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        # Train classifier
        self.classifier.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate model
        train_score = self.classifier.score(X_train, y_train)
        test_score = self.classifier.score(X_test, y_test)
        
        print(f"✅ Model training completed!")
        print(f"📊 Training Accuracy: {train_score:.3f}")
        print(f"📊 Test Accuracy: {test_score:.3f}")
        
        # Feature importance
        feature_importance = list(zip(
            list(self.feature_names) + list(self.extract_advanced_features("").keys()),
            self.classifier.feature_importances_
        ))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        print("\n🔝 Top 10 most important features:")
        for feature, importance in feature_importance[:10]:
            print(f"   {feature}: {importance:.4f}")
        
        return train_score, test_score
    
    def predict(self, text: str) -> Tuple[float, Dict]:
        """Predict phishing probability with detailed explanation"""
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making predictions")
        
        # Extract features
        advanced_features = self.extract_advanced_features(text)
        tfidf_features = self.vectorizer.transform([text])
        
        # Combine features
        advanced_array = np.array([list(advanced_features.values())])
        combined_features = np.hstack([tfidf_features.toarray(), advanced_array])
        
        # Get prediction probability
        probability = self.classifier.predict_proba(combined_features)[0][1]
        
        # Generate comprehensive explanation
        explanation = self._generate_detailed_explanation(text, probability, advanced_features)
        
        return probability, explanation
    
    def _generate_detailed_explanation(self, text: str, probability: float, features: Dict) -> Dict:
        """Generate detailed explanation for the prediction"""
        risk_level = "CRITICAL" if probability > 0.8 else "HIGH" if probability > 0.6 else "MEDIUM" if probability > 0.4 else "LOW"
        
        # Feature-based reasoning
        high_impact_features = []
        if features['urgency_score'] >= 2:
            high_impact_features.append(f"High urgency language ({features['urgency_score']} instances)")
        if features['authority_score'] >= 2:
            high_impact_features.append(f"Authority impersonation ({features['authority_score']} instances)")
        if features['info_request_score'] >= 2:
            high_impact_features.append(f"Personal information requests ({features['info_request_score']} instances)")
        if features['platform_migration_score'] >= 1:
            high_impact_features.append(f"Platform migration attempt ({features['platform_migration_score']} instances)")
        if features['financial_score'] >= 2:
            high_impact_features.append(f"Financial terminology ({features['financial_score']} instances)")
        if features['link_count'] >= 1:
            high_impact_features.append("Contains suspicious links")
        if features['capital_ratio'] > 0.3:
            high_impact_features.append("Excessive capitalization")
        
        # Behavioral pattern detection
        behavioral_patterns = []
        if features['scarcity_score'] > 0:
            behavioral_patterns.append("Scarcity tactics")
        if features['social_proof_score'] > 0:
            behavioral_patterns.append("Social proof manipulation")
        if features['negative_emotion_score'] > features['positive_emotion_score']:
            behavioral_patterns.append("Fear/negative emotion dominance")
        
        return {
            "probability": probability,
            "risk_level": risk_level,
            "risk_score": int(probability * 100),
            "key_indicators": high_impact_features,
            "behavioral_patterns": behavioral_patterns,
            "feature_analysis": features,
            "confidence": min(probability + 0.1, 0.95),  # Confidence based on probability
            "explanation_summary": self._generate_explanation_summary(high_impact_features, behavioral_patterns)
        }
    
    def _generate_explanation_summary(self, indicators: List[str], patterns: List[str]) -> str:
        """Generate human-readable summary"""
        if not indicators and not patterns:
            return "No strong phishing indicators detected"
        
        summary = "Phishing detection based on: "
        elements = indicators + patterns
        summary += ", ".join(elements[:3])  # Show top 3 reasons
        if len(elements) > 3:
            summary += f" and {len(elements) - 3} more indicators"
        
        return summary
    
    def save_model(self, filepath: str):
        """Save trained model"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'classifier': self.classifier,
                'is_trained': self.is_trained,
                'feature_names': self.feature_names
            }, f)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.dump(f)
            self.vectorizer = model_data['vectorizer']
            self.classifier = model_data['classifier']
            self.is_trained = model_data['is_trained']
            self.feature_names = model_data['feature_names']
        print(f"✅ Model loaded from {filepath}")