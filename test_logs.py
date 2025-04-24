import streamlit as st
import time
from datetime import datetime

def test_log_monitoring():
    st.title("🧪 Log Monitoring Test")
    
    # Test logs with different scenarios
    test_logs = [
        {
            "message": "INFO: Payment service initialized successfully",
            "expected_severity": "LOW",
            "description": "Normal startup message"
        },
        {
            "message": "WARNING: Database connection pool at 80% capacity",
            "expected_severity": "MEDIUM",
            "description": "Resource warning"
        },
        {
            "message": "ERROR: Failed to process payment - Database connection timeout",
            "expected_severity": "HIGH",
            "description": "Critical database error"
        },
        {
            "message": "ERROR: Memory usage exceeded 90% threshold",
            "expected_severity": "HIGH",
            "description": "Resource critical error"
        },
        {
            "message": "WARNING: API response time above 800ms for payment endpoint",
            "expected_severity": "MEDIUM",
            "description": "Performance warning"
        }
    ]
    
    # Display test controls
    st.header("Test Controls")
    if st.button("Run All Tests"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, test in enumerate(test_logs):
            # Update progress
            progress = (i + 1) / len(test_logs)
            progress_bar.progress(progress)
            
            # Simulate log processing
            status_text.text(f"Processing: {test['description']}")
            time.sleep(1)  # Simulate processing time
            
            # Display test results
            with st.expander(f"Test {i+1}: {test['description']}"):
                st.write(f"**Log Message:** {test['message']}")
                st.write(f"**Expected Severity:** {test['expected_severity']}")
                
                # Simulate AI analysis
                if test['expected_severity'] == "HIGH":
                    st.error("🔴 High Severity Issue Detected")
                    st.write("**AI Analysis:** Critical issue requiring immediate attention")
                    st.write("**Recommended Actions:**")
                    st.write("- Restart affected service")
                    st.write("- Scale resources if needed")
                    st.write("- Notify operations team")
                    
                    if st.button("Execute Auto-Fix", key=f"fix_{i}"):
                        st.info("🔄 Executing automated fixes...")
                        time.sleep(2)
                        st.success("✅ Issue resolved automatically!")
                        
                elif test['expected_severity'] == "MEDIUM":
                    st.warning("🟡 Medium Severity Issue Detected")
                    st.write("**AI Analysis:** Warning that should be monitored")
                    st.write("**Recommended Actions:**")
                    st.write("- Monitor resource usage")
                    st.write("- Optimize performance")
                    
                    if st.button("Send Alert", key=f"alert_{i}"):
                        st.info("📧 Alert sent to monitoring team")
                        
                else:
                    st.success("🟢 Low Severity - Normal Operation")
                    st.write("**AI Analysis:** Standard operational message")
                    st.write("**Action:** No action required")
            
            time.sleep(1)  # Pause between tests
        
        status_text.text("✅ All tests completed!")
        st.balloons()

    # Display test scenarios
    st.header("Test Scenarios")
    for test in test_logs:
        with st.expander(f"Scenario: {test['description']}"):
            st.write(f"**Log Message:** `{test['message']}`")
            st.write(f"**Expected Behavior:**")
            if test['expected_severity'] == "HIGH":
                st.write("- Should trigger high severity alert")
                st.write("- Should suggest automated fixes")
                st.write("- Should impact SLA metrics")
            elif test['expected_severity'] == "MEDIUM":
                st.write("- Should trigger warning alert")
                st.write("- Should suggest monitoring actions")
                st.write("- Should be tracked in metrics")
            else:
                st.write("- Should be logged as normal operation")
                st.write("- Should not trigger alerts")
                st.write("- Should maintain normal metrics")

if __name__ == "__main__":
    test_log_monitoring() 