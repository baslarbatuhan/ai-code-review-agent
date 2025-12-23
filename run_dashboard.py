"""Simple script to run the Streamlit dashboard."""
import subprocess
import sys
import os

if __name__ == "__main__":
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "main.py")
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        dashboard_path,
        "--server.port",
        "8501",
        "--server.address",
        "0.0.0.0",
    ])

