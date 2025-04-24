import streamlit as st
from utils import analyze_log_line

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
