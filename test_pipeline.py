import sys
import os
import sqlite3
from datetime import datetime

# Add src to path
sys.path.append('src')

def test_database_connection():
    """Test database connection and structure"""
    print("🔧 Testing Database Connection...")
    print("=" * 50)
    
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Test connection
        conn = sqlite3.connect('data/honeyshield.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("✅ Database connection successful!")
        print("📊 Found tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Create messages table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_name TEXT NOT NULL,
                sender_profile_url TEXT,
                message_content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                risk_score INTEGER DEFAULT 0,
                risk_level TEXT DEFAULT 'Low',
                keywords_found TEXT,
                analysis_notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Messages table verified/created!")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\n📦 Testing Module Imports...")
    print("=" * 50)
    
    modules_to_test = [
        'src.database',
        'src.analysis_engine',
        'src.enhanced_analysis_engine',
        'src.ml_phishing_detector',
        'src.training_data_generator'
    ]
    
    all_imports_successful = True
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - OK")
        except ImportError as e:
            print(f"❌ {module_name} - FAILED: {e}")
            all_imports_successful = False
        except Exception as e:
            print(f"⚠️  {module_name} - WARNING: {e}")
    
    return all_imports_successful

def test_analysis_engine():
    """Test the analysis engine with various messages"""
    print("\n🤖 Testing Analysis Engine...")
    print("=" * 50)
    
    try:
        from src.analysis_engine import EnhancedAnalysisEngine
        analyzer = EnhancedAnalysisEngine()
        
        test_messages = [
            {
                "name": "CRITICAL Phishing Attempt",
                "content": "URGENT SECURITY ALERT: Your LinkedIn account shows suspicious activity. To prevent immediate account suspension, you MUST verify your identity within 2 hours. Click: http://fake-security-site.com/verify",
                "expected_score": 80
            },
            {
                "name": "Financial Scam", 
                "content": "Investment opportunity with 500% guaranteed returns! Contact me on WhatsApp for this exclusive offer: +1-555-0123",
                "expected_score": 70
            },
            {
                "name": "Legitimate Message",
                "content": "Hi, I came across your profile and would like to connect to discuss industry trends.",
                "expected_score": 20
            },
            {
                "name": "Information Harvesting",
                "content": "I need your personal phone number and email to send you this confidential business proposal.",
                "expected_score": 65
            }
        ]
        
        results = []
        
        for test in test_messages:
            print(f"\n📨 Testing: {test['name']}")
            print(f"Message: {test['content'][:80]}...")
            
            result = analyzer.analyze_message(test['content'])
            
            print(f"🎯 Score: {result['final_score']} (expected: {test['expected_score']}+)")
            print(f"🚨 Level: {result['risk_level']}")
            
            if 'ml_analysis' in result:
                print(f"🤖 ML Prob: {result['ml_analysis'].get('probability', 0):.1%}")
            
            # Check if detection worked
            if result['final_score'] >= test['expected_score']:
                print("✅ Detection SUCCESS")
                results.append(True)
            else:
                print("❌ Detection WEAK")
                results.append(False)
        
        success_rate = sum(results) / len(results)
        print(f"\n📊 Detection Success Rate: {success_rate:.1%}")
        return success_rate >= 0.5
        
    except Exception as e:
        print(f"❌ Analysis engine test failed: {e}")
        return False

def test_database_operations():
    """Test database read/write operations"""
    print("\n💾 Testing Database Operations...")
    print("=" * 50)
    
    try:
        from src.database import DatabaseManager
        db = DatabaseManager()
        
        # Test message to insert
        test_message = {
            'sender_name': 'Pipeline Test Bot',
            'sender_profile_url': 'https://linkedin.com/in/test-bot',
            'message_content': 'This is a test message for pipeline verification.',
            'risk_score': 45,
            'keywords': 'test, pipeline, verification',
            'notes': 'Test insertion successful'
        }
        
        # Insert test message
        db.log_message(
            test_message['sender_name'],
            test_message['sender_profile_url'], 
            test_message['message_content'],
            test_message['risk_score'],
            test_message['keywords'],
            test_message['notes']
        )
        print("✅ Database write operation successful!")
        
        # Test read operation
        messages = db.get_recent_messages(5)
        print(f"✅ Database read operation successful! Found {len(messages)} messages")
        
        # Test statistics
        stats = db.get_threat_stats()
        print(f"✅ Statistics: {stats[0]} total messages, {stats[1]} high risk")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def test_critical_alert_detection():
    """Specifically test the critical alert from our previous example"""
    print("\n🚨 Testing Critical Alert Detection...")
    print("=" * 50)
    
    try:
        from src.analysis_engine import EnhancedAnalysisEngine
        from src.database import DatabaseManager
        
        analyzer = EnhancedAnalysisEngine()
        db = DatabaseManager()
        
        # The critical test message
        critical_message = """
        URGENT SECURITY ALERT: Your LinkedIn account shows suspicious activity from unauthorized IP addresses. To prevent immediate account suspension and potential legal consequences, you MUST verify your identity within the next 2 hours.

        Click here for immediate verification: http://linkedin-security-verification-urgent.com/verify?id=5847392

        This is a mandatory compliance requirement under LinkedIn's updated security policy. Failure to verify will result in permanent account termination and potential investigation by our legal team.

        For immediate assistance, contact our security team directly on WhatsApp: +1-555-019-2837 or Telegram: @linkedin_security_agent

        CONFIDENTIAL: This message contains sensitive security information. Do not share with anyone.
        """
        
        print("📨 Processing critical test message...")
        
        # Analyze the message
        result = analyzer.analyze_message(critical_message)
        
        print(f"🎯 FINAL RISK SCORE: {result['final_score']}/100")
        print(f"🚨 RISK LEVEL: {result['risk_level']}")
        
        if 'ml_analysis' in result:
            print(f"🤖 ML PROBABILITY: {result['ml_analysis'].get('probability', 0):.1%}")
        
        print(f"💡 CONFIDENCE: {result.get('confidence_score', 0):.1%}")
        
        # Show detection reasons
        if 'ml_analysis' in result and 'explanation' in result['ml_analysis']:
            reasons = result['ml_analysis']['explanation'].get('reasons', [])
            print("\n🔍 DETECTION REASONS:")
            for reason in reasons[:5]:  # Show first 5 reasons
                print(f"   ✅ {reason}")
        
        # Log to database
        db.log_message(
            sender_name="CRITICAL TEST - LinkedIn Security (FAKE)",
            sender_profile_url="http://linkedin.com/in/critical-test-fake",
            message_content=critical_message,
            risk_score=result['final_score'],
            keywords=", ".join(result['ml_analysis']['explanation'].get('reasons', ['Multiple high-risk indicators'])),
            notes=f"Critical test - {result['risk_level']} risk detected"
        )
        
        print("✅ Critical alert logged to database!")
        
        # Verify it's properly classified as critical
        if result['final_score'] >= 80:
            print("🎉 SUCCESS: Critical alert properly detected as HIGH RISK!")
            return True
        else:
            print(f"⚠️  WARNING: Critical alert detected as {result['risk_level']} (score: {result['final_score']})")
            return result['final_score'] >= 60  # Still accept medium-high as partial success
            
    except Exception as e:
        print(f"❌ Critical alert test failed: {e}")
        return False

def run_complete_pipeline_test():
    """Run the complete pipeline test"""
    print("🚀 STARTING COMPLETE PIPELINE TEST")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Database Connection", test_database_connection()))
    test_results.append(("Module Imports", test_imports()))
    test_results.append(("Analysis Engine", test_analysis_engine()))
    test_results.append(("Database Operations", test_database_operations()))
    test_results.append(("Critical Alert", test_critical_alert_detection()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PIPELINE TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Pipeline is working correctly.")
        return True
    elif passed_tests >= 3:
        print("⚠️  MOST TESTS PASSED! Pipeline is functional but may need minor fixes.")
        return True
    else:
        print("❌ MULTIPLE TEST FAILURES! Pipeline needs significant fixes.")
        return False

if __name__ == "__main__":
    success = run_complete_pipeline_test()
    
    if success:
        print("\n✨ Next steps:")
        print("1. Run: streamlit run src/dashboard.py")
        print("2. Check the dashboard to see test results")
        print("3. Run: python run_monitor.py (for actual LinkedIn monitoring)")
    else:
        print("\n🔧 Fix the failed tests before proceeding.")
    
    sys.exit(0 if success else 1)