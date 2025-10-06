import streamlit as st
import sqlite3
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class HoneyshieldDashboard:
    def __init__(self):
        self.setup_page()
    
    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Honeyshield Dashboard",
            page_icon="🛡️",
            layout="wide"
        )
    
    def display_header(self):
        """Display dashboard header"""
        st.title("🛡️ Honeyshield - Honey Trap Detection")
        st.markdown("---")
    
    def get_threat_stats(self):
        """Get threat statistics from database"""
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
        return stats
    
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
    
    def display_recent_messages(self):
        """Display recent messages table"""
        st.header("Recent Messages")
        
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
                elif risk_level == "Medium":
                    risk_color = "🟠"
                else:
                    risk_color = "🟢"
                
                with st.expander(f"{risk_color} {sender} - {risk_level} (Score: {risk_score}) - {timestamp}"):
                    st.write(f"**Message:** {content}")
                    st.write(f"**Keywords:** {keywords}")
        else:
            st.info("No messages found in database.")
    
    def display_risk_distribution(self):
        """Display risk distribution as text"""
        st.header("Risk Distribution")
        
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
            st.info("No risk data available.")
    
    def display_high_risk_alerts(self):
        """Display high-risk alerts"""
        st.header("🚨 High Risk Alerts")
        
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