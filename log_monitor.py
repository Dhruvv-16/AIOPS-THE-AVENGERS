import time
import json
from log_monitor import fetch_prometheus_logs, fetch_datadog_logs
from utils import analyze_log_line
from auto_resolver import resolve_error

# Load registered apps from JSON
def load_apps():
    try:
        with open("registered_apps.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Process logs and resolve issues
def process_logs(logs):
    for log in logs:
        # Log message handling: Assuming logs contain 'message' field
        if "message" in log:
            resolve_error(log)  # Resolve error based on log content

# Continuously monitor logs from registered apps
def fetch_logs_continuously():
    while True:
        apps = load_apps()
        
        for app in apps:
            if app["log_source"] == "Prometheus":
                # Fetch logs from Prometheus
                logs = fetch_prometheus_logs(app["prometheus_url"])
            elif app["log_source"] == "Datadog":
                # Fetch logs from Datadog
                logs = fetch_datadog_logs(app["api_key"], app["app_key"])
            else:
                logs = []  # Add logic for other sources if needed

            process_logs(logs)
        
        time.sleep(60)  # Poll every minute to fetch new logs

# Start continuous log fetching
if __name__ == "__main__":
    fetch_logs_continuously()

