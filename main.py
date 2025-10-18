# EdgeOne SecTest - Main Entry Point
# This file serves as the main entry point for deployment platforms

import subprocess
import sys
import os

if __name__ == "__main__":
    # Set environment variables for Streamlit
    os.environ["STREAMLIT_SERVER_PORT"] = os.environ.get("PORT", "8501")
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    
    # Run the main application
    subprocess.run([sys.executable, "-m", "streamlit", "run", "pentestweb.py", 
                   "--server.port", os.environ.get("PORT", "8501"),
                   "--server.address", "0.0.0.0"])
