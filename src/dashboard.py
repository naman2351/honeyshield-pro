import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class AlertDashboard:
    def __init__(self):
        self.setup_page()
        self.ensure_database_exists()
    
    def setup_page(self):
        """Configure Streamlit page for security operations"""
        st.set_page_config(
            page_title="Honeyshield Security Dashboard",
            page_icon="🛡️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Security-focused CSS
        st.markdown("""
        <style>
        .critical-alert {
            background: linear-gradient(45deg, #ff4444, #cc0000);
            padding: 15px;
            border-radius: 8px;
            color: white;
            border-left: 5px solid #ff0000;
            margin: 10px 0px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .critical-alert:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(255, 0, 0, 0.3);
        }
        .high-alert {
            background: linear-gradient(45deg, #ff6b6b, #ff4444);
            padding: 12px;
            border-radius: 8px;
            color: white;
            border-left: 5px solid #ff4444;
            margin: 8px 0px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .high-alert:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
        }
        .medium-alert {
            background: linear-gradient(45deg, #ffa726, #ff9800);
            padding: 10px;
            border-radius: 8px;
            color: white;
            border-left: 5px solid #ff9800;
            margin: 6px 0px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .medium-alert:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(255, 167, 38, 0.3);
        }
        .low-alert {
            background: linear-gradient(45deg, #4caf50, #388e3c);
            padding: 8px;
            border-radius: 8px;
            color: white;
            border-left: 5px solid #388e3c;
            margin: 4px 0px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .low-alert:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
        }
        .alert-details {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #e9ecef;
            margin: 10px 0px;
        }
        .security-metric {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #dee2e6;
        }
        .resolved-alert {
            background-color: #d4edda;
            padding: 10px;
            border-radius: 8px;
            border-left: 5px solid #28a745;
            margin: 5px 0px;
            color: #155724;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def ensure_database_exists(self):
        """Ensure database file and tables exist with alert-focused schema"""
        try:
            os.makedirs('data', exist_ok=True)
            conn = sqlite3.connect('data/honeyshield.db')
            cursor = conn.cursor()
            
            # Enhanced alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    severity TEXT NOT NULL,
                    status TEXT DEFAULT 'OPEN',
                    source_platform TEXT,
                    sender_name TEXT,
                    sender_profile TEXT,
                    message_content TEXT,
                    risk_score INTEGER,
                    threat_type TEXT,
                    indicators TEXT,
                    recommended_action TEXT,
                    analyst_notes TEXT,
                    ml_confidence REAL,
                    resolved_at DATETIME
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Database initialization error: {e}")
    
    def get_security_overview(self):
        """Get security overview statistics"""
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_alerts,
                    SUM(CASE WHEN severity = 'CRITICAL' AND status = 'OPEN' THEN 1 ELSE 0 END) as open_critical,
                    SUM(CASE WHEN severity = 'HIGH' AND status = 'OPEN' THEN 1 ELSE 0 END) as open_high,
                    SUM(CASE WHEN severity = 'MEDIUM' AND status = 'OPEN' THEN 1 ELSE 0 END) as open_medium,
                    SUM(CASE WHEN status = 'RESOLVED' THEN 1 ELSE 0 END) as resolved,
                    MAX(timestamp) as latest_alert
                FROM security_alerts
            ''')
            
            stats = cursor.fetchone()
            conn.close()
            
            return {
                'total_alerts': stats[0] or 0,
                'open_critical': stats[1] or 0,
                'open_high': stats[2] or 0,
                'open_medium': stats[3] or 0,
                'resolved_alerts': stats[4] or 0,
                'latest_alert': stats[5] or 'No alerts'
            }
            
        except Exception as e:
            st.error(f"Error getting security overview: {e}")
            return None
    
    def display_security_header(self):
        """Display security operations header"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.title("🛡️ Honeyshield Security Operations")
            st.markdown("**Real-time Social Engineering Threat Detection & Response**")
        
        with col2:
            st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))
        
        st.markdown("---")
    
    def display_security_metrics(self, overview):
        """Display security operations metrics"""
        st.header("📊 Security Overview")
        
        if not overview:
            st.info("No security data available. Alerts will appear here when detected.")
            return
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Open Critical", 
                overview['open_critical'],
                delta=None,
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "Open High", 
                overview['open_high'],
                delta=None,
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "Total Alerts", 
                overview['total_alerts']
            )
        
        with col4:
            st.metric(
                "Resolved", 
                overview['resolved_alerts']
            )
        
        with col5:
            st.metric(
                "Latest Alert", 
                overview['latest_alert'][:16] if overview['latest_alert'] != 'No alerts' else 'No alerts'
            )
    
    def display_active_alerts_section(self):
        """Display active security alerts with clickable interface"""
        st.header("🚨 Active Security Alerts")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            show_severity = st.selectbox(
                "Filter by Severity",
                ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
            )
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Newest First", "Highest Risk", "Oldest First"]
            )
        with col3:
            if st.button("🔄 Refresh Alerts", use_container_width=True):
                st.rerun()
        
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            
            # Build query based on filters
            query = '''
                SELECT 
                    alert_id, timestamp, severity, status, source_platform,
                    sender_name, sender_profile, message_content, risk_score,
                    threat_type, indicators, recommended_action, ml_confidence
                FROM security_alerts 
                WHERE status = 'OPEN'
            '''
            
            params = []
            
            if show_severity != "ALL":
                query += ' AND severity = ?'
                params.append(show_severity)
            
            # Add sorting
            if sort_by == "Newest First":
                query += ' ORDER BY timestamp DESC'
            elif sort_by == "Highest Risk":
                query += ' ORDER BY risk_score DESC'
            else:
                query += ' ORDER BY timestamp ASC'
            
            query += ' LIMIT 50'
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            if df.empty:
                st.success("🎉 No active security alerts! All systems secure.")
                return
            
            # Display each alert as clickable card
            for _, alert in df.iterrows():
                self._display_clickable_alert_card(alert)
                
        except Exception as e:
            st.error(f"Error loading alerts: {e}")
    
    def _display_clickable_alert_card(self, alert):
        """Display individual security alert as clickable card"""
        severity_config = {
            'CRITICAL': {'class': 'critical-alert', 'emoji': '🚨', 'color': '#ff4444'},
            'HIGH': {'class': 'high-alert', 'emoji': '⚠️', 'color': '#ff6b6b'},
            'MEDIUM': {'class': 'medium-alert', 'emoji': '🔍', 'color': '#ffa726'},
            'LOW': {'class': 'low-alert', 'emoji': 'ℹ️', 'color': '#4caf50'}
        }
        
        config = severity_config.get(alert['severity'], severity_config['MEDIUM'])
        
        # Create a unique key for this alert
        alert_key = f"alert_{alert['alert_id']}"
        
        # Check if this alert is expanded
        is_expanded = st.session_state.get(alert_key, False)
        
        # Alert Header (Clickable)
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            if st.button(
                f"{config['emoji']} **ALERT {alert['alert_id']}** | "
                f"Severity: **{alert['severity']}** | "
                f"Score: **{alert['risk_score']}/100**",
                key=f"btn_{alert_key}",
                use_container_width=True
            ):
                # Toggle expansion state
                st.session_state[alert_key] = not is_expanded
                st.rerun()
        
        with col2:
            st.write(f"**Time:** {alert['timestamp'][:16]}")
            st.write(f"**Source:** {alert['source_platform']}")
        
        with col3:
            if st.button("✅ Resolve", key=f"resolve_{alert_key}"):
                self._resolve_alert(alert['alert_id'])
                st.rerun()
        
        # Alert Details (Expanded View)
        if st.session_state.get(alert_key, False):
            with st.container():
                st.markdown('<div class="alert-details">', unsafe_allow_html=True)
                
                st.subheader("🔍 Alert Details")
                
                # Main alert information in columns
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.write("**Threat Information**")
                    st.write(f"**Sender:** {alert['sender_name']}")
                    if alert['sender_profile']:
                        st.write(f"**Profile:** {alert['sender_profile']}")
                    st.write(f"**Threat Type:** {alert['threat_type']}")
                    if alert['ml_confidence']:
                        st.write(f"**ML Confidence:** {alert['ml_confidence']:.1%}")
                    st.write(f"**Detection Time:** {alert['timestamp']}")
                
                with col_b:
                    st.write("**Detection Analysis**")
                    if alert['indicators'] and alert['indicators'] != 'None':
                        st.write("**Key Indicators:**")
                        indicators = alert['indicators'].split(', ')
                        for indicator in indicators:
                            st.write(f"• {indicator}")
                
                # Message Content
                st.write("**Message Content:**")
                st.info(alert['message_content'])
                
                # Recommended Action
                st.write("**Recommended Action:**")
                if alert['severity'] in ['CRITICAL', 'HIGH']:
                    st.error(alert['recommended_action'])
                else:
                    st.warning(alert['recommended_action'])
                
                # Action Buttons
                col_x, col_y, col_z = st.columns(3)
                with col_x:
                    if st.button("📋 Copy Alert Details", key=f"copy_{alert_key}"):
                        self._copy_alert_details(alert)
                with col_y:
                    if st.button("📧 Export Alert", key=f"export_{alert_key}"):
                        self._export_single_alert(alert)
                with col_z:
                    if st.button("❌ Close Details", key=f"close_{alert_key}"):
                        st.session_state[alert_key] = False
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
    
    def display_recently_resolved(self):
        """Display recently resolved alerts"""
        st.header("✅ Recently Resolved Alerts")
        
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            
            query = '''
                SELECT 
                    alert_id, timestamp, severity, sender_name, 
                    threat_type, risk_score, resolved_at
                FROM security_alerts 
                WHERE status = 'RESOLVED'
                ORDER BY resolved_at DESC
                LIMIT 10
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                st.info("No resolved alerts yet.")
                return
            
            for _, alert in df.iterrows():
                st.markdown(f'''
                <div class="resolved-alert">
                    🔒 <strong>{alert['alert_id']}</strong> | {alert['severity']} | 
                    {alert['sender_name']} | Resolved: {alert['resolved_at'][:16]}
                </div>
                ''', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error loading resolved alerts: {e}")
    
    def display_alert_actions(self):
        """Display alert management actions"""
        st.header("🔧 Alert Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh All Data", use_container_width=True):
                st.rerun()
            
            if st.button("📋 Export All Alerts", use_container_width=True):
                self._export_alert_report()
        
        with col2:
            if st.button("🚨 Test Alert System", use_container_width=True):
                self._test_alert_system()
            
            if st.button("🗑️ Clear Resolved Alerts", use_container_width=True):
                self._clear_resolved_alerts()
        
        with col3:
            if st.button("📊 System Status", use_container_width=True):
                self._show_system_status()
    
    def _resolve_alert(self, alert_id):
        """Mark an alert as resolved"""
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE security_alerts 
                SET status = 'RESOLVED', resolved_at = CURRENT_TIMESTAMP
                WHERE alert_id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
            st.success(f"Alert {alert_id} marked as resolved")
            
        except Exception as e:
            st.error(f"Error resolving alert: {e}")
    
    def _copy_alert_details(self, alert):
        """Copy alert details to clipboard"""
        alert_text = f"""
Alert ID: {alert['alert_id']}
Severity: {alert['severity']}
Risk Score: {alert['risk_score']}/100
Time: {alert['timestamp']}
Sender: {alert['sender_name']}
Threat Type: {alert['threat_type']}
Message: {alert['message_content']}
Recommended Action: {alert['recommended_action']}
        """
        st.code(alert_text, language='text')
        st.success("Alert details copied to clipboard (select and copy the text above)")
    
    def _export_single_alert(self, alert):
        """Export single alert as text file"""
        alert_text = f"""
HONEYSHIELD SECURITY ALERT REPORT
=================================

ALERT ID: {alert['alert_id']}
SEVERITY: {alert['severity']}
RISK SCORE: {alert['risk_score']}/100
TIMESTAMP: {alert['timestamp']}
STATUS: {alert['status']}

THREAT INFORMATION:
- Source Platform: {alert['source_platform']}
- Sender: {alert['sender_name']}
- Sender Profile: {alert['sender_profile']}
- Threat Type: {alert['threat_type']}
- ML Confidence: {alert['ml_confidence']:.1% if alert['ml_confidence'] else 'N/A'}

MESSAGE CONTENT:
{alert['message_content']}

DETECTION INDICATORS:
{alert['indicators']}

RECOMMENDED ACTION:
{alert['recommended_action']}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        st.download_button(
            label="📥 Download This Alert",
            data=alert_text,
            file_name=f"alert_{alert['alert_id']}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    
    def _export_alert_report(self):
        """Export all alerts as CSV report"""
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            
            query = '''
                SELECT 
                    alert_id, timestamp, severity, status, source_platform,
                    sender_name, threat_type, risk_score, ml_confidence
                FROM security_alerts 
                ORDER BY timestamp DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download All Alerts (CSV)",
                data=csv,
                file_name=f"honeyshield_alerts_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"Export failed: {e}")
    
    def _test_alert_system(self):
        """Test the alert system with a sample alert"""
        try:
            from src.alert_manager import AlertManager
            alert_mgr = AlertManager()
            
            test_alert = {
                'severity': 'HIGH',
                'source_platform': 'LinkedIn',
                'sender_name': 'TEST - Security System',
                'sender_profile': 'https://linkedin.com/in/test-system',
                'message_content': 'TEST ALERT: This is a test of the Honeyshield alert system. Everything is working correctly!',
                'risk_score': 75,
                'threat_type': 'System Test',
                'indicators': 'Test indicator 1, Test indicator 2',
                'recommended_action': 'This is a test alert. No action required.',
                'ml_confidence': 0.95
            }
            
            alert_mgr.create_alert(test_alert)
            st.success("✅ Test alert created successfully! Check the Active Alerts section.")
            st.rerun()
            
        except Exception as e:
            st.error(f"Test failed: {e}")
    
    def _clear_resolved_alerts(self):
        """Clear all resolved alerts from database"""
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM security_alerts WHERE status = 'RESOLVED'")
            conn.commit()
            conn.close()
            
            st.success("✅ All resolved alerts have been cleared")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error clearing resolved alerts: {e}")
    
    def _show_system_status(self):
        """Show system status information"""
        st.info("""
        **System Status Overview:**
        
        ✅ **Dashboard**: Operational
        ✅ **Database**: Connected
        ✅ **Alert System**: Active
        🔄 **Real-time Monitoring**: Ready
        
        **Last Check:** {}
        **Total Alerts Processed:** {}
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.get_security_overview()['total_alerts']))
    
    def run(self):
        """Run the security dashboard"""
        # Initialize session state for expanded alerts
        if 'alert_states' not in st.session_state:
            st.session_state.alert_states = {}
        
        # Sidebar
        with st.sidebar:
            st.title("🛡️ Security Console")
            st.markdown("---")
            
            st.markdown("### Quick Stats")
            overview = self.get_security_overview()
            if overview:
                st.metric("Open Critical", overview['open_critical'])
                st.metric("Open High", overview['open_high'])
                st.metric("Total Alerts", overview['total_alerts'])
            
            st.markdown("---")
            st.markdown("### Navigation")
            page = st.radio("Go to:", ["Active Alerts", "Resolved Alerts", "Management"])
            
            st.markdown("---")
            st.markdown("**Last Updated**")
            st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Main content based on navigation
        self.display_security_header()
        self.display_security_metrics(overview)
        
        if page == "Active Alerts":
            self.display_active_alerts_section()
        elif page == "Resolved Alerts":
            self.display_recently_resolved()
        elif page == "Management":
            self.display_alert_actions()

# Main execution
if __name__ == "__main__":
    dashboard = AlertDashboard()
    dashboard.run()