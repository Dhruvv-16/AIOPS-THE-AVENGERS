import json
import time
from log_analyzer import LogAnalyzer
from notifications import EmailNotifier
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestMonitor:
    def __init__(self):
        self.log_analyzer = LogAnalyzer()
        self.email_notifier = EmailNotifier()
        self.app_data = {
            "App Name": "E-Commerce Platform",
            "App URL": "https://shop.example.com",
            "Client": {
                "Name": "TechRetail Inc.",
                "Email": "alerts@techretail.com"
            },
            "Environment": "Production",
            "Monitoring": {
                "Log Source": "File System",
                "Log Format": "JSON"
            },
            "Alerts": {
                "Severity Levels": ["HIGH", "MEDIUM"],
                "Channels": ["Email"],
                "Automation Level": "Auto-fix Low Risk Issues"
            }
        }

    def load_test_logs(self):
        try:
            with open("test_logs.json", "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading test logs: {e}")
            return []

    def simulate_monitoring(self):
        logs = self.load_test_logs()
        if not logs:
            logging.error("No logs found to monitor")
            return

        logging.info("Starting log monitoring simulation...")
        
        for log in logs:
            # Simulate real-time log processing
            time.sleep(2)  # Simulate time between logs
            
            # Format log message
            log_message = f"[{log['timestamp']}] [{log['level']}] {log['message']}"
            logging.info(f"Processing log: {log_message}")
            
            # Analyze log
            analysis = self.log_analyzer.analyze_log(log_message)
            
            if not analysis:
                continue
            
            # Log the analysis
            logging.info(f"Analysis: {analysis}")
            
            # Get resolution steps
            resolution_steps = self.log_analyzer.get_resolution_steps(analysis)
            
            # Execute automated actions if severity is HIGH
            if analysis["severity"] == "HIGH":
                for step in resolution_steps:
                    logging.info(f"Executing action: {step['action']}")
                    # In a real scenario, this would execute actual actions
                    time.sleep(1)  # Simulate action execution
            
            # Send notification for medium/high severity issues
            if analysis["severity"] in ["MEDIUM", "HIGH"]:
                self.email_notifier.send_alert(
                    self.app_data,
                    f"{analysis['severity']} severity issue detected",
                    f"Analysis: {analysis['ai_analysis']}\nCategory: {analysis['category']}"
                )
                logging.info(f"Alert sent for {analysis['severity']} severity issue")

if __name__ == "__main__":
    monitor = TestMonitor()
    monitor.simulate_monitoring() 