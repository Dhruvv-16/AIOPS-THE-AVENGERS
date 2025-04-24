from log_analyzer import analyze_log_line  # Assuming this is where analyze_log_line is defined

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import time

# Email notification function (same as before)
def send_email(subject, body, to_email):
    from_email = "your_email@example.com"  # Your email address (e.g., Gmail)
    from_password = "your_app_password"  # Your app-specific password for security

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # SMTP server setup (using Gmail as an example)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.close()

        print("📧 Email sent successfully!")
    except Exception as e:
        print(f"⚠️ Failed to send email: {e}")

# Load the registered apps and their configuration
def load_registered_apps():
    try:
        with open("registered_apps.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("No registered apps found.")
        return []

# Simulating log collection for monitoring
def simulate_log_collection(app_config):
    return [
        f"INFO {app_config['App Name']} started successfully.",
        f"WARNING {app_config['App Name']} memory usage high.",
        f"ERROR {app_config['App Name']} failed to connect to database.",
    ]

# Collect the registered apps
def get_registered_apps():
    return load_registered_apps()

if __name__ == "__main__":
    # Get all registered apps
    registered_apps = get_registered_apps()

    for app_config in registered_apps:
        print(f"\nMonitoring app: {app_config['App Name']} at {app_config['App URL']}...\n")

        logs = simulate_log_collection(app_config)

        for log in logs:
            print(f"→ {log}")
            try:
                result = analyze_log_line(log)
                print("🧠 AI Analysis:")
                print(result)

                # Check if the log is of type ERROR or WARNING
                if "ERROR" in result or "WARNING" in result:
                    subject = f"Alert: {app_config['App Name']} Log Issue"
                    body = f"An issue was detected in the log:\n\n{result}\n\nLog: {log}"

                    # Send email to the client's email address
                    send_email(subject, body, app_config['Client Email'])
            except Exception as e:
                print(f"⚠️ Failed to analyze log: {e}")
            time.sleep(1)  # Avoid spamming API

    print("---\n")
