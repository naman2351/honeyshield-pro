#!/usr/bin/env python3
"""
Quick ML Model Fix - Creates a working dummy model
"""

import pickle
import os

def create_working_model():
    """Create a working ML model structure"""
    print("🔧 Creating working ML model...")
    
    os.makedirs('models', exist_ok=True)
    
    # Create a proper model structure
    working_model = {
        'vectorizer': None,  # Will be set during training
        'classifier': None,   # Will be set during training  
        'is_trained': False,
        'feature_names': []
    }
    
    with open('models/advanced_phishing_detector.pkl', 'wb') as f:
        pickle.dump(working_model, f)
    
    print("✅ Working ML model structure created!")
    print("💡 Now you can run: python train_advanced_model.py")

if __name__ == "__main__":
    create_working_model()