import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database import DatabaseManager

class HoneyshieldDashboard:
    def __init__(self):
        self.db = DatabaseManager()
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
    
    def display_overview_metrics(self):
        """Display overview metrics"""
        st.header("Overview Metrics")
        
        stats = self.db.get_threat_stats()
        if stats:
            total_messages, high_risk, medium_risk, unique_senders = stats
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Messages", total_messages)
            with col2:
                st.metric("High Risk", high_risk, delta=None)
            with col3:
                st.metric("Medium Risk", medium_risk, delta=None)
            with col4:
                st.metric("Unique Senders", unique_senders)
    
    def display_recent_messages(self):
        """Display recent messages table"""
        st.header("Recent Messages")
        
        messages = self.db.get_recent_messages(limit=20)
        
        if messages:
            # Convert to DataFrame for better display
            df = pd.DataFrame(messages, 
                            columns=['ID', 'Sender', 'Profile URL', 'Message', 'Timestamp', 
                                   'Risk Score', 'Risk Level', 'Keywords', 'Notes'])
            
            # Style the DataFrame
            def color_risk_level(val):
                if val == 'High':
                    return 'color: red; font-weight: bold'
                elif val == 'Medium':
                    return 'color: orange'
                else:
                    return 'color: green'
            
            styled_df = df[['Timestamp', 'Sender', 'Message', 'Risk Level', 'Risk Score', 'Keywords']].style.map(
                color_risk_level, subset=['Risk Level']
            )
            
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No messages found in database.")
    
    def display_threat_analysis(self):
        """Display threat analysis charts"""
        st.header("Threat Analysis")
        
        messages = self.db.get_recent_messages(limit=100)
        
        if messages:
            df = pd.DataFrame(messages, 
                            columns=['ID', 'Sender', 'Profile URL', 'Message', 'Timestamp', 
                                   'Risk Score', 'Risk Level', 'Keywords', 'Notes'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Risk level distribution
                risk_counts = df['Risk Level'].value_counts()
                fig_pie = px.pie(
                    values=risk_counts.values,
                    names=risk_counts.index,
                    title="Risk Level Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Risk scores over time
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                df_sorted = df.sort_values('Timestamp')
                
                fig_line = px.line(
                    df_sorted,
                    x='Timestamp',
                    y='Risk Score',
                    color='Risk Level',
                    title="Risk Scores Over Time",
                    color_discrete_map={
                        'High': 'red',
                        'Medium': 'orange', 
                        'Low': 'green'
                    }
                )
                st.plotly_chart(fig_line, use_container_width=True)
    
    def display_high_risk_alerts(self):
        """Display high-risk alerts"""
        st.header("🚨 High Risk Alerts")
        
        conn = sqlite3.connect('data/honeyshield.db')
        high_risk_messages = pd.read_sql_query(
            "SELECT * FROM messages WHERE risk_level = 'High' ORDER BY timestamp DESC LIMIT 10",
            conn
        )
        conn.close()
        
        if not high_risk_messages.empty:
            for _, alert in high_risk_messages.iterrows():
                with st.expander(f"🚨 {alert['sender_name']} - Score: {alert['risk_score']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Message:** {alert['message_content']}")
                        st.write(f"**Profile:** {alert['sender_profile_url']}")
                    
                    with col2:
                        st.write(f"**Keywords Detected:** {alert['keywords_found']}")
                        st.write(f"**Analysis:** {alert['analysis_notes']}")
                        st.write(f"**Timestamp:** {alert['timestamp']}")
        else:
            st.success("No high-risk alerts! 🎉")
    
    def run(self):
        """Run the dashboard"""
        self.display_header()
        self.display_overview_metrics()
        
        tab1, tab2, tab3 = st.tabs(["Recent Messages", "Threat Analysis", "High Risk Alerts"])
        
        with tab1:
            self.display_recent_messages()
        
        with tab2:
            self.display_threat_analysis()
        
        with tab3:
            self.display_high_risk_alerts()

# Main execution
if __name__ == "__main__":
    dashboard = HoneyshieldDashboard()
    dashboard.run()