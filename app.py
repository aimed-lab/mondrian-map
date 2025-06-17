"""
Mondrian Map Explorer - Main Application Entry Point

This file serves as the main entry point for backward compatibility.
The actual application logic has been moved to apps/streamlit_app.py
with a proper modular structure.

For development and new deployments, use:
    streamlit run apps/streamlit_app.py

This file is kept for backward compatibility with existing deployments.
"""

import sys
from pathlib import Path

# Add the apps directory to the path
sys.path.append(str(Path(__file__).parent / "apps"))

# Import and run the main application
from streamlit_app import main

if __name__ == "__main__":
    main()
