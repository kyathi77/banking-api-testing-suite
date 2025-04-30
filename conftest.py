import pytest
import subprocess
import time
import os
import signal
import requests

server_process = None

def wait_for_server(url, max_retries=5, retry_delay=1):
    """Wait for server to be ready"""
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            if response.status_code == 404:  # API running but route not found
                return True
            return True
        except requests.ConnectionError:
            retries += 1
            time.sleep(retry_delay)
    return False

@pytest.fixture(scope="session", autouse=True)
def setup_server():
    """Start the mock API server before tests and stop it after"""
    global server_process
    
    # Start server
    server_process = subprocess.Popen(["python", "mock_banking_api.py"])
    
    # Wait for server to start
    wait_for_server("http://localhost:5000/")
    
    yield
    
    # Stop server after tests
    server_process.send_signal(signal.SIGTERM)
    server_process.wait()