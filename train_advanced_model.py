#!/usr/bin/env python3
"""
Advanced Model Training Script
Trains the ML-first phishing detection model with comprehensive features
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Add src to path
sys.path.append('src')

from src.ml_phishing_detector import MLPhishingDetector
from src.advanced_training_generator import AdvancedTrainingGenerator

def train_advanced_model(dataset_size: int = 5000, test_size: float = 0.2, save_path: str = "models/advanced_phishing_detector.pkl"):
    """Train the advanced ML phishing detection model"""
    
    print("🚀 Starting Advanced ML Model Training")
    print("=" * 60)
    
    # Create directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Generate training data
    print("📊 Generating advanced training dataset...")
    generator = AdvancedTrainingGenerator()
    dataset = generator.generate_dataset(dataset_size)
    generator.save_dataset(dataset)
    
    # Prepare training data
    texts = [item['text'] for item in dataset]
    labels = [item['label'] for item in dataset]
    
    print(f"📈 Dataset: {len(texts)} samples ({sum(labels)} phishing, {len(labels)-sum(labels)} legitimate)")
    
    # Initialize and train model
    print("🤖 Training advanced ML detector...")
    detector = MLPhishingDetector()
    
    train_score, test_score = detector.train(texts, labels, test_size=test_size)
    
    # Save model
    detector.save_model(save_path)
    
    # Test with critical examples
    print("\n🧪 Model Validation with Critical Examples:")
    print("-" * 50)
    
    critical_examples = [
        "URGENT: Your account will be suspended in 2 hours. Click here to verify: http://security-verify-now.com",
        "Investment opportunity with 500% returns! Contact me on WhatsApp: +1234567890",
        "Official LinkedIn security: We detected suspicious activity. Verify now: http://linkedin-security-portal.com",
        "Hi, I'd like to connect and discuss potential collaboration opportunities in tech."
    ]
    
    for example in critical_examples:
        try:
            prob, explanation = detector.predict(example)
            risk_status = "🔴 PHISHING" if prob > 0.7 else "🟡 SUSPICIOUS" if prob > 0.4 else "🟢 LEGITIMATE"
            print(f"{risk_status} ({prob:.1%}): {example[:60]}...")
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
    
    print(f"\n✅ Advanced model training completed!")
    print(f"💾 Model saved to: {save_path}")
    print(f"📊 Final Test Accuracy: {test_score:.3f}")
    
    return detector, test_score

def main():
    parser = argparse.ArgumentParser(description='Train advanced phishing detection model')
    parser.add_argument('--size', type=int, default=5000, help='Training dataset size')
    parser.add_argument('--test-size', type=float, default=0.2, help='Test set proportion')
    parser.add_argument('--output', type=str, default='models/advanced_phishing_detector.pkl', help='Output model path')
    
    args = parser.parse_args()
    
    try:
        detector, accuracy = train_advanced_model(
            dataset_size=args.size,
            test_size=args.test_size,
            save_path=args.output
        )
        
        # Exit with success code
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()