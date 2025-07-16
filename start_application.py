#!/usr/bin/env python3
"""
Library Management System Launcher
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project directory to path
project_dir = "/home/kamran/Documents/Library Management"
sys.path.insert(0, project_dir)

def main():
    try:
        # Check if database exists
        db_path = os.path.join(project_dir, "data", "library.db")
        if not os.path.exists(db_path):
            print("Database not found. Please run setup.py first.")
            return
        
        # Import and start application
        from config.database import DatabaseManager
        from gui.main_window import MainWindow
        
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        
        # Create and start GUI
        root = tk.Tk()
        MainWindow(root)
        root.mainloop()
        
    except ImportError as e:
        error_msg = f"Missing dependency: {e}\n\nPlease install required packages:\npip install -r requirements.txt"
        try:
            messagebox.showerror("Import Error", error_msg)
        except Exception as e:
            print(f"{error_msg}\nAdditional details: {e}")
    except Exception as e:
        error_msg = f"Application error: {e}"
        try:
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            print(f"{error_msg}\nAdditional details: {e}")

if __name__ == "__main__":
    main()
