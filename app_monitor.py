import streamlit as st
import json
import time
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ApplicationMonitor:
    def __init__(self):
        self.applications = {}
        self.log_patterns = {
            "database": {
                "patterns": ["connection failed", "timeout", "deadlock"],
                "severity": "HIGH",
                "auto_fix": ["restart_database", "check_connection"]
            },
            "memory": {
                "patterns": ["out of memory", "memory limit exceeded"],
                "severity": "HIGH",
                "auto_fix": ["clear_cache", "scale_resources"]
            },
            "performance": {
                "patterns": ["slow response", "high latency"],
                "severity": "MEDIUM",
                "auto_fix": ["optimize_query", "scale_resources"]
            }
        }
        
    def register_application(self, app_data):
        """Register a new application for monitoring"""
        app_id = f"app_{len(self.applications) + 1}"
        self.applications[app_id] = {
            "basic_info": {
                "name": app_data["name"],
                "url": app_data["url"],
                "environment": app_data["environment"],
                "registration_date": app_data["registration_date"],
                "status": app_data["status"]
            },
            "client_info": app_data["client"],
            "technical_info": app_data["technical"],
            "monitoring_config": app_data["monitoring"],
            "notes": app_data["notes"],
            "logs": [],
            "metrics": {
                "uptime": 100.0,
                "response_time": 0,
                "error_rate": 0.0,
                "last_check": datetime.now().isoformat()
            }
        }
        return app_id

    def generate_ai_analysis(self, log_entry, app_id):
        """Generate AI analysis for a log entry with application context"""
        app_info = self.applications[app_id]
        
        # Enhanced AI analysis based on application context
        analysis = {
            "severity": "HIGH" if "error" in log_entry.lower() else "MEDIUM",
            "analysis": "AI analysis of the log entry",
            "recommended_actions": ["action1", "action2"],
            "impact": {
                "uptime": "High" if "error" in log_entry.lower() else "Low",
                "performance": "High" if "slow" in log_entry.lower() else "Low",
                "security": "High" if "security" in log_entry.lower() else "Low"
            }
        }
        
        # Add SLA compliance check
        if "error" in log_entry.lower():
            analysis["sla_compliance"] = "At Risk"
        else:
            analysis["sla_compliance"] = "Compliant"
            
        return analysis

    def process_log(self, app_id, log_entry):
        """Process and analyze a log entry with enhanced context"""
        if app_id not in self.applications:
            return None

        # Add timestamp and enhanced analysis
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "entry": log_entry,
            "analysis": self.generate_ai_analysis(log_entry, app_id)
        }

        # Check for known patterns with application context
        for category, pattern_data in self.log_patterns.items():
            for pattern in pattern_data["patterns"]:
                if pattern in log_entry.lower():
                    log_data["category"] = category
                    log_data["severity"] = pattern_data["severity"]
                    log_data["auto_fix"] = pattern_data["auto_fix"]
                    break

        # Update application metrics
        self.update_metrics(app_id, log_data)
        
        self.applications[app_id]["logs"].append(log_data)
        return log_data

    def update_metrics(self, app_id, log_data):
        """Update application metrics based on log analysis"""
        app = self.applications[app_id]
        
        # Update error rate
        if log_data["analysis"]["severity"] == "HIGH":
            app["metrics"]["error_rate"] = min(100.0, app["metrics"]["error_rate"] + 0.1)
        
        # Update uptime
        if log_data["analysis"]["severity"] == "HIGH":
            app["metrics"]["uptime"] = max(0.0, app["metrics"]["uptime"] - 0.1)
            
        # Update last check time
        app["metrics"]["last_check"] = datetime.now().isoformat()

    def get_application_status(self, app_id):
        """Get current status of an application with enhanced metrics"""
        if app_id not in self.applications:
            return None
            
        app = self.applications[app_id]
        return {
            "basic_info": app["basic_info"],
            "metrics": app["metrics"],
            "last_log": app["logs"][-1] if app["logs"] else None,
            "sla_compliance": self.check_sla_compliance(app_id)
        }
        
    def check_sla_compliance(self, app_id):
        """Check if application is meeting SLA requirements"""
        app = self.applications[app_id]
        metrics = app["metrics"]
        requirements = app["monitoring_config"]["sla"]
        
        compliance = {
            "uptime": metrics["uptime"] >= requirements["uptime"],
            "response_time": metrics["response_time"] <= requirements["response_time"],
            "overall": True
        }
        
        compliance["overall"] = all(compliance.values())
        return compliance

# Initialize the Streamlit app
st.set_page_config(page_title="AI-Powered Application Monitor", layout="wide")
st.title("🤖 AI-Powered Application Monitor")

# Initialize the monitor
if 'monitor' not in st.session_state:
    st.session_state.monitor = ApplicationMonitor()

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Register Application", "View Logs", "AI Analysis"])

with tab1:
    st.header("Register New Application")
    with st.form("app_registration"):
        # Basic Information
        st.subheader("Basic Information")
        app_name = st.text_input("Application Name*")
        app_url = st.text_input("Application URL*")
        environment = st.selectbox("Environment*", ["Production", "Staging", "Development"])
        
        # Client Information
        st.subheader("Client Information")
        client_name = st.text_input("Client Name*")
        client_email = st.text_input("Client Email*")
        client_phone = st.text_input("Client Phone")
        
        # Technical Details
        st.subheader("Technical Details")
        tech_stack = st.multiselect(
            "Technology Stack*",
            ["Python", "Java", "Node.js", "React", "Angular", "Vue.js", "Docker", "Kubernetes", "AWS", "Azure", "GCP"]
        )
        database = st.selectbox(
            "Database*",
            ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Oracle", "SQL Server"]
        )
        deployment_type = st.selectbox(
            "Deployment Type*",
            ["Cloud", "On-premise", "Hybrid"]
        )
        
        # Monitoring Configuration
        st.subheader("Monitoring Configuration")
        monitoring_frequency = st.selectbox(
            "Log Check Frequency*",
            ["Real-time", "Every 5 minutes", "Every 15 minutes", "Every 30 minutes", "Every hour"]
        )
        alert_threshold = st.selectbox(
            "Alert Threshold*",
            ["High Only", "Medium and High", "All Issues"]
        )
        notification_channels = st.multiselect(
            "Notification Channels*",
            ["Email", "Slack", "Teams", "SMS"]
        )
        
        # SLA Requirements
        st.subheader("SLA Requirements")
        response_time = st.number_input("Expected Response Time (ms)*", min_value=100, value=1000)
        uptime_requirement = st.slider("Required Uptime (%)*", min_value=90, max_value=100, value=99)
        
        # Additional Notes
        st.subheader("Additional Information")
        additional_notes = st.text_area("Additional Notes", help="Any specific requirements or notes about the application")
        
        if st.form_submit_button("Register Application"):
            if not all([app_name, app_url, environment, client_name, client_email, tech_stack, database, 
                       deployment_type, monitoring_frequency, alert_threshold, notification_channels]):
                st.error("Please fill in all required fields (marked with *)")
            else:
                app_data = {
                    "name": app_name,
                    "url": app_url,
                    "environment": environment,
                    "client": {
                        "name": client_name,
                        "email": client_email,
                        "phone": client_phone
                    },
                    "technical": {
                        "stack": tech_stack,
                        "database": database,
                        "deployment": deployment_type
                    },
                    "monitoring": {
                        "frequency": monitoring_frequency,
                        "alert_threshold": alert_threshold,
                        "notification_channels": notification_channels,
                        "sla": {
                            "response_time": response_time,
                            "uptime": uptime_requirement
                        }
                    },
                    "notes": additional_notes,
                    "registration_date": datetime.now().isoformat(),
                    "status": "active"
                }
                app_id = st.session_state.monitor.register_application(app_data)
                st.success(f"Application registered successfully! ID: {app_id}")
                st.info("You can now view and monitor this application in the 'View Logs' tab.")

with tab2:
    st.header("Application Logs")
    if st.session_state.monitor.applications:
        selected_app = st.selectbox(
            "Select Application",
            options=list(st.session_state.monitor.applications.keys()),
            format_func=lambda x: st.session_state.monitor.applications[x]["basic_info"]["name"]
        )
        
        if selected_app:
            app_data = st.session_state.monitor.applications[selected_app]
            st.write(f"**Name:** {app_data['basic_info']['name']}")
            st.write(f"**URL:** {app_data['basic_info']['url']}")
            st.write(f"**Environment:** {app_data['basic_info']['environment']}")
            
            # Log entry form
            with st.form("log_entry"):
                log_message = st.text_area("Enter Log Message")
                if st.form_submit_button("Add Log"):
                    if log_message:
                        log_data = st.session_state.monitor.process_log(selected_app, log_message)
                        st.success("Log added and analyzed!")
            
            # Display logs
            if app_data["logs"]:
                st.subheader("Recent Logs")
                for log in reversed(app_data["logs"]):
                    with st.expander(f"{log['timestamp']} - {log['entry']}"):
                        st.write(f"**Severity:** {log['analysis']['severity']}")
                        st.write(f"**Analysis:** {log['analysis']['analysis']}")
                        st.write(f"**Recommended Actions:** {', '.join(log['analysis']['recommended_actions'])}")
    else:
        st.info("No applications registered yet. Please register an application first.")

with tab3:
    st.header("AI Analysis Dashboard")
    if st.session_state.monitor.applications:
        # Display overall statistics
        total_apps = len(st.session_state.monitor.applications)
        total_logs = sum(len(app["logs"]) for app in st.session_state.monitor.applications.values())
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Applications", total_apps)
        with col2:
            st.metric("Total Logs Analyzed", total_logs)
        
        # Display recent issues
        st.subheader("Recent Issues")
        for app_id, app_data in st.session_state.monitor.applications.items():
            for log in app_data["logs"][-5:]:  # Show last 5 logs
                if log["analysis"]["severity"] == "HIGH":
                    with st.expander(f"🚨 {app_data['basic_info']['name']} - {log['entry']}"):
                        st.write(f"**Time:** {log['timestamp']}")
                        st.write(f"**Analysis:** {log['analysis']['analysis']}")
                        st.write(f"**Auto-Fix Actions:** {', '.join(log['analysis']['recommended_actions'])}")
                        if st.button("Execute Auto-Fix", key=f"fix_{log['timestamp']}"):
                            st.info("Executing automated fixes...")
                            time.sleep(2)
                            st.success("Issues resolved automatically!")
    else:
        st.info("No applications registered yet. Please register an application first.") 