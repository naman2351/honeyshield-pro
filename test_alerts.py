import sqlite3
from src.analysis_engine import AnalysisEngine
from src.database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)

def test_alert_system():
    """Test the alert system with suspicious messages"""
    
    analysis_engine = AnalysisEngine()
    db = DatabaseManager()
    
    # Test messages with different risk levels
    test_messages = [
        # High risk messages
        ("Hi, I have a confidential government contract opportunity. Can we move to WhatsApp? I need your personal number urgently.", "High Risk Test 1"),
        ("This is a sensitive military project. I need to meet you immediately to discuss classified information.", "High Risk Test 2"),
        
        # Medium risk messages
        ("I have a great business proposal for you. Let's connect on Telegram for more details.", "Medium Risk Test 1"),
        ("Investment opportunity that requires immediate attention. Can we talk privately?", "Medium Risk Test 2"),
        
        # Low risk messages
        ("Hi, how are you doing today?", "Low Risk Test 1"),
        ("Nice to connect with you on LinkedIn!", "Low Risk Test 2")
    ]
    
    print("🚀 Testing Alert System...")
    print("=" * 50)
    
    for message_content, test_name in test_messages:
        print(f"\n📨 Testing: {test_name}")
        print(f"Message: {message_content}")
        
        # Analyze the message
        analysis_result = analysis_engine.calculate_risk_score(message_content)
        mitre_techniques = analysis_engine.map_to_mitre(analysis_result)
        
        print(f"🔍 Risk Score: {analysis_result['risk_score']}")
        print(f"📊 Risk Level: {'High' if analysis_result['risk_score'] >= 70 else 'Medium' if analysis_result['risk_score'] >= 40 else 'Low'}")
        print(f"🔑 Keywords Found: {analysis_result['keywords']}")
        print(f"📝 Analysis Notes: {analysis_result['analysis_notes']}")
        print(f"🎯 MITRE Techniques: {mitre_techniques}")
        
        # Log to database
        db.log_message(
            sender_name=test_name,
            sender_profile_url=f"https://linkedin.com/in/test-{test_name.replace(' ', '-')}",
            message_content=message_content,
            risk_score=analysis_result['risk_score'],
            keywords=analysis_result['keywords'],
            notes=f"{analysis_result['analysis_notes']}; MITRE: {mitre_techniques}"
        )
        
        print("✅ Logged to database")
        print("-" * 50)

if __name__ == "__main__":
    test_alert_system()
    print("\n🎉 Test completed! Now run the dashboard to see the results:")
    print("streamlit run src/dashboard.py")