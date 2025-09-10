#!/usr/bin/env python3
"""
JarvisX - Full Advanced Desktop AI Assistant
Main entry point for the application
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Ensure required directories exist
for directory in ['logs', 'temp', 'temp/models']:
    Path(directory).mkdir(exist_ok=True)

def main():
    """Main application entry point"""
    try:
        from core.app import JarvisXApp
        from PyQt5.QtWidgets import QApplication
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("JarvisX")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("JarvisX")
        
        # Create and show main window
        window = JarvisXApp()
        window.show()
        
        # Start event loop
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error starting JarvisX: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()