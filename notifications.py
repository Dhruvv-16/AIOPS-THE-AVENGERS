import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, LOG_DIR

class EmailNotifier:
    def __init__(self):
        self.host = EMAIL_HOST
        self.port = EMAIL_PORT
        self.username = EMAIL_USERNAME
        self.password = EMAIL_PASSWORD
        
        # Configure logging
        logging.basicConfig(
            filename=f"{LOG_DIR}/notifications.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def send_alert(self, app, subject, body):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = app.get('Client Email', self.username)  # Fallback to admin email
            msg['Subject'] = f"[{app['App Name']}] {subject}"

            # Create HTML body
            html_body = f"""
            <html>
                <body>
                    <h2>Alert for {app['App Name']}</h2>
                    <p><strong>Subject:</strong> {subject}</p>
                    <p><strong>Details:</strong></p>
                    <pre>{body}</pre>
                    <hr>
                    <p>This is an automated message from your AI Log Monitor.</p>
                </body>
            </html>
            """

            msg.attach(MIMEText(html_body, 'html'))

            # Connect to SMTP server and send email
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logging.info(f"Alert sent successfully to {msg['To']}")
            return True

        except Exception as e:
            logging.error(f"Failed to send alert: {str(e)}")
            return False

    def send_summary(self, app, summary_data):
        """Send daily/weekly summary"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = app.get('Client Email', self.username)
            msg['Subject'] = f"[{app['App Name']}] Monitoring Summary Report"

            # Create HTML summary
            html_body = f"""
            <html>
                <body>
                    <h2>Monitoring Summary for {app['App Name']}</h2>
                    <h3>Period: {summary_data['period']}</h3>
                    
                    <h4>Statistics:</h4>
                    <ul>
                        <li>Total Logs Analyzed: {summary_data['total_logs']}</li>
                        <li>High Severity Issues: {summary_data['high_severity']}</li>
                        <li>Medium Severity Issues: {summary_data['medium_severity']}</li>
                        <li>Automated Actions Taken: {summary_data['automated_actions']}</li>
                    </ul>
                    
                    <h4>Top Issues:</h4>
                    <ul>
                        {''.join([f"<li>{issue}</li>" for issue in summary_data['top_issues']])}
                    </ul>
                    
                    <h4>Recommendations:</h4>
                    <ul>
                        {''.join([f"<li>{rec}</li>" for rec in summary_data['recommendations']])}
                    </ul>
                    
                    <hr>
                    <p>This is an automated summary from your AI Log Monitor.</p>
                </body>
            </html>
            """

            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logging.info(f"Summary sent successfully to {msg['To']}")
            return True

        except Exception as e:
            logging.error(f"Failed to send summary: {str(e)}")
            return False 