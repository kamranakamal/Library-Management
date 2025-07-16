"""
Main application window
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import (
    APP_NAME, APP_VERSION, APP_AUTHOR, WINDOW_WIDTH, WINDOW_HEIGHT, BACKGROUND_COLOR
)
from gui.student_management import StudentManagementFrame
from gui.timeslot_management import TimeslotManagementFrame
from gui.analytics import AnalyticsFrame
from gui.book_management import BookManagementFrame


class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_menu()
        self.create_main_interface()
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=BACKGROUND_COLOR)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (WINDOW_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (WINDOW_HEIGHT // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        # Configure window icon (if available)
        try:
            self.root.iconbitmap('icon.ico')
        except Exception:
            pass
    
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_command(label="Restore Database", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Export Data", command=self.export_data)
        tools_menu.add_command(label="WhatsApp Automation", command=self.open_whatsapp_automation)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Create main interface with tabs"""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Student Management tab
        self.student_frame = StudentManagementFrame(self.notebook)
        self.notebook.add(self.student_frame, text="Student Management")
        
        # Timeslot Management tab
        self.timeslot_frame = TimeslotManagementFrame(self.notebook)
        self.notebook.add(self.timeslot_frame, text="Timeslot Management")
        
        # Book Management tab
        self.book_frame = BookManagementFrame(self.notebook)
        self.notebook.add(self.book_frame, text="Book Management")
        
        # Analytics tab
        self.analytics_frame = AnalyticsFrame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytics")
        
        # Status bar
        self.create_status_bar()
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side='bottom', fill='x')
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side='left', padx=5, pady=2)
        
        # Add current date/time
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.time_label = ttk.Label(self.status_bar, text=current_time)
        self.time_label.pack(side='right', padx=5, pady=2)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.after(3000, lambda: self.status_label.config(text="Ready"))
    
    def backup_database(self):
        """Backup database"""
        try:
            from tkinter import filedialog
            from utils.database_manager import DatabaseOperations
            
            # Ask user for backup location
            backup_path = filedialog.asksaveasfilename(
                title="Save Database Backup",
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            
            if backup_path:
                db_ops = DatabaseOperations()
                success, message = db_ops.backup_database(backup_path)
                
                if success:
                    messagebox.showinfo("Backup", "Database backup created successfully!")
                    self.update_status("Database backed up")
                else:
                    messagebox.showerror("Backup Error", message)
        
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to backup database: {str(e)}")
    
    def restore_database(self):
        """Restore database from backup"""
        try:
            from tkinter import filedialog
            from utils.database_manager import DatabaseOperations
            
            # Ask user to select backup file
            backup_path = filedialog.askopenfilename(
                title="Select Database Backup",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            
            if backup_path:
                # Confirm restoration
                confirm = messagebox.askyesno(
                    "Restore Database",
                    "This will replace the current database. Are you sure?",
                    icon='warning'
                )
                
                if confirm:
                    db_ops = DatabaseOperations()
                    success, message = db_ops.restore_database(backup_path)
                    
                    if success:
                        messagebox.showinfo("Restore", "Database restored successfully!")
                        self.update_status("Database restored")
                        # Refresh all frames
                        self.refresh_all_frames()
                    else:
                        messagebox.showerror("Restore Error", message)
        
        except Exception as e:
            messagebox.showerror("Restore Error", f"Failed to restore database: {str(e)}")
    
    def export_data(self):
        """Export data to Excel"""
        try:
            from utils.excel_exporter import ExcelExporter
            
            exporter = ExcelExporter()
            success, filepath = exporter.export_all_data()
            
            if success:
                messagebox.showinfo("Export", f"Data exported successfully to:\n{filepath}")
                self.update_status("Data exported to Excel")
            else:
                messagebox.showerror("Export Error", filepath)
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def open_whatsapp_automation(self):
        """Open WhatsApp automation window"""
        try:
            from gui.whatsapp_window import WhatsAppWindow
            WhatsAppWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open WhatsApp automation: {str(e)}")
    
    def refresh_all_frames(self):
        """Refresh all frames after database changes"""
        try:
            if hasattr(self.student_frame, 'refresh'):
                self.student_frame.refresh()
            if hasattr(self.timeslot_frame, 'refresh'):
                self.timeslot_frame.refresh()
            if hasattr(self.book_frame, 'refresh'):
                self.book_frame.refresh()
            if hasattr(self.analytics_frame, 'refresh'):
                self.analytics_frame.refresh()
        except Exception as e:
            print(f"Error refreshing frames: {e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
{APP_NAME}
Version {APP_VERSION}

A comprehensive library management system for managing:
• Student subscriptions and seat assignments
• Timeslot bookings with overlap detection
• Book borrowing and returns
• Analytics and reporting
• WhatsApp automation for notifications

Built with Python, SQLite, and Tkinter

© 2025 {APP_AUTHOR}
        """.strip()
        
        messagebox.showinfo("About", about_text)
