#!/usr/bin/env python3
import logging
import os

print(f"Current working directory: {os.getcwd()}")
print(f"Python version: {os.sys.version}")

# Test basic logging
logging.basicConfig(
    filename='/home/perplexity/Desktop/GitHub/chainlit/test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

print("About to write to log...")
logging.info("This is a test log message")
print("Log message written")

# Check if file exists
log_file = '/home/perplexity/Desktop/GitHub/chainlit/test.log'
if os.path.exists(log_file):
    print(f"✓ Log file created: {log_file}")
    with open(log_file, 'r') as f:
        content = f.read()
        print(f"Log content: {content}")
else:
    print(f"✗ Log file NOT created: {log_file}")

# Also try relative path
logging.basicConfig(
    filename='test2.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True  # This forces reconfiguration
)

logging.info("This is a second test log message")

if os.path.exists('test2.log'):
    print("✓ Relative path log file created: test2.log")
else:
    print("✗ Relative path log file NOT created")
