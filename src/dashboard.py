import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class MLFirstDashboard:
    def __init__(self):
        self.setup_page()
        self.ensure_database_exists()
    
    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Honeyshield ML Dashboard",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        .critical-alert {
            background-color: #ff4444;
            padding: 10px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
        }
        .high-alert {
            background-color: #ff6b6b;
            padding: 8px;
            border-radius: 5px;
            color: white;
        }
        .medium-alert {
            background-color: #ffa726;
            padding: 6px;
            border-radius: 5px;
            color: white;
        }
        .ml-insight {
            background-color: #e3f2fd;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #2196f3;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def ensure_database_exists(self):
        """Ensure database file and tables exist"""
        try:
            os.makedirs('data', exist_ok=True)
            conn = sqlite3.connect('data/honeyshield.db')
            cursor = conn.cursor()
            
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
                    analysis_notes TEXT,
                    ml_confidence REAL DEFAULT 0.0,
                    threat_types TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Database initialization error: {e}")
    
    def get_advanced_stats(self):
        """Get comprehensive statistics with ML insights"""
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            
            # Basic stats
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_messages,
                    SUM(CASE WHEN risk_level = 'CRITICAL' THEN 1 ELSE 0 END) as critical,
                    SUM(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) as high,
                    SUM(CASE WHEN risk_level = 'MEDIUM' THEN 1 ELSE 0 END) as medium,
                    SUM(CASE WHEN risk_level = 'LOW' THEN 1 ELSE 0 END) as low,
                    AVG(risk_score) as avg_score,
                    AVG(ml_confidence) as avg_confidence
                FROM messages
            ''')
            
            stats = cursor.fetchone()
            
            # Threat type analysis
            cursor.execute('''
                SELECT threat_types, COUNT(*) as count
                FROM messages 
                WHERE threat_types IS NOT NULL AND threat_types != ''
                GROUP BY threat_types
            ''')
            
            threat_data = cursor.fetchall()
            
            # Temporal analysis
            cursor.execute('''
                SELECT 
                    strftime('%H', timestamp) as hour,
                    COUNT(*) as message_count,
                    AVG(risk_score) as avg_risk
                FROM messages 
                GROUP BY hour
                ORDER BY hour
            ''')
            
            temporal_data = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_messages': stats[0] or 0,
                'critical_alerts': stats[1] or 0,
                'high_alerts': stats[2] or 0,
                'medium_alerts': stats[3] or 0,
                'low_alerts': stats[4] or 0,
                'avg_risk_score': stats[5] or 0,
                'avg_confidence': stats[6] or 0,
                'threat_distribution': threat_data,
                'temporal_patterns': temporal_data
            }
            
        except Exception as e:
            st.error(f"Error getting stats: {e}")
            return None
    
    def display_ml_insights_header(self):
        """Display the main header with ML focus"""
        st.title("🤖 Honeyshield ML-First Dashboard")
        st.markdown("""
        **AI-Powered Social Engineering Detection** · Real-time ML Analysis · Behavioral Threat Intelligence
        """)
        st.markdown("---")
    
    def display_ml_metrics(self, stats):
        """Display ML-focused metrics"""
        st.header("🎯 ML Detection Metrics")
        
        if not stats:
            st.info("No data available yet. Run the monitoring system to collect data.")
            return
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Messages", stats['total_messages'])
        
        with col2:
            st.metric("Critical Alerts", stats['critical_alerts'], delta=None)
        
        with col3:
            st.metric("High Confidence", f"{stats['avg_confidence']:.1%}")
        
        with col4:
            st.metric("Avg Risk Score", f"{stats['avg_risk_score']:.1f}")
        
        with col5:
            detection_rate = (stats['critical_alerts'] + stats['high_alerts']) / max(stats['total_messages'], 1)
            st.metric("Threat Detection Rate", f"{detection_rate:.1%}")
    
    def display_risk_distribution_chart(self, stats):
        """Display interactive risk distribution chart"""
        if not stats or stats['total_messages'] == 0:
            return
        
        st.header("📊 Risk Distribution Analysis")
        
        # Risk level distribution
        risk_data = {
            'Level': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
            'Count': [
                stats['critical_alerts'],
                stats['high_alerts'], 
                stats['medium_alerts'],
                stats['low_alerts']
            ],
            'Color': ['#ff4444', '#ff6b6b', '#ffa726', '#4caf50']
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=risk_data['Level'],
                y=risk_data['Count'],
                marker_color=risk_data['Color'],
                text=risk_data['Count'],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Message Risk Level Distribution",
            xaxis_title="Risk Level",
            yaxis_title="Message Count",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_threat_intelligence(self, stats):
        """Display threat intelligence insights"""
        st.header("🎭 Threat Intelligence")
        
        if not stats or not stats['threat_distribution']:
            st.info("No threat classification data available yet.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Threat Type Analysis")
            for threat_type, count in stats['threat_distribution'][:5]:  # Top 5
                try:
                    threat_data = json.loads(threat_type)
                    primary_type = threat_data.get('primary_types', ['Unknown'])[0]
                    st.write(f"**{primary_type}**: {count} occurrences")
                except:
                    st.write(f"**{threat_type}**: {count} occurrences")
        
        with col2:
            st.subheader("ML Confidence Distribution")
            if stats['avg_confidence'] > 0:
                confidence_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = stats['avg_confidence'] * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Avg ML Confidence"},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "lightgreen"}
                        ]
                    }
                ))
                st.plotly_chart(confidence_gauge, use_container_width=True)
    
    def display_recent_detections(self):
        """Display recent ML detections with detailed analysis"""
        st.header("🔍 Recent ML Detections")
        
        try:
            conn = sqlite3.connect('data/honeyshield.db')
            
            # Get recent messages with ML analysis
            query = '''
                SELECT 
                    timestamp, sender_name, message_content, risk_score, risk_level,
                    keywords_found, analysis_notes, ml_confidence, threat_types
                FROM messages 
                ORDER BY timestamp DESC 
                LIMIT 15
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                st.info("No detection data available. Run the monitoring system to collect data.")
                return
            
            # Display each detection
            for _, row in df.iterrows():
                self._display_detection_card(row)
                
        except Exception as e:
            st.error(f"Error loading detections: {e}")
    
    def _display_detection_card(self, row):
        """Display individual detection card with ML insights"""
        # Risk level styling
        risk_config = {
            'CRITICAL': {'color': 'red', 'emoji': '🚨', 'class': 'critical-alert'},
            'HIGH': {'color': 'orange', 'emoji': '⚠️', 'class': 'high-alert'},
            'MEDIUM': {'color': 'yellow', 'emoji': '🔍', 'class': 'medium-alert'},
            'LOW': {'color': 'green', 'emoji': '✅', 'class': ''}
        }
        
        config = risk_config.get(row['risk_level'], risk_config['LOW'])
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"<div class='{config['class']}'>"
                          f"{config['emoji']} **{row['sender_name']}** - {row['risk_level']} Risk "
                          f"(Score: {row['risk_score']}/100)"
                          f"</div>", unsafe_allow_html=True)
                
                # Message preview
                st.text_area("Message", row['message_content'], height=80, key=f"msg_{row.name}", disabled=True)
            
            with col2:
                st.metric("ML Confidence", f"{row['ml_confidence']:.1%}" if row['ml_confidence'] else "N/A")
                st.write(f"**Time:** {row['timestamp'][:16]}")
            
            # Expandable detailed analysis
            with st.expander("View ML Analysis Details"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if row['keywords_found'] and row['keywords_found'] != 'None':
                        st.write("**Key Indicators:**")
                        indicators = row['keywords_found'].split(', ')
                        for indicator in indicators[:5]:
                            st.write(f"• {indicator}")
                
                with col_b:
                    if row['threat_types'] and row['threat_types'] != 'None':
                        try:
                            threat_data = json.loads(row['threat_types'])
                            st.write("**Threat Classification:**")
                            for threat_type in threat_data.get('primary_types', []):
                                st.write(f"• {threat_type}")
                        except:
                            st.write("**Threat Info:**", row['threat_types'])
                
                if row['analysis_notes'] and row['analysis_notes'] != 'None':
                    st.write("**ML Analysis Notes:**")
                    st.info(row['analysis_notes'])
            
            st.markdown("---")
    
    def display_system_health(self):
        """Display system health and ML model status"""
        st.header("💻 System Health")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Database health
            try:
                conn = sqlite3.connect('data/honeyshield.db')
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM messages")
                count = cursor.fetchone()[0]
                conn.close()
                
                st.success("✅ Database Connected")
                st.metric("Stored Messages", count)
            except:
                st.error("❌ Database Issue")
        
        with col2:
            # ML Model status
            model_path = "models/advanced_phishing_detector.pkl"
            if os.path.exists(model_path):
                st.success("✅ ML Model Loaded")
                model_time = datetime.fromtimestamp(os.path.getmtime(model_path))
                st.metric("Model Updated", model_time.strftime("%Y-%m-%d"))
            else:
                st.warning("⚠️ ML Model Not Found")
                st.info("Run: python train_advanced_model.py")
        
        with col3:
            # System status
            st.success("✅ Dashboard Active")
            st.metric("Last Refresh", datetime.now().strftime("%H:%M:%S"))
    
    def display_real_time_testing(self):
        """Display real-time testing interface"""
        st.header("🧪 Real-time ML Testing")
        
        # Test message input
        test_message = st.text_area(
            "Test Message Input",
            placeholder="Paste a suspicious message here to test ML detection...",
            height=100
        )
        
        if st.button("🔍 Analyze with ML", type="primary") and test_message:
            with st.spinner("ML analysis in progress..."):
                try:
                    from ml_first_engine import MLFirstAnalysisEngine
                    
                    # Initialize and load model
                    engine = MLFirstAnalysisEngine()
                    engine.load_model("models/advanced_phishing_detector.pkl")
                    
                    # Analyze the message
                    result = engine.analyze_message(test_message)
                    
                    # Display results
                    st.subheader("🤖 ML Analysis Results")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Risk Score", f"{result['final_score']}/100")
                    
                    with col2:
                        st.metric("Risk Level", result['risk_level'])
                    
                    with col3:
                        st.metric("ML Confidence", f"{result['ml_analysis']['confidence']:.1%}")
                    
                    # Detailed analysis
                    with st.expander("View Detailed Analysis"):
                        if result['key_indicators']:
                            st.write("**Key Detection Indicators:**")
                            for indicator in result['key_indicators']:
                                st.write(f"• {indicator}")
                        
                        if result['behavioral_patterns']:
                            st.write("**Behavioral Patterns:**")
                            for pattern in result['behavioral_patterns']:
                                st.write(f"• {pattern}")
                        
                        st.write("**Recommended Action:**")
                        st.info(result['recommended_action'])
                        
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    st.info("Make sure the ML model is trained and available at models/advanced_phishing_detector.pkl")
    
    def run(self):
        """Run the advanced dashboard"""
        # Sidebar
        with st.sidebar:
            st.title("🤖 Navigation")
            st.markdown("---")
            st.markdown("**ML Model Status**")
            
            # Model status in sidebar
            model_path = "models/advanced_phishing_detector.pkl"
            if os.path.exists(model_path):
                st.success("✅ ML Model Ready")
            else:
                st.error("❌ Train ML Model First")
                if st.button("Train Model"):
                    st.info("Run: python train_advanced_model.py")
            
            st.markdown("---")
            st.markdown("**Quick Actions**")
            if st.button("🔄 Refresh Data"):
                st.rerun()
            
            st.markdown("---")
            st.markdown("**About**")
            st.info("ML-First phishing detection using advanced behavioral analysis and threat classification.")
        
        # Main content
        self.display_ml_insights_header()
        
        # Get statistics
        stats = self.get_advanced_stats()
        
        # Display all sections
        self.display_ml_metrics(stats)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Analytics", 
            "🔍 Detections", 
            "🧪 Test ML", 
            "💻 System"
        ])
        
        with tab1:
            self.display_risk_distribution_chart(stats)
            self.display_threat_intelligence(stats)
        
        with tab2:
            self.display_recent_detections()
        
        with tab3:
            self.display_real_time_testing()
        
        with tab4:
            self.display_system_health()

# Main execution
if __name__ == "__main__":
    dashboard = MLFirstDashboard()
    dashboard.run()