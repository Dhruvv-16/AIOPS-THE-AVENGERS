import time
import random
import logging
from datetime import datetime
import os

def generate_log_entry(step, error_type):
    """Generate log entries based on the current step in the error scenario"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if error_type == "database":
        if step == 0:  # Normal operation
            return f"{timestamp} INFO: Database connection stable. Response time: {random.randint(50, 100)}ms"
        elif step == 1:  # Warning signs
            return f"{timestamp} WARNING: Database connection pool at {random.randint(75, 85)}% capacity"
        elif step == 2:  # Error occurs
            return f"{timestamp} ERROR: Database connection failed. Error code: DB-{random.randint(1000, 9999)}"
        elif step == 3:  # Auto-resolution attempt
            return f"{timestamp} INFO: Attempting database service restart..."
        elif step == 4:  # Resolution steps
            return f"{timestamp} INFO: Restarting database service..."
        elif step == 5:  # Recovery
            return f"{timestamp} INFO: Database service restarted successfully"
        elif step == 6:  # Back to normal
            return f"{timestamp} INFO: Database connection restored. Response time: {random.randint(50, 100)}ms"

    elif error_type == "memory":
        if step == 0:  # Normal operation
            return f"{timestamp} INFO: Memory usage normal. Current usage: {random.randint(30, 50)}%"
        elif step == 1:  # Warning signs
            return f"{timestamp} WARNING: Memory usage increasing. Current: {random.randint(65, 75)}%"
        elif step == 2:  # Error occurs
            return f"{timestamp} ERROR: Memory allocation failed. Out of memory error"
        elif step == 3:  # Auto-resolution attempt
            return f"{timestamp} INFO: Initiating memory cleanup..."
        elif step == 4:  # Resolution steps
            return f"{timestamp} INFO: Clearing cache and unused resources..."
        elif step == 5:  # Recovery
            return f"{timestamp} INFO: Memory cleanup completed successfully"
        elif step == 6:  # Back to normal
            return f"{timestamp} INFO: Memory usage normalized. Current: {random.randint(30, 50)}%"

    elif error_type == "api":
        if step == 0:  # Normal operation
            return f"{timestamp} INFO: API endpoints responding normally. Latency: {random.randint(100, 200)}ms"
        elif step == 1:  # Warning signs
            return f"{timestamp} WARNING: API response time increasing. Current: {random.randint(500, 800)}ms"
        elif step == 2:  # Error occurs
            return f"{timestamp} ERROR: API service unavailable. Status: 503"
        elif step == 3:  # Auto-resolution attempt
            return f"{timestamp} INFO: Attempting API service recovery..."
        elif step == 4:  # Resolution steps
            return f"{timestamp} INFO: Restarting API service and load balancer..."
        elif step == 5:  # Recovery
            return f"{timestamp} INFO: API service restored. Status: 200"
        elif step == 6:  # Back to normal
            return f"{timestamp} INFO: API endpoints responding normally. Latency: {random.randint(100, 200)}ms"

def main():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )

    print("Starting log generation...")
    print("Logs will be written to logs/app.log")
    print("This will simulate multiple error scenarios with automatic resolution")
    print("Press Ctrl+C to stop")

    error_types = ["database", "memory", "api"]
    current_error = 0
    step = 0

    try:
        while True:
            # Generate log entry based on current step and error type
            log_entry = generate_log_entry(step, error_types[current_error])
            logging.info(log_entry)
            print(log_entry)

            # Progress through the error scenario
            if step < 6:
                step += 1
                time.sleep(3)  # Wait 3 seconds between steps
            else:
                step = 0
                current_error = (current_error + 1) % len(error_types)  # Cycle through error types
                time.sleep(5)  # Wait 5 seconds before next error scenario

    except KeyboardInterrupt:
        print("\nStopping log generation...")

if __name__ == "__main__":
    main() 