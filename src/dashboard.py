import streamlit as st
import sqlite3
import os
from datetime import datetime
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class HoneyshieldDashboard:
    def __init__(self):
        self.setup_page()
        self.ensure_database_exists()
    
    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Honeyshield Dashboard",
            page_icon="🛡️",
            layout="wide"
        )
    
    def ensure_database_exists(self):
        """Ensure database file and tables exist"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Test database connection
            conn = sqlite3.connect('data/honeyshield.db')
            cursor = conn.cursor()
            
            # Check if messages table exists, create if not
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
            
        except Exception as e:
            st.error(f"Database error: {e}")
    
    def get_threat_stats(self):
        """Get threat statistics from database"""
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_messages,
                    SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END) as high_risk,
                    SUM(CASE WHEN risk_level = 'Medium' THEN 1 ELSE 0 END) as medium_risk,
                    COUNT(DISTINCT sender_profile_url) as unique_senders
                FROM messages
            ''')
            
            stats = cursor.fetchone()
            conn.close()
            
            # If no messages yet, return zeros
            if stats[0] is None:
                return (0, 0, 0, 0)
            return stats
            
        except Exception as e:
            st.error(f"Error getting stats: {e}")
            return (0, 0, 0, 0)
    
    def display_header(self):
        """Display dashboard header"""
        st.title("🛡️ Honeyshield - Honey Trap Detection")
        st.markdown("---")
    
    def display_overview_metrics(self):
        """Display overview metrics"""
        st.header("Overview Metrics")
        
        stats = self.get_threat_stats()
        if stats:
            total_messages, high_risk, medium_risk, unique_senders = stats
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Messages", total_messages)
            with col2:
                st.metric("High Risk", high_risk)
            with col3:
                st.metric("Medium Risk", medium_risk)
            with col4:
                st.metric("Unique Senders", unique_senders)
        else:
            st.info("No data available yet. Run the monitor to collect messages.")
    
    def display_recent_messages(self):
        """Display recent messages table"""
        st.header("Recent Messages")
        
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, sender_name, message_content, risk_level, risk_score, keywords_found
                FROM messages 
                ORDER BY timestamp DESC 
                LIMIT 20
            ''')
            
            messages = cursor.fetchall()
            conn.close()
            
            if messages:
                # Display as a simple table
                for msg in messages:
                    timestamp, sender, content, risk_level, risk_score, keywords = msg
                    
                    # Color code based on risk
                    if risk_level == "High":
                        risk_color = "🔴"
                        risk_style = "color: red; font-weight: bold"
                    elif risk_level == "Medium":
                        risk_color = "🟠"
                        risk_style = "color: orange"
                    else:
                        risk_color = "🟢"
                        risk_style = "color: green"
                    
                    with st.expander(f"{risk_color} {sender} - {risk_level} (Score: {risk_score}) - {timestamp}"):
                        st.write(f"**Message:** {content}")
                        st.write(f"**Keywords:** {keywords}")
            else:
                st.info("No messages found in database. Run the monitor to collect data.")
                
        except Exception as e:
            st.error(f"Error loading messages: {e}")
    
    def display_risk_distribution(self):
        """Display risk distribution as text"""
        st.header("Risk Distribution")
        
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT risk_level, COUNT(*) as count
                FROM messages 
                GROUP BY risk_level
            ''')
            
            distribution = cursor.fetchall()
            conn.close()
            
            if distribution:
                for risk_level, count in distribution:
                    if risk_level == "High":
                        st.error(f"**{risk_level} Risk:** {count} messages")
                    elif risk_level == "Medium":
                        st.warning(f"**{risk_level} Risk:** {count} messages")
                    else:
                        st.success(f"**{risk_level} Risk:** {count} messages")
            else:
                st.info("No risk data available. Run the monitor to collect data.")
                
        except Exception as e:
            st.error(f"Error loading risk distribution: {e}")
    
    def display_high_risk_alerts(self):
        """Display high-risk alerts"""
        st.header("🚨 High Risk Alerts")
        
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, sender_name, sender_profile_url, message_content, risk_score, keywords_found, analysis_notes
                FROM messages 
                WHERE risk_level = 'High' 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            
            high_risk_alerts = cursor.fetchall()
            conn.close()
            
            if high_risk_alerts:
                for alert in high_risk_alerts:
                    timestamp, sender, profile_url, content, score, keywords, notes = alert
                    
                    st.error(f"**🚨 HIGH RISK ALERT - {sender}**")
                    st.write(f"**Time:** {timestamp}")
                    st.write(f"**Risk Score:** {score}")
                    st.write(f"**Message:** {content}")
                    st.write(f"**Keywords:** {keywords}")
                    st.write(f"**Analysis:** {notes}")
                    st.write(f"**Profile:** {profile_url}")
                    st.markdown("---")
            else:
                st.success("No high-risk alerts! 🎉")
                
        except Exception as e:
            st.error(f"Error loading high-risk alerts: {e}")
    
    def run(self):
        """Run the dashboard"""
        self.display_header()
        self.display_overview_metrics()
        
        tab1, tab2, tab3 = st.tabs(["Recent Messages", "Risk Overview", "High Risk Alerts"])
        
        with tab1:
            self.display_recent_messages()
        
        with tab2:
            self.display_risk_distribution()
        
        with tab3:
            self.display_high_risk_alerts()

# Main execution
if __name__ == "__main__":
    dashboard = HoneyshieldDashboard()
    dashboard.run()