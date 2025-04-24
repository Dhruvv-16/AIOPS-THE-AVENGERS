import streamlit as st
from utils import analyze_log_line
import requests
from datetime import datetime
import json
import logging
from config import GROQ_API_KEY, LOG_DIR

# Configure logging
logging.basicConfig(
    filename=f"{LOG_DIR}/log_analyzer.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LogAnalyzer:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.error_patterns = self._load_error_patterns()
        
    def _load_error_patterns(self):
        """Load known error patterns and their solutions"""
        return {
            "database connection": {
                "type": "ERROR",
                "category": "Database",
                "severity": "HIGH",
                "automated_actions": ["restart_database", "check_connection"]
            },
            "memory usage": {
                "type": "WARNING",
                "category": "Resources",
                "severity": "MEDIUM",
                "automated_actions": ["clear_cache", "scale_resources"]
            },
            "cpu high": {
                "type": "WARNING",
                "category": "Resources",
                "severity": "MEDIUM",
                "automated_actions": ["optimize_processes", "scale_resources"]
            }
        }

    def analyze_log(self, log_entry):
        """Analyze a log entry using AI and pattern matching"""
        try:
            # First check against known patterns
            for pattern, info in self.error_patterns.items():
                if pattern in log_entry.lower():
                    return {
                        "timestamp": datetime.now().isoformat(),
                        "pattern_match": pattern,
                        "severity": info["severity"],
                        "category": info["category"],
                        "automated_actions": info["automated_actions"],
                        "ai_analysis": self._get_ai_analysis(log_entry)
                    }
            
            # If no pattern matched, still get AI analysis
            return {
                "timestamp": datetime.now().isoformat(),
                "pattern_match": None,
                "severity": "UNKNOWN",
                "category": "UNKNOWN",
                "automated_actions": [],
                "ai_analysis": self._get_ai_analysis(log_entry)
            }
        except Exception as e:
            logging.error(f"Error analyzing log: {str(e)}")
            return None

    def _get_ai_analysis(self, log_entry):
        """Get AI analysis using Groq API"""
        prompt = f"""
        Analyze this log entry and provide:
        1. The type of issue (ERROR/WARNING/INFO)
        2. Root cause analysis
        3. Recommended automated actions
        4. Priority level
        5. Potential impact

        Log entry: {log_entry}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "You are an expert log analysis AI assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logging.error(f"AI API Error: {response.status_code}")
                return "AI analysis failed"
        except Exception as e:
            logging.error(f"Error in AI analysis: {str(e)}")
            return "AI analysis failed"

    def get_resolution_steps(self, analysis_result):
        """Generate resolution steps based on analysis"""
        if not analysis_result:
            return []
            
        automated_actions = analysis_result.get("automated_actions", [])
        resolution_steps = []
        
        for action in automated_actions:
            if action == "restart_database":
                resolution_steps.append({
                    "action": "restart_database",
                    "description": "Automatically restart the database service",
                    "priority": "HIGH"
                })
            elif action == "clear_cache":
                resolution_steps.append({
                    "action": "clear_cache",
                    "description": "Clear system cache to free up memory",
                    "priority": "MEDIUM"
                })
            elif action == "scale_resources":
                resolution_steps.append({
                    "action": "scale_resources",
                    "description": "Increase allocated resources",
                    "priority": "MEDIUM"
                })
                
        return resolution_steps

st.set_page_config(page_title="Log Analyzer with Groq LLaMA", layout="wide")

st.title("Log Analyzer")

# Input text area for logs
log_input = st.text_area(
    "Paste your logs here (one log per line):",
    height=200,
    placeholder="Example:\nERROR 2024-04-01 10:00:00 Something went wrong...\nINFO 2024-04-01 10:01:00 Process started."
)

# Button to trigger log analysis
if st.button("Analyze Logs") and log_input.strip():
    st.subheader("📄 Log Analysis Results")

    # Split the input into individual log lines
    log_lines = log_input.strip().split("\n")

    # Loop through each log line and analyze it
    for i, line in enumerate(log_lines):
        line = line.strip()
        if line:
            try:
                # Analyze the log line using the backend function
                with st.spinner(f"Analyzing log line {i + 1}..."):
                    result = analyze_log_line(line)

                    # Display the log analysis results
                    st.markdown(f"### 🔹 Log Line {i + 1}")
                    st.code(line, language="bash")  # Show the original log line
                    st.markdown(result)  # Show the analysis result
                    st.markdown("---")  # Divider for clarity
            except Exception as e:
                st.error(f"Error analyzing line {i + 1}: {e}")
        else:
            st.warning(f"Log line {i + 1} is empty.")
else:
    st.markdown("""
    Please paste some logs in the input field and click **'Analyze Logs'** to start the analysis.
    The analysis will provide the log type, definition, and suggested resolutions.
    """)
