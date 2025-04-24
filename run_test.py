import streamlit as st
import json
import time
from datetime import datetime

# Set up the Streamlit page
st.set_page_config(page_title="Log Monitor Test", layout="wide")
st.title("🔍 Log Monitor Test Interface")

# Function to simulate log generation
def generate_test_logs():
    return [
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Application started successfully",
            "service": "payment-service"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "WARNING",
            "message": "High memory usage detected: 85%",
            "service": "payment-service"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "message": "Failed to connect to database: Connection timeout",
            "service": "payment-service"
        }
    ]

# Function to analyze log severity
def analyze_log_severity(log):
    if log["level"] == "ERROR":
        return "🔴 HIGH", "This is a critical error that needs immediate attention"
    elif log["level"] == "WARNING":
        return "🟡 MEDIUM", "This is a warning that should be monitored"
    else:
        return "🟢 LOW", "This is an informational message"

# Create two columns for the interface
col1, col2 = st.columns(2)

with col1:
    st.header("Test Log Generator")
    if st.button("Generate Test Logs"):
        logs = generate_test_logs()
        st.session_state.logs = logs
        st.success("Test logs generated!")

with col2:
    st.header("Log Analysis")
    if 'logs' in st.session_state:
        for log in st.session_state.logs:
            severity, analysis = analyze_log_severity(log)
            
            with st.expander(f"{severity} - {log['message']}"):
                st.write(f"**Timestamp:** {log['timestamp']}")
                st.write(f"**Service:** {log['service']}")
                st.write(f"**Analysis:** {analysis}")
                
                if severity == "🔴 HIGH":
                    st.error("This requires immediate action!")
                    if st.button("Simulate Auto-Fix", key=f"fix_{log['timestamp']}"):
                        st.info("Simulating automated fix...")
                        time.sleep(2)
                        st.success("Issue resolved automatically!")
                elif severity == "🟡 MEDIUM":
                    st.warning("Monitor this situation")
                    if st.button("Send Alert", key=f"alert_{log['timestamp']}"):
                        st.info("Alert sent to monitoring team")
                else:
                    st.info("No action required")

# Add a clear button
if st.button("Clear Logs"):
    if 'logs' in st.session_state:
        del st.session_state.logs
    st.info("Logs cleared") 