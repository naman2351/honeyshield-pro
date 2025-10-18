import sqlite3
import os
from src.database import DatabaseManager

def initialize_database():
    """Initialize the database with required tables"""
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    print("🔧 Initializing database...")
    
    # Initialize using your DatabaseManager
    db = DatabaseManager()
    
    # Test the connection
    conn = sqlite3.connect('data/honeyshield.db')
    cursor = conn.cursor()
    
    # Check if tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("✅ Database initialized successfully!")
    print("📊 Tables created:")
    for table in tables:
        print(f"   - {table[0]}")
    
    conn.close()

if __name__ == "__main__":
    initialize_database()