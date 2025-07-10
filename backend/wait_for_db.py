#!/usr/bin/env python
"""
Script to wait for database to be available.
"""

import os
import time
import socket
from time import sleep

# Get database connection info from environment variables
db_host = os.environ.get("POSTGRES_HOST", "localhost")
db_port = int(os.environ.get("POSTGRES_PORT", "5432"))

# Maximum number of attempts
max_attempts = 30
attempt = 0

print(f"Waiting for PostgreSQL at {db_host}:{db_port}...")

# Try to connect to the database
while attempt < max_attempts:
    try:
        # Try creating a socket connection to check if postgres is accepting connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((db_host, db_port))
            if result == 0:
                print("Database is available!")
                exit(0)
    except Exception as e:
        print(
            f"Attempt {attempt + 1}/{max_attempts}: Database not available yet - {str(e)}"
        )

    attempt += 1
    print(f"Attempt {attempt}/{max_attempts}: Waiting for database...")
    sleep(2)

print("Could not connect to database after maximum attempts. Exiting...")
exit(1)
