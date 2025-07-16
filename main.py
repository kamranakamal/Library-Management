#!/usr/bin/env python3
"""
Library Management System
Main application entry point
Version: 1.0.5
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import DatabaseManager
from gui.main_window import MainWindow


def main():
    """Main application entry point"""
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        
        # Create main application window
        root = tk.Tk()
        MainWindow(root)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
