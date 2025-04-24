import streamlit as st
import time
import json
import requests
import logging
from datetime import datetime
import threading
import queue
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys

class LogEventHandler(FileSystemEventHandler):
    def __init__(self, log_queue):
        self.log_queue = log_queue
        self.last_position = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.log'):
            try:
                with open(event.src_path, 'r') as f:
                    # Move to the last read position
                    f.seek(self.last_position)
                    # Read new lines
                    new_lines = f.readlines()
                    if new_lines:
                        print(f"New log entries detected: {len(new_lines)}")
                        for line in new_lines:
                            self.log_queue.put(line.strip())
                        # Update the last position
                        self.last_position = f.tell()
            except Exception as e:
                print(f"Error reading log file: {e}")
                logging.error(f"Error reading log file: {e}")

class LiveLogMonitor:
    def __init__(self):
        self.log_queue = queue.Queue()
        self.observer = None
        self.monitoring_thread = None
        self.is_monitoring = False
        self.applications = {}
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitor.log'),
                logging.StreamHandler()
            ]
        )
        
    def register_application(self, app_data):
        """Register a new application for monitoring"""
        app_id = f"app_{len(self.applications) + 1}"
        self.applications[app_id] = {
            "name": app_data["name"],
            "log_path": app_data["log_path"],
            "environment": app_data["environment"],
            "status": "inactive",
            "last_check": datetime.now().isoformat(),
            "customer": {
                "name": app_data["customer_name"],
                "email": app_data["customer_email"],
                "phone": app_data["customer_phone"],
                "company": app_data["customer_company"]
            },
            "api_credentials": {
                "api_key": app_data["api_key"],
                "api_secret": app_data["api_secret"],
                "endpoint": app_data["api_endpoint"]
            },
            "configuration": {
                "alert_threshold": app_data["alert_threshold"],
                "retry_attempts": app_data["retry_attempts"],
                "check_interval": app_data["check_interval"],
                "auto_resolve": app_data["auto_resolve"],
                "notifications": app_data["notifications"]
            },
            "metrics": {
                "error_count": 0,
                "warning_count": 0,
                "uptime": 100.0
            }
        }
        return app_id
        
    def start_monitoring(self, app_id):
        """Start monitoring an application's logs"""
        if app_id not in self.applications:
            return False
            
        app = self.applications[app_id]
        log_path = app["log_path"]
        
        if not os.path.exists(log_path):
            logging.error(f"Log path does not exist: {log_path}")
            return False
            
        # Start file observer
        event_handler = LogEventHandler(self.log_queue)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=log_path, recursive=False)
        self.observer.start()
        
        # Start monitoring thread
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self.monitor_logs, args=(app_id,))
        self.monitoring_thread.start()
        
        return True
        
    def stop_monitoring(self):
        """Stop monitoring logs"""
        self.is_monitoring = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.monitoring_thread:
            self.monitoring_thread.join()
            
    def monitor_logs(self, app_id):
        """Monitor logs in real-time"""
        while self.is_monitoring:
            try:
                # Get new log entries
                while not self.log_queue.empty():
                    log_entry = self.log_queue.get()
                    self.process_log(app_id, log_entry)
                    
                # Update metrics
                self.update_metrics(app_id)
                
                # Sleep briefly to prevent CPU overload
                time.sleep(0.1)
                
            except Exception as e:
                logging.error(f"Error in monitoring thread: {e}")
                
    def process_log(self, app_id, log_entry):
        """Process and analyze a log entry with enhanced error handling"""
        app = self.applications[app_id]
        
        # Basic log analysis
        if "ERROR" in log_entry:
            app["metrics"]["error_count"] += 1
            analysis = self.analyze_error(log_entry)
            
            if analysis["can_auto_resolve"]:
                # Add to recent issues
                app["recent_issues"] = app.get("recent_issues", [])
                app["recent_issues"].append({
                    "timestamp": datetime.now().isoformat(),
                    "error": log_entry,
                    "resolution": "Auto-resolved",
                    "resolution_time": analysis["resolution_time"]
                })
                
                # Keep only last 5 issues
                if len(app["recent_issues"]) > 5:
                    app["recent_issues"] = app["recent_issues"][-5:]
                
                # Attempt auto-resolution
                self.auto_resolve(app_id, analysis["resolution_steps"])
                
        elif "WARNING" in log_entry:
            app["metrics"]["warning_count"] += 1
            self.handle_warning(app_id, log_entry)
            
        # Update last check time
        app["last_check"] = datetime.now().isoformat()
        
    def handle_error(self, app_id, log_entry):
        """Handle error log entries"""
        app = self.applications[app_id]
        
        # AI Analysis (placeholder for actual AI implementation)
        analysis = self.analyze_error(log_entry)
        
        # Automated resolution
        if analysis["can_auto_resolve"]:
            self.auto_resolve(app_id, analysis["resolution_steps"])
            
    def handle_warning(self, app_id, log_entry):
        """Handle warning log entries"""
        app = self.applications[app_id]
        
        # AI Analysis (placeholder for actual AI implementation)
        analysis = self.analyze_warning(log_entry)
        
        # Send alert if needed
        if analysis["needs_attention"]:
            self.send_alert(app_id, log_entry, analysis)
            
    def analyze_error(self, log_entry):
        """Analyze error log entry and determine resolution steps"""
        if "Database connection failed" in log_entry:
            return {
                "can_auto_resolve": True,
                "resolution_steps": [
                    "restart_database_service",
                    "verify_connection",
                    "clear_connection_pool"
                ],
                "severity": "HIGH",
                "error_type": "database_connection",
                "resolution_time": "2 minutes"
            }
        elif "Memory allocation failed" in log_entry:
            return {
                "can_auto_resolve": True,
                "resolution_steps": [
                    "clear_memory_cache",
                    "release_unused_resources",
                    "restart_memory_manager"
                ],
                "severity": "HIGH",
                "error_type": "memory_error",
                "resolution_time": "1 minute"
            }
        elif "API service unavailable" in log_entry:
            return {
                "can_auto_resolve": True,
                "resolution_steps": [
                    "restart_api_service",
                    "reset_load_balancer",
                    "verify_endpoints"
                ],
                "severity": "HIGH",
                "error_type": "api_error",
                "resolution_time": "3 minutes"
            }
        return {
            "can_auto_resolve": False,
            "resolution_steps": [],
            "severity": "UNKNOWN",
            "error_type": "unknown",
            "resolution_time": "N/A"
        }
        
    def analyze_warning(self, log_entry):
        """Analyze warning log entry (placeholder for AI implementation)"""
        # This would be replaced with actual AI analysis
        return {
            "needs_attention": True,
            "recommendations": ["monitor_resource_usage", "optimize_performance"],
            "severity": "MEDIUM"
        }
        
    def auto_resolve(self, app_id, steps):
        """Automatically resolve issues with simulated actions"""
        app = self.applications[app_id]
        
        for step in steps:
            if step == "restart_database_service":
                logging.info(f"Executing: Restarting database service for {app['name']}")
                time.sleep(2)  # Simulate service restart
            elif step == "verify_connection":
                logging.info(f"Executing: Verifying database connection for {app['name']}")
                time.sleep(1)  # Simulate connection verification
            elif step == "clear_connection_pool":
                logging.info(f"Executing: Clearing connection pool for {app['name']}")
                time.sleep(1)  # Simulate pool clearing
            elif step == "clear_memory_cache":
                logging.info(f"Executing: Clearing memory cache for {app['name']}")
                time.sleep(1)  # Simulate cache clearing
            elif step == "release_unused_resources":
                logging.info(f"Executing: Releasing unused resources for {app['name']}")
                time.sleep(1)  # Simulate resource release
            elif step == "restart_memory_manager":
                logging.info(f"Executing: Restarting memory manager for {app['name']}")
                time.sleep(2)  # Simulate manager restart
            elif step == "restart_api_service":
                logging.info(f"Executing: Restarting API service for {app['name']}")
                time.sleep(2)  # Simulate service restart
            elif step == "reset_load_balancer":
                logging.info(f"Executing: Resetting load balancer for {app['name']}")
                time.sleep(1)  # Simulate balancer reset
            elif step == "verify_endpoints":
                logging.info(f"Executing: Verifying API endpoints for {app['name']}")
                time.sleep(1)  # Simulate endpoint verification
                
        logging.info(f"Auto-resolution completed for {app['name']}")
        app["metrics"]["auto_resolved_issues"] = app["metrics"].get("auto_resolved_issues", 0) + 1
        
    def send_alert(self, app_id, log_entry, analysis):
        """Send alert for issues that need attention"""
        app = self.applications[app_id]
        
        # Simulate sending alert
        logging.info(f"Alert sent for {app['name']}: {log_entry}")
        
    def update_metrics(self, app_id):
        """Update application metrics"""
        app = self.applications[app_id]
        
        # Update uptime based on error count
        total_checks = app["metrics"]["error_count"] + app["metrics"]["warning_count"]
        if total_checks > 0:
            error_rate = app["metrics"]["error_count"] / total_checks
            app["metrics"]["uptime"] = max(0, 100 - (error_rate * 100))
            
# Streamlit UI
def main():
    # Set page config
    st.set_page_config(
        page_title="AIOps - Intelligent Log Monitoring",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize monitor in session state
    if 'monitor' not in st.session_state:
        st.session_state.monitor = LiveLogMonitor()
    
    # Custom CSS
    st.markdown("""
    <style>
    /* Main Colors */
    :root {
        --primary: #2563eb;
        --secondary: #475569;
        --success: #22c55e;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
        --background: #ffffff;
        --card-bg: #f8fafc;
        --text-primary: #000000;
        --text-secondary: #4b5563;
        --border-color: #e5e7eb;
        --heading-color: #111827;
    }
    
    /* Global Styles */
    .stApp {
        background-color: var(--background);
        color: var(--text-primary);
    }
    
    /* Header Styles */
    .main-header {
        font-size: 2.5rem;
        color: var(--heading-color);
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: var(--heading-color);
        margin-bottom: 1.5rem;
        font-weight: 600;
    }
    
    /* Card Styles */
    .metric-card {
        background-color: var(--card-bg);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    .metric-card h3 {
        color: var(--heading-color);
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.1);
    }
    
    .section-card {
        background-color: var(--card-bg);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    .section-card h3 {
        color: var(--heading-color);
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Log Entry Styles */
    .log-entry {
        font-family: 'SF Mono', 'Consolas', monospace;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        font-size: 0.9rem;
        line-height: 1.5;
        border: 1px solid var(--border-color);
    }
    
    .log-error {
        background-color: #fef2f2;
        border-left: 4px solid var(--danger);
        color: #991b1b;
    }
    
    .log-warning {
        background-color: #fffbeb;
        border-left: 4px solid var(--warning);
        color: #92400e;
    }
    
    .log-info {
        background-color: #eff6ff;
        border-left: 4px solid var(--info);
        color: #1e40af;
    }
    
    /* Form Styles */
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 0.75rem;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        background-color: var(--background);
    }
    
    .stSelectbox>div>div>div {
        border-radius: 8px;
        padding: 0.75rem;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        background-color: var(--background);
    }
    
    /* Button Styles */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
        background-color: var(--primary);
        color: white;
        border: none;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #1d4ed8;
    }
    
    /* Status Badge */
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        border: 1px solid var(--border-color);
    }
    
    .status-active {
        background-color: #dcfce7;
        color: #166534;
        border-color: #86efac;
    }
    
    .status-inactive {
        background-color: #fee2e2;
        color: #991b1b;
        border-color: #fca5a5;
    }
    
    /* Metric Value */
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: var(--heading-color);
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-bottom: 0.25rem;
    }
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-weight: 600;
        color: var(--heading-color);
    }
    
    /* Streamlit Default Text Colors */
    .stMarkdown {
        color: var(--text-primary);
    }
    
    .stTextInput label {
        color: var(--heading-color);
        font-weight: 600;
    }
    
    .stSelectbox label {
        color: var(--heading-color);
        font-weight: 600;
    }
    
    .stNumberInput label {
        color: var(--heading-color);
        font-weight: 600;
    }
    
    .stSlider label {
        color: var(--heading-color);
        font-weight: 600;
    }
    
    .stCheckbox label {
        color: var(--heading-color);
        font-weight: 600;
    }
    
    .stMultiselect label {
        color: var(--heading-color);
        font-weight: 600;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--background);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h1 class="main-header">AIOps</h1>
        <p style='font-size: 1.25rem; color: var(--text-secondary); max-width: 800px; margin: 0 auto;'>
            Intelligent Log Monitoring & Automated Issue Resolution
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    if st.session_state.monitor.applications:
        total_apps = len(st.session_state.monitor.applications)
        active_apps = sum(1 for app in st.session_state.monitor.applications.values() if app["status"] == "active")
        total_errors = sum(app["metrics"]["error_count"] for app in st.session_state.monitor.applications.values())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Total Applications</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(total_apps), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Active Applications</div>
                <div class="metric-value" style="color: var(--success);">{}</div>
            </div>
            """.format(active_apps), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Total Errors</div>
                <div class="metric-value" style="color: var(--danger);">{}</div>
            </div>
            """.format(total_errors), unsafe_allow_html=True)
    else:
        st.info("ℹ️ No applications registered yet. Register your first application to start monitoring.")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📝 Register Application", "📊 Live Monitoring", "📈 Analytics"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">📝 Register New Application</h2>', unsafe_allow_html=True)
        with st.form("app_registration"):
            # Application Details
            with st.container():
                st.markdown("""
                <div class="section-card">
                    <h3>📱 Application Details</h3>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    app_name = st.text_input("Application Name*", placeholder="Enter application name")
                    environment = st.selectbox("Environment*", ["Production", "Staging", "Development"])
                with col2:
                    log_path = st.text_input("Log File Path*", placeholder="e.g., ./logs/app.log")
                    st.markdown("""
                    <div style='font-size: 0.8rem; color: #666; margin-top: -1rem;'>
                        Path to the application's log file
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Customer Information
            with st.container():
                st.markdown("""
                <div class="section-card">
                    <h3>👥 Customer Information</h3>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    customer_name = st.text_input("Customer Name*", placeholder="Enter customer name")
                    customer_email = st.text_input("Customer Email*", placeholder="Enter customer email")
                with col2:
                    customer_phone = st.text_input("Customer Phone", placeholder="Enter customer phone")
                    customer_company = st.text_input("Company Name", placeholder="Enter company name")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # API Credentials
            with st.container():
                st.markdown("""
                <div class="section-card">
                    <h3>🔑 API Credentials</h3>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    api_key = st.text_input("API Key*", type="password", placeholder="Enter API key")
                    api_endpoint = st.text_input("API Endpoint*", placeholder="Enter API endpoint")
                with col2:
                    api_secret = st.text_input("API Secret*", type="password", placeholder="Enter API secret")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Configuration Settings
            with st.container():
                st.markdown("""
                <div class="section-card">
                    <h3>⚙️ Configuration Settings</h3>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    alert_threshold = st.slider("Alert Threshold (%)", 0, 100, 80, 
                        help="Percentage of errors that will trigger an alert")
                    retry_attempts = st.number_input("Retry Attempts", 1, 10, 3,
                        help="Number of times to retry failed operations")
                with col2:
                    check_interval = st.number_input("Check Interval (seconds)", 1, 300, 60,
                        help="Time between log checks")
                    auto_resolve = st.checkbox("Enable Auto-Resolution", value=True,
                        help="Automatically attempt to resolve detected issues")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Notification Settings
            with st.container():
                st.markdown("""
                <div class="section-card">
                    <h3>🔔 Notification Settings</h3>
                """, unsafe_allow_html=True)
                notifications = st.multiselect(
                    "Select Notification Methods",
                    ["Email", "SMS", "Slack", "Webhook"],
                    default=["Email"],
                    help="Choose how you want to receive alerts"
                )
                st.markdown("</div>", unsafe_allow_html=True)
            
            if st.form_submit_button("Register Application", use_container_width=True):
                if app_name and log_path and customer_name and customer_email and api_key and api_secret and api_endpoint:
                    app_data = {
                        "name": app_name,
                        "log_path": log_path,
                        "environment": environment,
                        "customer_name": customer_name,
                        "customer_email": customer_email,
                        "customer_phone": customer_phone,
                        "customer_company": customer_company,
                        "api_key": api_key,
                        "api_secret": api_secret,
                        "api_endpoint": api_endpoint,
                        "alert_threshold": alert_threshold,
                        "retry_attempts": retry_attempts,
                        "check_interval": check_interval,
                        "auto_resolve": auto_resolve,
                        "notifications": notifications
                    }
                    app_id = st.session_state.monitor.register_application(app_data)
                    st.success(f"✅ Application registered successfully! ID: {app_id}")
                else:
                    st.error("❌ Please fill in all required fields (marked with *)")
                    
    with tab2:
        st.markdown('<h2 class="sub-header">📊 Live Log Monitoring</h2>', unsafe_allow_html=True)
        if st.session_state.monitor.applications:
            selected_app = st.selectbox(
                "Select Application",
                options=list(st.session_state.monitor.applications.keys()),
                format_func=lambda x: st.session_state.monitor.applications[x]["name"]
            )
            
            if selected_app:
                app = st.session_state.monitor.applications[selected_app]
                
                # Status cards
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown("""
                    <div class="metric-card">
                        <h3>Status</h3>
                        <p style='color: #4CAF50; font-size: 1.2rem;'>🟢 Active</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <h3>Environment</h3>
                        <p style='font-size: 1.2rem;'>{}</p>
                    </div>
                    """.format(app["environment"]), unsafe_allow_html=True)
                with col3:
                    st.markdown("""
                    <div class="metric-card">
                        <h3>Last Check</h3>
                        <p style='font-size: 1.2rem;'>{}</p>
                    </div>
                    """.format(app["last_check"]), unsafe_allow_html=True)
                with col4:
                    st.markdown("""
                    <div class="metric-card">
                        <h3>Auto-Resolved Issues</h3>
                        <p style='font-size: 1.2rem; color: #4CAF50;'>{}</p>
                    </div>
                    """.format(app["metrics"].get("auto_resolved_issues", 0)), unsafe_allow_html=True)
                
                # Control buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("▶️ Start Monitoring", use_container_width=True):
                        if st.session_state.monitor.start_monitoring(selected_app):
                            st.success("✅ Monitoring started!")
                        else:
                            st.error("❌ Failed to start monitoring")
                with col2:
                    if st.button("⏹️ Stop Monitoring", use_container_width=True):
                        st.session_state.monitor.stop_monitoring()
                        st.info("ℹ️ Monitoring stopped")
                
                # Live log stream
                st.markdown('<h3 class="sub-header">Live Log Stream</h3>', unsafe_allow_html=True)
                log_container = st.empty()
                
                while st.session_state.monitor.is_monitoring:
                    try:
                        log_entry = st.session_state.monitor.log_queue.get(timeout=1)
                        with log_container.container():
                            if "ERROR" in log_entry:
                                st.markdown(f'<div class="log-entry log-error">{log_entry}</div>', unsafe_allow_html=True)
                            elif "WARNING" in log_entry:
                                st.markdown(f'<div class="log-entry log-warning">{log_entry}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="log-entry log-info">{log_entry}</div>', unsafe_allow_html=True)
                    except queue.Empty:
                        pass
                        
    with tab3:
        st.markdown('<h2 class="sub-header">📈 Analytics Dashboard</h2>', unsafe_allow_html=True)
        if st.session_state.monitor.applications:
            for app_id, app in st.session_state.monitor.applications.items():
                with st.expander(f"📊 {app['name']} - {app['environment']}", expanded=True):
                    # Status and Overview
                    st.markdown("""
                    <div class="section-card">
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <h3>Overview</h3>
                            <span class='status-badge status-{}'>{}</span>
                        </div>
                    """.format(
                        "active" if app["status"] == "active" else "inactive",
                        "Active" if app["status"] == "active" else "Inactive"
                    ), unsafe_allow_html=True)
                    
                    # Customer Information
                    st.markdown("### 👥 Customer Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        <div class="config-item">
                            <p><strong>Name:</strong> {}</p>
                            <p><strong>Email:</strong> {}</p>
                        </div>
                        """.format(app['customer']['name'], app['customer']['email']), unsafe_allow_html=True)
                    with col2:
                        st.markdown("""
                        <div class="config-item">
                            <p><strong>Phone:</strong> {}</p>
                            <p><strong>Company:</strong> {}</p>
                        </div>
                        """.format(app['customer']['phone'], app['customer']['company']), unsafe_allow_html=True)
                    
                    # Configuration Summary
                    st.markdown("### ⚙️ Configuration")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        <div class="config-item">
                            <p><strong>Alert Threshold:</strong> {}%</p>
                            <p><strong>Retry Attempts:</strong> {}</p>
                        </div>
                        """.format(app['configuration']['alert_threshold'], app['configuration']['retry_attempts']), unsafe_allow_html=True)
                    with col2:
                        st.markdown("""
                        <div class="config-item">
                            <p><strong>Check Interval:</strong> {}s</p>
                            <p><strong>Auto-Resolution:</strong> {}</p>
                        </div>
                        """.format(app['configuration']['check_interval'], 'Enabled' if app['configuration']['auto_resolve'] else 'Disabled'), unsafe_allow_html=True)
                    
                    # Metrics
                    st.markdown("### 📊 Performance Metrics")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown("""
                        <div class="metric-card">
                            <h4>Error Count</h4>
                            <p style='font-size: 2rem; color: #f44336;'>{}</p>
                        </div>
                        """.format(app["metrics"]["error_count"]), unsafe_allow_html=True)
                    with col2:
                        st.markdown("""
                        <div class="metric-card">
                            <h4>Warning Count</h4>
                            <p style='font-size: 2rem; color: #ff9800;'>{}</p>
                        </div>
                        """.format(app["metrics"]["warning_count"]), unsafe_allow_html=True)
                    with col3:
                        st.markdown("""
                        <div class="metric-card">
                            <h4>Uptime</h4>
                            <p style='font-size: 2rem; color: #4CAF50;'>{:.2f}%</p>
                        </div>
                        """.format(app["metrics"]["uptime"]), unsafe_allow_html=True)
                    with col4:
                        st.markdown("""
                        <div class="metric-card">
                            <h4>Status</h4>
                            <p style='font-size: 2rem;'>{}</p>
                        </div>
                        """.format("🟢" if app["status"] == "active" else "🔴"), unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
if __name__ == "__main__":
    main() 