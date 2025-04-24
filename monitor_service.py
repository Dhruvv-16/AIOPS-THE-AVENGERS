import schedule
import time
import json
import logging
from datetime import datetime
import requests
from config import CONFIG_PATH, LOG_DIR, LOG_CHECK_INTERVAL
from log_analyzer import LogAnalyzer
from notifications import EmailNotifier

class MonitoringService:
    def __init__(self):
        self.log_analyzer = LogAnalyzer()
        self.email_notifier = EmailNotifier()
        self.apps = self._load_apps()
        
        # Configure logging
        logging.basicConfig(
            filename=f"{LOG_DIR}/monitoring_service.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _load_apps(self):
        """Load registered apps from configuration"""
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading apps: {str(e)}")
            return []

    def fetch_logs(self, app):
        """Fetch logs from the application"""
        try:
            if app.get("Log Source") == "Datadog":
                return self._fetch_datadog_logs(app)
            elif app.get("Log Source") == "ELK":
                return self._fetch_elk_logs(app)
            else:
                return self._fetch_custom_logs(app)
        except Exception as e:
            logging.error(f"Error fetching logs for {app['App Name']}: {str(e)}")
            return []

    def _fetch_datadog_logs(self, app):
        # Implement Datadog log fetching
        pass

    def _fetch_elk_logs(self, app):
        # Implement ELK log fetching
        pass

    def _fetch_custom_logs(self, app):
        """Fetch logs from custom API endpoint"""
        try:
            response = requests.get(f"{app['API URL']}/logs", timeout=10)
            if response.status_code == 200:
                return response.json()
            logging.error(f"Error fetching logs from {app['App Name']}: {response.status_code}")
            return []
        except Exception as e:
            logging.error(f"Exception fetching logs from {app['App Name']}: {str(e)}")
            return []

    def execute_action(self, app, action):
        """Execute automated actions based on analysis"""
        try:
            if action["action"] == "restart_database":
                # Implement database restart logic
                logging.info(f"Restarting database for {app['App Name']}")
                # Add your database restart implementation here
                return True
            elif action["action"] == "clear_cache":
                # Implement cache clearing logic
                logging.info(f"Clearing cache for {app['App Name']}")
                # Add your cache clearing implementation here
                return True
            elif action["action"] == "scale_resources":
                # Implement resource scaling logic
                logging.info(f"Scaling resources for {app['App Name']}")
                # Add your resource scaling implementation here
                return True
            return False
        except Exception as e:
            logging.error(f"Error executing action {action['action']}: {str(e)}")
            return False

    def monitor_app(self, app):
        """Monitor a single application"""
        logging.info(f"Monitoring {app['App Name']}...")
        
        # Fetch logs
        logs = self.fetch_logs(app)
        
        for log in logs:
            # Analyze log
            analysis = self.log_analyzer.analyze_log(log)
            
            if not analysis:
                continue
                
            # Log the analysis
            logging.info(f"Analysis for {app['App Name']}: {json.dumps(analysis)}")
            
            # Get resolution steps
            resolution_steps = self.log_analyzer.get_resolution_steps(analysis)
            
            # Execute automated actions if severity is HIGH
            if analysis["severity"] == "HIGH":
                for step in resolution_steps:
                    if self.execute_action(app, step):
                        # Notify about the automated action
                        self.email_notifier.send_alert(
                            app,
                            f"Automated action taken: {step['action']}",
                            f"Analysis: {analysis['ai_analysis']}\nAction: {step['description']}"
                        )
            
            # Send notification for medium/high severity issues
            if analysis["severity"] in ["MEDIUM", "HIGH"]:
                self.email_notifier.send_alert(
                    app,
                    f"{analysis['severity']} severity issue detected",
                    f"Analysis: {analysis['ai_analysis']}\nCategory: {analysis['category']}"
                )

    def start_monitoring(self):
        """Start the monitoring service"""
        logging.info("Starting monitoring service...")
        
        # Schedule monitoring for each app
        for app in self.apps:
            schedule.every(LOG_CHECK_INTERVAL).seconds.do(self.monitor_app, app)
        
        # Run continuously
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    service = MonitoringService()
    service.start_monitoring() 