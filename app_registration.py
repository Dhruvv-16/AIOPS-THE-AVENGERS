import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="AI Log Monitor - App Registration", layout="wide")
st.title("📋 Application Registration")

# Initialize session state for notifications
if 'notification' not in st.session_state:
    st.session_state.notification = None

def load_existing_apps():
    try:
        if os.path.exists("registered_apps.json"):
            with open("registered_apps.json", "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading existing apps: {e}")
        return []

def save_app_data(app_data):
    try:
        existing_apps = load_existing_apps()
        existing_apps.append(app_data)
        with open("registered_apps.json", "w") as f:
            json.dump(existing_apps, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving app data: {e}")
        return False

# Create tabs for registration and viewing
tab1, tab2 = st.tabs(["Register New Application", "View Registered Applications"])

with tab1:
    st.header("Application Details")
    
    # Basic Information
    col1, col2 = st.columns(2)
    with col1:
        app_name = st.text_input("Application Name*", help="Name of your web application")
        app_url = st.text_input("Application URL*", help="Base URL of your web application")
        environment = st.selectbox("Environment*", ["Production", "Staging", "Development"])
    
    with col2:
        client_name = st.text_input("Client/Organization Name*")
        client_email = st.text_input("Client Email*", help="Primary contact email for notifications")
        client_phone = st.text_input("Client Phone", help="Optional contact number")

    # Technical Details
    st.subheader("Technical Configuration")
    col3, col4 = st.columns(2)
    
    with col3:
        tech_stack = st.multiselect(
            "Technology Stack*",
            ["Python", "Node.js", "Java", "PHP", "Ruby", ".NET", "Go", "Other"],
            help="Select all technologies used in your application"
        )
        
        database_type = st.multiselect(
            "Database Systems",
            ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Other"],
            help="Select all databases used in your application"
        )

    with col4:
        deployment_platform = st.selectbox(
            "Deployment Platform*",
            ["AWS", "Google Cloud", "Azure", "DigitalOcean", "Heroku", "On-Premise", "Other"]
        )
        
        container_platform = st.multiselect(
            "Container Platform",
            ["Docker", "Kubernetes", "None"],
            help="Select if you use containerization"
        )

    # Monitoring Configuration
    st.subheader("Monitoring Configuration")
    col5, col6 = st.columns(2)
    
    with col5:
        log_source = st.selectbox(
            "Log Source*",
            ["Datadog", "ELK Stack", "CloudWatch", "Custom API", "File System"],
            help="Where are your application logs stored?"
        )
        
        log_format = st.selectbox(
            "Log Format",
            ["JSON", "Plain Text", "Syslog", "Custom"],
            help="Format of your log entries"
        )

    with col6:
        monitoring_frequency = st.slider(
            "Monitoring Frequency (seconds)*",
            min_value=30,
            max_value=3600,
            value=60,
            help="How often should we check your logs?"
        )
        
        retention_days = st.number_input(
            "Log Retention (days)",
            min_value=1,
            max_value=365,
            value=30,
            help="How long should we retain the logs?"
        )

    # Alert Configuration
    st.subheader("Alert Configuration")
    col7, col8 = st.columns(2)
    
    with col7:
        alert_severity = st.multiselect(
            "Alert on Severity Levels*",
            ["HIGH", "MEDIUM", "LOW"],
            default=["HIGH", "MEDIUM"],
            help="Select severity levels that should trigger alerts"
        )
        
        notification_channels = st.multiselect(
            "Notification Channels*",
            ["Email", "Slack", "SMS", "Webhook"],
            default=["Email"],
            help="How should we notify you?"
        )

    with col8:
        automation_level = st.selectbox(
            "Automation Level*",
            [
                "Monitor Only (No automated actions)",
                "Send Notifications Only",
                "Auto-fix Low Risk Issues",
                "Full Automation (Auto-fix all detected issues)"
            ],
            help="Level of automated intervention allowed"
        )

    # API Credentials (conditional based on log source)
    st.subheader("API Credentials")
    if log_source == "Datadog":
        datadog_api_key = st.text_input("Datadog API Key*", type="password")
        datadog_app_key = st.text_input("Datadog Application Key*", type="password")
    elif log_source == "ELK Stack":
        elk_url = st.text_input("ELK Stack URL*")
        elk_username = st.text_input("ELK Username*")
        elk_password = st.text_input("ELK Password*", type="password")
    elif log_source == "CloudWatch":
        aws_access_key = st.text_input("AWS Access Key*", type="password")
        aws_secret_key = st.text_input("AWS Secret Key*", type="password")
        aws_region = st.text_input("AWS Region*")

    # Custom Fields
    st.subheader("Additional Configuration")
    custom_tags = st.text_input(
        "Custom Tags",
        help="Comma-separated tags for organizing applications (e.g., team-a, critical, customer-facing)"
    )
    
    notes = st.text_area(
        "Notes",
        help="Any additional information or special instructions"
    )

    # Submit Button
    if st.button("Register Application"):
        # Validate required fields
        required_fields = {
            "Application Name": app_name,
            "Application URL": app_url,
            "Client Email": client_email,
            "Environment": environment,
            "Technology Stack": tech_stack,
            "Log Source": log_source,
            "Alert Severity Levels": alert_severity,
            "Notification Channels": notification_channels
        }
        
        missing_fields = [field for field, value in required_fields.items() 
                         if not value or (isinstance(value, list) and not value)]
        
        if missing_fields:
            st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
        else:
            # Prepare app data
            app_data = {
                "App Name": app_name,
                "App URL": app_url,
                "Client": {
                    "Name": client_name,
                    "Email": client_email,
                    "Phone": client_phone
                },
                "Environment": environment,
                "Technical": {
                    "Stack": tech_stack,
                    "Databases": database_type,
                    "Deployment": deployment_platform,
                    "Containers": container_platform
                },
                "Monitoring": {
                    "Log Source": log_source,
                    "Log Format": log_format,
                    "Frequency": monitoring_frequency,
                    "Retention Days": retention_days
                },
                "Alerts": {
                    "Severity Levels": alert_severity,
                    "Channels": notification_channels,
                    "Automation Level": automation_level
                },
                "API Credentials": {},  # Will be populated based on log source
                "Tags": [tag.strip() for tag in custom_tags.split(",")] if custom_tags else [],
                "Notes": notes,
                "Registration Date": datetime.now().isoformat()
            }
            
            # Add source-specific credentials
            if log_source == "Datadog":
                app_data["API Credentials"]["datadog"] = {
                    "api_key": datadog_api_key,
                    "app_key": datadog_app_key
                }
            elif log_source == "ELK Stack":
                app_data["API Credentials"]["elk"] = {
                    "url": elk_url,
                    "username": elk_username,
                    "password": elk_password
                }
            elif log_source == "CloudWatch":
                app_data["API Credentials"]["aws"] = {
                    "access_key": aws_access_key,
                    "secret_key": aws_secret_key,
                    "region": aws_region
                }
            
            if save_app_data(app_data):
                st.success("✅ Application registered successfully!")
                st.balloons()
            else:
                st.error("❌ Failed to register application. Please try again.")

with tab2:
    st.header("Registered Applications")
    apps = load_existing_apps()
    
    if not apps:
        st.info("No applications registered yet.")
    else:
        for app in apps:
            # Safely access app data with default values
            app_name = app.get("App Name", "Unknown Application")
            environment = app.get("Environment", "Unknown Environment")
            
            with st.expander(f"📱 {app_name} ({environment})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("Basic Info")
                    st.write(f"**URL:** {app.get('App URL', 'Not specified')}")
                    client = app.get("Client", {})
                    st.write(f"**Client:** {client.get('Name', 'Not specified')}")
                    st.write(f"**Email:** {client.get('Email', 'Not specified')}")
                
                with col2:
                    st.subheader("Technical Details")
                    technical = app.get("Technical", {})
                    st.write(f"**Stack:** {', '.join(technical.get('Stack', ['Not specified']))}")
                    st.write(f"**Deployment:** {technical.get('Deployment', 'Not specified')}")
                    if technical.get('Databases'):
                        st.write(f"**Databases:** {', '.join(technical.get('Databases', ['Not specified']))}")
                
                with col3:
                    st.subheader("Monitoring")
                    monitoring = app.get("Monitoring", {})
                    alerts = app.get("Alerts", {})
                    st.write(f"**Log Source:** {monitoring.get('Log Source', 'Not specified')}")
                    st.write(f"**Automation:** {alerts.get('Automation Level', 'Not specified')}")
                    st.write(f"**Alert Levels:** {', '.join(alerts.get('Severity Levels', ['Not specified']))}")
