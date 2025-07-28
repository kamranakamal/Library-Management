"""
WhatsApp automation window
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from utils.whatsapp_automation import WhatsAppAutomation
from models.subscription import Subscription


class WhatsAppWindow:
    """WhatsApp automation window"""
    
    def __init__(self, parent):
        self.parent = parent
        self.whatsapp = WhatsAppAutomation()
        self.setup_window()
    
    def setup_window(self):
        """Setup WhatsApp automation window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("WhatsApp Automation")
        self.window.geometry("900x700")
        self.window.minsize(800, 600)  # Set minimum size
        self.window.grab_set()  # Make window modal
        
        # Configure window to be resizable
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        
        # Bind keyboard shortcuts
        self.window.bind('<Control-i>', lambda e: self.initialize_whatsapp())
        self.window.bind('<Control-r>', lambda e: self.check_status())
        self.window.bind('<F5>', lambda e: self.force_status_check())
        self.window.bind('<Control-q>', lambda e: self.close_whatsapp())
        
        # Allow window to be closed properly
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Start periodic status checker
        self.start_status_monitor()
        
        # Create main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Create notebook for different functions
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Login tab
        self.create_login_tab(notebook)
        
        # Reminders tab
        self.create_reminders_tab(notebook)
        
        # Subscription cancellations tab
        self.create_cancellations_tab(notebook)
        
        # Custom messages tab
        self.create_custom_messages_tab(notebook)
    
    def start_status_monitor(self):
        """Start periodic status monitoring"""
        self.last_status = None
        self.status_check_count = 0
        self.connection_retry_count = 0
        self.is_initializing = False  # Track initialization state
        
        def monitor():
            if hasattr(self, 'window') and self.window.winfo_exists():
                # Only check if we have a driver initialized and not currently initializing
                if self.whatsapp.driver and not self.is_initializing:
                    # First check if driver is still valid
                    if not self.whatsapp.is_driver_valid():
                        if self.whatsapp.is_logged_in:
                            self.whatsapp.is_logged_in = False
                            self.status_var.set("Browser crashed")
                            self.log_message("❌ Browser session crashed")
                            self.last_status = "crashed"
                    else:
                        try:
                            # Use the comprehensive status check
                            is_logged_in, status_message = self.whatsapp.check_login_status()
                            
                            # Only log status changes, not repeated same status
                            current_status = "connected" if is_logged_in else "disconnected"
                            
                            if current_status != self.last_status:
                                if is_logged_in and not self.whatsapp.is_logged_in:
                                    self.whatsapp.is_logged_in = True
                                    self.status_var.set("Connected")
                                    self.log_message("✅ Login detected - WhatsApp Web connected!")
                                    self.connection_retry_count = 0
                                elif not is_logged_in:
                                    if "QR code" in status_message:
                                        if self.whatsapp.is_logged_in:
                                            self.whatsapp.is_logged_in = False
                                            self.status_var.set("Waiting for QR scan")
                                            self.log_message("📱 Please scan QR code to login")
                                            self.connection_retry_count = 0
                                    elif "loading" in status_message.lower() or "page loading" in status_message.lower():
                                        # Don't change status for loading states if we think we're connected
                                        if not self.whatsapp.is_logged_in:
                                            self.status_var.set("Loading...")
                                    else:
                                        # Only report connection issues after multiple consecutive failures
                                        self.connection_retry_count += 1
                                        if self.connection_retry_count >= 5:  # 5 consecutive failures = 25 seconds
                                            if self.whatsapp.is_logged_in:
                                                self.whatsapp.is_logged_in = False
                                                self.status_var.set("Connection issues")
                                                self.log_message(f"⚠️ Multiple connection check failures: {status_message}")
                                        # Don't immediately report as disconnected - wait for multiple failures
                                                # Don't auto-reconnect if initializing to avoid conflicts
                                                if not self.is_initializing:
                                                    threading.Thread(target=self.initialize_whatsapp, daemon=True).start()
                                
                                self.last_status = current_status
                                self.status_check_count += 1
                                
                        except Exception as e:
                            # Handle driver errors gracefully
                            error_str = str(e).lower()
                            if any(error in error_str for error in ["session deleted", "chrome not reachable", "connection refused"]):
                                if self.whatsapp.is_logged_in:
                                    self.whatsapp.is_logged_in = False
                                    self.status_var.set("Browser crashed")
                                    self.log_message("❌ Browser session ended")
                                    self.last_status = "crashed"
                elif not self.whatsapp.driver and not self.is_initializing:
                    # No driver and not initializing - show as not connected
                    if self.last_status != "no_driver":
                        self.status_var.set("Not initialized")
                        self.last_status = "no_driver"
                
                # Schedule next check with longer interval to reduce conflicts
                self.window.after(15000, monitor)  # Check every 15 seconds to reduce conflicts
        
        # Start the monitor
        self.window.after(2000, monitor)  # Start after 2 seconds
    
    def create_login_tab(self, parent):
        """Create WhatsApp login tab"""
        login_frame = ttk.Frame(parent)
        parent.add(login_frame, text="Login")
        
        # Configure login frame grid
        login_frame.rowconfigure(4, weight=1)  # Log frame gets extra space
        login_frame.columnconfigure(0, weight=1)
        
        # Instructions
        instructions = """
WhatsApp Web Login Instructions:

1. Click 'Initialize WhatsApp' to open WhatsApp Web
2. Scan the QR code with your phone's WhatsApp
3. Wait for login confirmation
4. Once logged in, you can send automated messages

Note: Keep this window open while using WhatsApp automation.
        """.strip()
        
        instructions_frame = ttk.Frame(login_frame)
        instructions_frame.grid(row=0, column=0, sticky='ew', pady=(10, 20), padx=10)
        instructions_frame.columnconfigure(0, weight=1)
        
        # Add keyboard shortcuts info
        shortcuts_text = "Keyboard shortcuts: Ctrl+I (Initialize) | Ctrl+R (Check Status) | F5 (Force Refresh) | Ctrl+Q (Close WhatsApp)"
        shortcuts_frame = ttk.Frame(instructions_frame)
        shortcuts_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(shortcuts_frame, text=shortcuts_text, font=('Arial', 8), 
                 foreground='gray').pack(fill='x')
        
        # Status display
        self.status_var = tk.StringVar(value="Not connected")
        status_frame = ttk.LabelFrame(login_frame, text="Connection Status", padding=10)
        status_frame.grid(row=1, column=0, sticky='ew', pady=10, padx=10)
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w')
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 10, 'bold'))
        status_label.grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        # Buttons - Main controls
        button_frame = ttk.LabelFrame(login_frame, text="Main Controls", padding=10)
        button_frame.grid(row=2, column=0, sticky='ew', pady=10, padx=10)
        button_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        init_btn = ttk.Button(button_frame, text="Initialize WhatsApp", command=self.initialize_whatsapp)
        init_btn.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.create_tooltip(init_btn, "Start WhatsApp Web and prepare for automation")
        
        status_btn = ttk.Button(button_frame, text="Check Status", command=self.check_status)
        status_btn.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.create_tooltip(status_btn, "Check current WhatsApp connection status")
        
        refresh_btn = ttk.Button(button_frame, text="Force Refresh", command=self.force_status_check)
        refresh_btn.grid(row=0, column=2, sticky='ew', padx=5, pady=5)
        self.create_tooltip(refresh_btn, "Force a detailed status check with logging")
        
        close_btn = ttk.Button(button_frame, text="Close WhatsApp", command=self.close_whatsapp)
        close_btn.grid(row=0, column=3, sticky='ew', padx=5, pady=5)
        self.create_tooltip(close_btn, "Close WhatsApp Web browser session")
        
        # Diagnostic frame
        diagnostic_frame = ttk.LabelFrame(login_frame, text="Diagnostic Tools", padding=10)
        diagnostic_frame.grid(row=3, column=0, sticky='ew', pady=10, padx=10)
        diagnostic_frame.columnconfigure((0, 1), weight=1)
        
        test_btn = ttk.Button(diagnostic_frame, text="Test Chrome Installation", command=self.test_chrome)
        test_btn.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.create_tooltip(test_btn, "Check if Chrome is properly installed")
        
        clear_btn = ttk.Button(diagnostic_frame, text="Clear Session Data", command=self.clear_session)
        clear_btn.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.create_tooltip(clear_btn, "Clear saved login data (requires re-scanning QR code)")
        
        # Log display
        log_frame = ttk.LabelFrame(login_frame, text="Activity Log", padding=10)
        log_frame.grid(row=4, column=0, sticky='nsew', pady=10, padx=10)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', wrap='word')
        self.log_text.grid(row=0, column=0, sticky='nsew')
    
    def create_reminders_tab(self, parent):
        """Create subscription reminders tab"""
        reminders_frame = ttk.Frame(parent)
        parent.add(reminders_frame, text="Subscription Reminders")
        
        # Configure frame grid
        reminders_frame.rowconfigure(2, weight=1)  # Preview gets extra space
        reminders_frame.columnconfigure(0, weight=1)
        
        # Options frame
        options_frame = ttk.LabelFrame(reminders_frame, text="Reminder Options", padding=10)
        options_frame.grid(row=0, column=0, sticky='ew', pady=10, padx=10)
        options_frame.columnconfigure(0, weight=1)
        
        # Days before expiry
        days_label_frame = ttk.Frame(options_frame)
        days_label_frame.pack(fill='x', pady=5)
        
        ttk.Label(days_label_frame, text="Send reminders for subscriptions expiring in:").pack(anchor='w')
        
        days_input_frame = ttk.Frame(options_frame)
        days_input_frame.pack(fill='x', pady=5)
        
        self.reminder_days_var = tk.StringVar(value="7")
        days_spinbox = tk.Spinbox(days_input_frame, from_=1, to=30, textvariable=self.reminder_days_var, 
                                 width=10, font=('Arial', 10))
        days_spinbox.pack(side='left')
        ttk.Label(days_input_frame, text="days").pack(side='left', padx=5)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(reminders_frame, text="Expiring Subscriptions Preview", padding=10)
        preview_frame.grid(row=2, column=0, sticky='nsew', pady=10, padx=10)
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        
        # Create frame for treeview and scrollbar
        tree_frame = ttk.Frame(preview_frame)
        tree_frame.grid(row=0, column=0, sticky='nsew')
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Expiring subscriptions tree with selection
        columns = ('Select', 'Student', 'Mobile', 'Seat', 'Timeslot', 'Expiry Date', 'Days Left')
        self.reminder_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        
        # Store selection state for each item
        self.reminder_selections = {}
        
        for col in columns:
            self.reminder_tree.heading(col, text=col)
            if col == 'Select':
                self.reminder_tree.column(col, width=60, minwidth=60)
            else:
                self.reminder_tree.column(col, width=120, minwidth=80)
        
        # Bind click event for checkbox functionality
        self.reminder_tree.bind('<Button-1>', self.on_reminder_tree_click)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.reminder_tree.yview)
        self.reminder_tree.configure(yscrollcommand=scrollbar.set)
        
        self.reminder_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Buttons
        button_frame = ttk.Frame(reminders_frame)
        button_frame.grid(row=3, column=0, sticky='ew', pady=10, padx=10)
        button_frame.columnconfigure((0, 1), weight=1)
        
        load_btn = ttk.Button(button_frame, text="Load Expiring Subscriptions", 
                             command=self.load_expiring_subscriptions)
        load_btn.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.create_tooltip(load_btn, "Load subscriptions that will expire soon")
        
        select_all_btn = ttk.Button(button_frame, text="Select All", 
                                   command=self.select_all_reminders)
        select_all_btn.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.create_tooltip(select_all_btn, "Select all students for reminders")
        
        deselect_all_btn = ttk.Button(button_frame, text="Deselect All", 
                                     command=self.deselect_all_reminders)
        deselect_all_btn.grid(row=0, column=2, sticky='ew', padx=5, pady=5)
        self.create_tooltip(deselect_all_btn, "Deselect all students")
        
        send_btn = ttk.Button(button_frame, text="Send Reminders", 
                             command=self.send_subscription_reminders)
        send_btn.grid(row=0, column=3, sticky='ew', padx=5, pady=5)
        self.create_tooltip(send_btn, "Send reminder messages to selected students only")
    
    def create_cancellations_tab(self, parent):
        """Create subscription cancellations tab"""
        cancellations_frame = ttk.Frame(parent)
        parent.add(cancellations_frame, text="Subscription Cancellations")
        
        # Configure frame grid
        cancellations_frame.rowconfigure(3, weight=1)  # Preview gets extra space
        cancellations_frame.columnconfigure(0, weight=1)
        
        # Instructions
        instructions = """
This feature sends cancellation notifications to students whose subscriptions have expired.
The message includes readmission contact information and encourages them to return.
        """.strip()
        
        instructions_frame = ttk.Frame(cancellations_frame)
        instructions_frame.grid(row=0, column=0, sticky='ew', pady=10, padx=10)
        instructions_frame.columnconfigure(0, weight=1)
        
        ttk.Label(instructions_frame, text=instructions, justify='left', 
                 font=('Arial', 10), wraplength=800).pack(fill='x')
        
        # Options frame
        options_frame = ttk.LabelFrame(cancellations_frame, text="Cancellation Options", padding=10)
        options_frame.grid(row=1, column=0, sticky='ew', pady=10, padx=10)
        options_frame.columnconfigure(0, weight=1)
        
        # Days since expiry
        days_label_frame = ttk.Frame(options_frame)
        days_label_frame.pack(fill='x', pady=5)
        
        ttk.Label(days_label_frame, text="Send cancellations for subscriptions expired within:").pack(anchor='w')
        
        days_input_frame = ttk.Frame(options_frame)
        days_input_frame.pack(fill='x', pady=5)
        
        self.cancellation_days_var = tk.StringVar(value="7")
        days_spinbox = tk.Spinbox(days_input_frame, from_=1, to=30, textvariable=self.cancellation_days_var, 
                                 width=10, font=('Arial', 10))
        days_spinbox.pack(side='left')
        ttk.Label(days_input_frame, text="days").pack(side='left', padx=5)
        
        # Warning frame
        warning_frame = ttk.LabelFrame(options_frame, text="⚠️ Important Warning", padding=10)
        warning_frame.pack(fill='x', pady=10)
        
        warning_text = "This will send cancellation messages to expired students. Use carefully!"
        warning_label = ttk.Label(warning_frame, text=warning_text, foreground='red', 
                                 font=('Arial', 10, 'bold'), wraplength=700)
        warning_label.pack(fill='x')
        
        # Preview frame
        preview_frame = ttk.LabelFrame(cancellations_frame, text="Expired Subscriptions Preview", padding=10)
        preview_frame.grid(row=3, column=0, sticky='nsew', pady=10, padx=10)
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        
        # Create frame for treeview and scrollbar
        tree_frame = ttk.Frame(preview_frame)
        tree_frame.grid(row=0, column=0, sticky='nsew')
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Expired subscriptions tree
        columns = ('Student', 'Mobile', 'Seat', 'Timeslot', 'Expired Date', 'Days Expired')
        self.cancellation_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.cancellation_tree.heading(col, text=col)
            self.cancellation_tree.column(col, width=120, minwidth=80)
        
        scrollbar2 = ttk.Scrollbar(tree_frame, orient='vertical', command=self.cancellation_tree.yview)
        self.cancellation_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.cancellation_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar2.grid(row=0, column=1, sticky='ns')
        
        # Buttons
        button_frame = ttk.Frame(cancellations_frame)
        button_frame.grid(row=4, column=0, sticky='ew', pady=10, padx=10)
        button_frame.columnconfigure((0, 1), weight=1)
        
        load_btn = ttk.Button(button_frame, text="Load Expired Subscriptions", 
                             command=self.load_expired_subscriptions)
        load_btn.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.create_tooltip(load_btn, "Load subscriptions that have recently expired")
        
        send_btn = ttk.Button(button_frame, text="Send Cancellation Messages", 
                             command=self.send_cancellation_messages)
        send_btn.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.create_tooltip(send_btn, "Send cancellation notices to students with expired subscriptions")
    
    def create_custom_messages_tab(self, parent):
        """Create custom messages tab"""
        custom_frame = ttk.Frame(parent)
        parent.add(custom_frame, text="Custom Messages")
        
        # Configure frame grid
        custom_frame.rowconfigure(1, weight=1)  # Results frame gets extra space
        custom_frame.columnconfigure(0, weight=1)
        
        # Message composition
        compose_frame = ttk.LabelFrame(custom_frame, text="Compose Message", padding=10)
        compose_frame.grid(row=0, column=0, sticky='ew', pady=10, padx=10)
        compose_frame.columnconfigure(0, weight=1)
        
        # Recipients section
        recipients_label_frame = ttk.Frame(compose_frame)
        recipients_label_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(recipients_label_frame, text="Recipients (one phone number per line):").pack(anchor='w')
        
        recipients_input_frame = ttk.Frame(compose_frame)
        recipients_input_frame.pack(fill='x', pady=(0, 10))
        recipients_input_frame.columnconfigure(0, weight=1)
        
        self.recipients_text = tk.Text(recipients_input_frame, height=5, width=50, font=('Arial', 10))
        recipients_scroll = ttk.Scrollbar(recipients_input_frame, orient='vertical', command=self.recipients_text.yview)
        self.recipients_text.configure(yscrollcommand=recipients_scroll.set)
        
        self.recipients_text.grid(row=0, column=0, sticky='nsew')
        recipients_scroll.grid(row=0, column=1, sticky='ns')
        
        # Message section
        message_label_frame = ttk.Frame(compose_frame)
        message_label_frame.pack(fill='x', pady=(10, 5))
        
        ttk.Label(message_label_frame, text="Message:").pack(anchor='w')
        
        message_input_frame = ttk.Frame(compose_frame)
        message_input_frame.pack(fill='x', pady=(0, 10))
        message_input_frame.columnconfigure(0, weight=1)
        
        self.message_text = tk.Text(message_input_frame, height=8, width=50, font=('Arial', 10))
        message_scroll = ttk.Scrollbar(message_input_frame, orient='vertical', command=self.message_text.yview)
        self.message_text.configure(yscrollcommand=message_scroll.set)
        
        self.message_text.grid(row=0, column=0, sticky='nsew')
        message_scroll.grid(row=0, column=1, sticky='ns')
        
        # Send button
        send_button_frame = ttk.Frame(compose_frame)
        send_button_frame.pack(fill='x', pady=10)
        
        send_btn = ttk.Button(send_button_frame, text="Send Messages", command=self.send_custom_messages)
        send_btn.pack(pady=5)
        self.create_tooltip(send_btn, "Send custom messages to all specified recipients")
        
        # Results frame
        results_frame = ttk.LabelFrame(custom_frame, text="Sending Results", padding=10)
        results_frame.grid(row=1, column=0, sticky='nsew', pady=10, padx=10)
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.grid(row=0, column=0, sticky='nsew')
        results_text_frame.rowconfigure(0, weight=1)
        results_text_frame.columnconfigure(0, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_text_frame, height=10, state='disabled', 
                                                     font=('Arial', 10), wrap='word')
        self.results_text.grid(row=0, column=0, sticky='nsew')
    
    def log_message(self, message):
        """Add message to log - thread safe version"""
        def update_log():
            try:
                # Check if widget still exists
                if hasattr(self, 'log_text') and self.log_text.winfo_exists():
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    self.log_text.config(state='normal')
                    self.log_text.insert('end', f"[{timestamp}] {message}\n")
                    self.log_text.see('end')
                    self.log_text.config(state='disabled')
                    # Force update the GUI
                    self.log_text.update_idletasks()
            except Exception as e:
                # Fallback to console logging if GUI fails
                print(f"GUI Log Error: {e} - Message: {message}")
        
        # Always print to console for debugging
        print(f"WhatsApp Log: {message}")
        
        # Schedule GUI update on main thread
        try:
            if hasattr(self, 'window') and self.window:
                self.window.after(0, update_log)
        except Exception as e:
            # If after() fails, just print to console
            print(f"Error scheduling GUI update: {e}")
    
    def initialize_whatsapp(self):
        """Initialize WhatsApp Web"""
        # Disable button during initialization
        try:
            for widget in self.window.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    for tab in widget.tabs():
                        tab_frame = widget.nametowidget(tab)
                        self.set_buttons_state(tab_frame, 'disabled')
        except Exception:
            pass
        
        def update_status(status):
            """Thread-safe status update"""
            def update():
                self.status_var.set(status)
            self.window.after(0, update)
        
        def enable_buttons():
            """Re-enable buttons after initialization"""
            try:
                for widget in self.window.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Notebook):
                                for tab in child.tabs():
                                    tab_frame = child.nametowidget(tab)
                                    self.set_buttons_state(tab_frame, 'normal')
            except Exception:
                pass
        
        def init_thread():
            try:
                self.is_initializing = True  # Mark that we're initializing
                self.log_message("Starting WhatsApp Web initialization...")
                update_status("Initializing...")
                
                # Initialize driver
                self.log_message("Setting up Chrome driver...")
                success, message = self.whatsapp.initialize_driver()
                self.log_message(f"Driver initialization: {message}")
                
                if not success:
                    self.log_message(f"Failed to initialize driver: {message}")
                    update_status("Failed")
                    self.window.after(0, enable_buttons)
                    self.is_initializing = False
                    return
                
                self.log_message("Driver initialized successfully. Opening WhatsApp Web...")
                
                # Login to WhatsApp
                try:
                    success, message = self.whatsapp.login_to_whatsapp()
                    self.log_message(f"Login attempt result: {message}")
                except Exception as login_error:
                    error_str = str(login_error).lower()
                    if "connection refused" in error_str or "session deleted" in error_str:
                        self.log_message("❌ Browser session crashed during login attempt - reinitializing...")
                        try:
                            self.whatsapp.driver.quit()
                        except:
                            pass
                        self.whatsapp.driver = None
                        
                        # Try to reinitialize once
                        success, message = self.whatsapp.initialize_driver()
                        if success:
                            self.log_message("✅ Driver reinitialized - retrying login...")
                            success, message = self.whatsapp.login_to_whatsapp()
                        else:
                            self.log_message(f"❌ Failed to recover: {message}")
                            update_status("Failed")
                            self.window.after(0, enable_buttons)
                            self.is_initializing = False
                            return
                    else:
                        self.log_message(f"❌ Login error: {login_error}")
                        update_status("Failed")
                        self.window.after(0, enable_buttons)
                        self.is_initializing = False
                        return
                
                if success and "Already logged in" in message:
                    # Already logged in - verify and set status
                    self.whatsapp.is_logged_in = True
                    update_status("Connected")
                    self.log_message("✅ Already logged in to WhatsApp Web!")
                    self.window.after(0, enable_buttons)
                    self.is_initializing = False
                    return
                    
                elif "scan the QR code" in message:
                    update_status("Waiting for QR scan")
                    self.log_message("QR code is ready for scanning. Please scan with your phone.")
                    
                    # Wait for login with progress updates
                    self.log_message("Waiting for QR code scan (2 minutes timeout)...")
                    
                    # Custom wait with status updates
                    import time
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    from selenium.webdriver.common.by import By
                    from selenium.common.exceptions import TimeoutException
                    
                    timeout = 120
                    start_time = time.time()
                    
                    while time.time() - start_time < timeout:
                        try:
                            # First check if driver is still valid
                            if not self.whatsapp.driver:
                                self.log_message("❌ Driver lost during wait - reinitializing...")
                                success, message = self.whatsapp.initialize_driver()
                                if not success:
                                    self.log_message(f"Failed to reinitialize driver: {message}")
                                    update_status("Failed")
                                    self.window.after(0, enable_buttons)
                                    self.is_initializing = False
                                    return
                                # Navigate back to WhatsApp
                                self.whatsapp.driver.get("https://web.whatsapp.com")
                                time.sleep(3)
                            
                            # Use comprehensive login status check with error handling
                            try:
                                is_logged_in, status_message = self.whatsapp.check_login_status()
                            except Exception as status_error:
                                # Handle connection errors specifically
                                error_str = str(status_error).lower()
                                if "connection refused" in error_str or "session deleted" in error_str or "chrome not reachable" in error_str:
                                    self.log_message("❌ Browser session lost - reinitializing...")
                                    try:
                                        self.whatsapp.driver.quit()
                                    except:
                                        pass
                                    self.whatsapp.driver = None
                                    
                                    # Reinitialize driver
                                    success, message = self.whatsapp.initialize_driver()
                                    if not success:
                                        self.log_message(f"Failed to recover: {message}")
                                        update_status("Failed")
                                        self.window.after(0, enable_buttons)
                                        self.is_initializing = False
                                        return
                                    
                                    # Navigate back to WhatsApp
                                    self.whatsapp.driver.get("https://web.whatsapp.com")
                                    time.sleep(3)
                                    continue
                                else:
                                    self.log_message(f"Status check error: {status_error}")
                                    time.sleep(5)
                                    continue
                            
                            if is_logged_in:
                                self.whatsapp.is_logged_in = True
                                update_status("Connected")
                                self.log_message("✅ Login confirmed - WhatsApp Web successfully connected!")
                                self.window.after(0, enable_buttons)
                                self.is_initializing = False
                                return
                            
                            # Check if we're still seeing QR code or if there's an issue
                            if "QR code" in status_message:
                                # Still waiting for QR scan - continue
                                remaining = int(timeout - (time.time() - start_time))
                                if remaining > 0:
                                    update_status(f"Waiting for QR scan ({remaining}s)")
                                    if remaining % 15 == 0:  # Log every 15 seconds
                                        self.log_message(f"Still waiting for QR code scan... ({remaining} seconds remaining)")
                                time.sleep(5)  # Check every 5 seconds
                                continue
                            else:
                                # Something else is happening, log it
                                self.log_message(f"Status: {status_message}")
                                time.sleep(5)
                                continue
                                
                        except Exception as e:
                            # General error handling
                            error_str = str(e).lower()
                            if "connection refused" in error_str or "session deleted" in error_str or "chrome not reachable" in error_str:
                                self.log_message("❌ Browser connection lost - attempting recovery...")
                                try:
                                    if self.whatsapp.driver:
                                        self.whatsapp.driver.quit()
                                except:
                                    pass
                                self.whatsapp.driver = None
                                time.sleep(2)
                                continue
                            else:
                                self.log_message(f"Unexpected error: {str(e)}")
                                time.sleep(5)
                                continue
                    
                    # Timeout reached
                    update_status("Failed")
                    self.log_message("❌ Login timeout - please try again")
                    
                elif "Already logged in" in message:
                    update_status("Connected")
                    self.log_message("✅ Already logged in to WhatsApp Web!")
                elif success:
                    update_status("Connected")
                    self.log_message("✅ WhatsApp Web connected successfully!")
                else:
                    update_status("Failed")
                    self.log_message(f"❌ Login failed: {message}")
                    
                self.window.after(0, enable_buttons)
                self.is_initializing = False
                    
            except Exception as e:
                error_msg = f"Initialization error: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                update_status("Error")
                import traceback
                self.log_message(f"Stack trace: {traceback.format_exc()}")
                self.window.after(0, enable_buttons)
                self.is_initializing = False
        
        # Run in separate thread to avoid blocking UI
        self.log_message("Starting WhatsApp initialization in background...")
        threading.Thread(target=init_thread, daemon=True).start()
    
    def set_buttons_state(self, parent, state):
        """Recursively set button states"""
        try:
            for child in parent.winfo_children():
                if isinstance(child, ttk.Button):
                    child.configure(state=state)
                elif hasattr(child, 'winfo_children'):
                    self.set_buttons_state(child, state)
        except Exception:
            pass
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def update_ui_responsively(self):
        """Update UI elements responsively"""
        try:
            # Force GUI update
            self.window.update_idletasks()
        except Exception:
            pass
    
    def check_status(self):
        """Check WhatsApp connection status"""
        # Show visual feedback
        original_text = None
        try:
            # Find the check status button and change text temporarily
            for widget in self.window.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Notebook):
                            for tab in child.tabs():
                                tab_frame = child.nametowidget(tab)
                                self.update_button_text(tab_frame, "Check Status", "Checking...")
        except Exception:
            pass
        
        def restore_button_text():
            """Restore button text after check"""
            try:
                for widget in self.window.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Notebook):
                                for tab in child.tabs():
                                    tab_frame = child.nametowidget(tab)
                                    self.update_button_text(tab_frame, "Checking...", "Check Status")
            except Exception:
                pass
        
        def check_thread():
            try:
                if not self.whatsapp.driver:
                    self.window.after(0, lambda: self.status_var.set("Not connected"))
                    self.log_message("WhatsApp driver not initialized")
                    self.window.after(0, restore_button_text)
                    return
                
                # Use the comprehensive login status check method
                try:
                    is_logged_in, status_message = self.whatsapp.check_login_status()
                    
                    if is_logged_in:
                        self.whatsapp.is_logged_in = True
                        self.window.after(0, lambda: self.status_var.set("Connected"))
                        self.log_message("✅ WhatsApp is connected and ready")
                        self.log_message(f"Status details: {status_message}")
                    else:
                        self.whatsapp.is_logged_in = False
                        if "QR code" in status_message:
                            self.window.after(0, lambda: self.status_var.set("Waiting for QR scan"))
                            self.log_message("📱 QR code visible - please scan to login")
                        elif "loading" in status_message.lower():
                            self.window.after(0, lambda: self.status_var.set("Loading..."))
                            self.log_message("⏳ WhatsApp Web is loading...")
                        else:
                            self.window.after(0, lambda: self.status_var.set("Disconnected"))
                            self.log_message(f"❌ Not connected: {status_message}")
                        
                except Exception as e:
                    # Handle connection errors gracefully
                    error_str = str(e).lower()
                    if any(error in error_str for error in ["connection refused", "session deleted", "chrome not reachable"]):
                        self.whatsapp.is_logged_in = False
                        self.window.after(0, lambda: self.status_var.set("Browser crashed"))
                        self.log_message("❌ Browser session ended or crashed")
                    else:
                        self.whatsapp.is_logged_in = False
                        self.window.after(0, lambda: self.status_var.set("Error"))
                        self.log_message(f"❌ Error checking status: {str(e)}")
                    
            except Exception as e:
                self.window.after(0, lambda: self.status_var.set("Error"))
                self.log_message(f"❌ Status check failed: {str(e)}")
            finally:
                self.window.after(0, restore_button_text)
        
        # Run status check in background thread
        threading.Thread(target=check_thread, daemon=True).start()
    
    def update_button_text(self, parent, old_text, new_text):
        """Update button text recursively"""
        try:
            for child in parent.winfo_children():
                if isinstance(child, ttk.Button) and child.cget('text') == old_text:
                    child.configure(text=new_text)
                elif hasattr(child, 'winfo_children'):
                    self.update_button_text(child, old_text, new_text)
        except Exception:
            pass
    
    def force_status_check(self):
        """Force an immediate status check with detailed logging"""
        def force_check():
            try:
                self.log_message("🔄 Forcing status check...")
                
                if not self.whatsapp.driver:
                    self.window.after(0, lambda: self.status_var.set("Not connected"))
                    self.log_message("❌ No driver initialized")
                    return
                
                # Check current URL
                try:
                    current_url = self.whatsapp.driver.current_url
                    self.log_message(f"📍 Current URL: {current_url}")
                except Exception as e:
                    self.log_message(f"❌ Cannot get current URL: {e}")
                    self.window.after(0, lambda: self.status_var.set("Error"))
                    return
                
                # Use comprehensive status check
                is_logged_in, status_message = self.whatsapp.check_login_status()
                self.log_message(f"🔍 Status check result: {status_message}")
                
                if is_logged_in:
                    self.whatsapp.is_logged_in = True
                    self.window.after(0, lambda: self.status_var.set("Connected"))
                    self.log_message("✅ WhatsApp is connected!")
                else:
                    self.whatsapp.is_logged_in = False
                    if "QR code" in status_message:
                        self.window.after(0, lambda: self.status_var.set("Waiting for QR scan"))
                        self.log_message("📱 QR code visible - please scan to login")
                    elif "loading" in status_message.lower():
                        self.window.after(0, lambda: self.status_var.set("Loading"))
                        self.log_message("⏳ Page still loading...")
                    else:
                        self.window.after(0, lambda: self.status_var.set("Not connected"))
                        self.log_message(f"❌ Not connected: {status_message}")
                    
            except Exception as e:
                self.log_message(f"❌ Force status check failed: {str(e)}")
                self.window.after(0, lambda: self.status_var.set("Error"))
        
        # Run in background thread
        threading.Thread(target=force_check, daemon=True).start()
    
    def close_whatsapp(self):
        """Close WhatsApp connection"""
        try:
            success, message = self.whatsapp.close_driver()
            self.log_message(message)
            self.status_var.set("Disconnected")
        except Exception as e:
            self.log_message(f"Error closing WhatsApp: {str(e)}")
    
    def load_expiring_subscriptions(self):
        """Load expiring subscriptions"""
        # Find and disable the load button temporarily
        try:
            for widget in self.window.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Notebook):
                            for tab in child.tabs():
                                tab_frame = child.nametowidget(tab)
                                self.update_button_text(tab_frame, "Load Expiring Subscriptions", "Loading...")
                                self.set_button_state(tab_frame, "Load Expiring Subscriptions", 'disabled')
        except Exception:
            pass
        
        def load_thread():
            try:
                # Get data in background thread
                days = int(self.reminder_days_var.get())
                expiring_subs = Subscription.get_expiring_soon(days)
                
                # Update UI in main thread
                def update_ui():
                    try:
                        # Clear existing items
                        # Clear existing items and selections
                        for item in self.reminder_tree.get_children():
                            self.reminder_tree.delete(item)
                        self.reminder_selections.clear()
                        
                        for sub in expiring_subs:
                            from datetime import datetime, date
                            end_date = datetime.strptime(sub['end_date'], '%Y-%m-%d').date()
                            days_left = (end_date - date.today()).days
                            
                            item_id = self.reminder_tree.insert('', 'end', values=(
                                '☐',  # Unchecked checkbox
                                sub['student_name'],
                                sub['mobile_number'],
                                f"Seat {sub['seat_number']}",
                                sub['timeslot_name'],
                                sub['end_date'],
                                days_left
                            ))
                            # Store subscription data for this item
                            self.reminder_selections[item_id] = {'selected': False, 'data': sub}
                        
                        self.log_message(f"Loaded {len(expiring_subs)} expiring subscriptions")
                        
                    except Exception as e:
                        self.log_message(f"Error updating UI: {str(e)}")
                        messagebox.showerror("Error", f"Failed to load expiring subscriptions: {str(e)}")
                    finally:
                        # Re-enable button and restore text
                        try:
                            for widget in self.window.winfo_children():
                                if isinstance(widget, ttk.Frame):
                                    for child in widget.winfo_children():
                                        if isinstance(child, ttk.Notebook):
                                            for tab in child.tabs():
                                                tab_frame = child.nametowidget(tab)
                                                self.update_button_text(tab_frame, "Loading...", "Load Expiring Subscriptions")
                                                self.set_button_state(tab_frame, "Load Expiring Subscriptions", 'normal')
                        except Exception:
                            pass
                
                # Schedule UI update on main thread
                if hasattr(self, 'window') and self.window.winfo_exists():
                    self.window.after(0, update_ui)
                    
            except Exception as e:
                # Schedule error message on main thread
                if hasattr(self, 'window') and self.window.winfo_exists():
                    def show_error():
                        messagebox.showerror("Error", f"Failed to load expiring subscriptions: {str(e)}")
                        # Re-enable button
                        try:
                            for widget in self.window.winfo_children():
                                if isinstance(widget, ttk.Frame):
                                    for child in widget.winfo_children():
                                        if isinstance(child, ttk.Notebook):
                                            for tab in child.tabs():
                                                tab_frame = child.nametowidget(tab)
                                                self.update_button_text(tab_frame, "Loading...", "Load Expiring Subscriptions")
                                                self.set_button_state(tab_frame, "Load Expiring Subscriptions", 'normal')
                        except Exception:
                            pass
                    self.window.after(0, show_error)
        
        # Run in background thread
        threading.Thread(target=load_thread, daemon=True).start()
    
    def send_subscription_reminders(self):
        """Send subscription reminder messages"""
        if not self.whatsapp.is_logged_in:
            messagebox.showwarning("Warning", "Please login to WhatsApp first")
            return
        
        def send_thread():
            try:
                # Get only selected students
                selected_subs = []
                for item_id, data in self.reminder_selections.items():
                    if data['selected']:
                        selected_subs.append(data['data'])
                
                if not selected_subs:
                    self.log_message("No students selected for reminders")
                    return
                
                self.log_message(f"Sending consolidated reminders to {len(selected_subs)} selected students...")
                
                # Use consolidated reminders for selected students only
                results = self.whatsapp.send_consolidated_reminders(selected_subs)
                
                successful = len([r for r in results if r['success']])
                failed = len(results) - successful
                
                self.log_message(f"Consolidated reminders sent: {successful} successful, {failed} failed")
                
                # Show detailed results
                for result in results:
                    status = "✓" if result['success'] else "✗"
                    self.log_message(f"{status} {result['name']}: {result['message']}")
                
            except Exception as e:
                self.log_message(f"Error sending reminders: {str(e)}")
        
        # Check if any students are selected
        selected_count = sum(1 for data in self.reminder_selections.values() if data['selected'])
        if selected_count == 0:
            messagebox.showwarning("Warning", "Please select at least one student to send reminders to.")
            return
        
        # Confirm before sending
        if messagebox.askyesno("Confirm", f"Send subscription reminders to {selected_count} selected students?"):
            threading.Thread(target=send_thread, daemon=True).start()
    
    def load_expired_subscriptions(self):
        """Load expired subscriptions for cancellation messages"""
        def load_thread():
            try:
                # Get data in background thread
                days = int(self.cancellation_days_var.get())
                from models.subscription import Subscription
                
                expired_subs = Subscription.get_expired_subscriptions(days_expired=days)
                
                # Update UI in main thread
                def update_ui():
                    try:
                        # Clear existing items
                        for item in self.cancellation_tree.get_children():
                            self.cancellation_tree.delete(item)
                        
                        # Add expired subscriptions to tree
                        for sub in expired_subs:
                            from datetime import date, datetime
                            
                            # Calculate days expired
                            end_date = datetime.strptime(sub['end_date'], '%Y-%m-%d').date()
                            days_expired = (date.today() - end_date).days
                            
                            self.cancellation_tree.insert('', 'end', values=(
                                sub['student_name'],
                                sub['mobile_number'],
                                sub['seat_number'],
                                sub['timeslot_name'],
                                sub['end_date'],
                                f"{days_expired} days"
                            ))
                        
                        self.log_message(f"Loaded {len(expired_subs)} expired subscriptions for cancellation")
                        
                    except Exception as e:
                        self.log_message(f"Error updating UI: {str(e)}")
                        messagebox.showerror("Error", f"Failed to load expired subscriptions: {str(e)}")
                
                # Schedule UI update on main thread
                if hasattr(self, 'window') and self.window.winfo_exists():
                    self.window.after(0, update_ui)
                    
            except Exception as e:
                # Schedule error message on main thread
                if hasattr(self, 'window') and self.window.winfo_exists():
                    self.window.after(0, lambda: messagebox.showerror("Error", f"Failed to load expired subscriptions: {str(e)}"))
        
        # Run in background thread
        threading.Thread(target=load_thread, daemon=True).start()
    
    def send_cancellation_messages(self):
        """Send cancellation messages to expired students"""
        # Get expired subscriptions from tree
        expired_subs = []
        for item in self.cancellation_tree.get_children():
            values = self.cancellation_tree.item(item)['values']
            expired_subs.append({
                'student_name': values[0],
                'mobile_number': values[1],
                'seat_number': values[2],
                'timeslot_name': values[3],
                'end_date': values[4]
            })
        
        if not expired_subs:
            messagebox.showwarning("Warning", "No expired subscriptions loaded. Please load expired subscriptions first.")
            return
        
        def send_thread():
            try:
                self.log_message(f"Sending cancellation messages to {len(expired_subs)} students...")
                
                results = self.whatsapp.send_subscription_cancellations(expired_subs)
                
                successful = len([r for r in results if r['success']])
                failed = len(results) - successful
                
                self.log_message(f"Cancellation messages sent: {successful} successful, {failed} failed")
                
                # Show detailed results
                for result in results:
                    status = "✓" if result['success'] else "✗"
                    self.log_message(f"{status} {result['name']}: {result['message']}")
                
            except Exception as e:
                self.log_message(f"Error sending cancellation messages: {str(e)}")
        
        # Confirm before sending with warning
        warning_message = (
            f"⚠️ WARNING: This will send CANCELLATION messages to {len(expired_subs)} students.\n\n"
            "These messages inform students that their subscriptions have been cancelled "
            "due to expiration and provide readmission contact information.\n\n"
            "Are you sure you want to proceed?"
        )
        
        if messagebox.askyesno("Confirm Cancellation Messages", warning_message):
            threading.Thread(target=send_thread, daemon=True).start()
    
    def send_custom_messages(self):
        """Send custom messages"""
        if not self.whatsapp.is_logged_in:
            messagebox.showwarning("Warning", "Please login to WhatsApp first")
            return
        
        def send_thread():
            try:
                # Get recipients and message
                recipients_text = self.recipients_text.get('1.0', 'end-1c').strip()
                message_text = self.message_text.get('1.0', 'end-1c').strip()
                
                if not recipients_text or not message_text:
                    messagebox.showwarning("Warning", "Please enter recipients and message")
                    return
                
                # Parse recipients
                phone_numbers = [line.strip() for line in recipients_text.split('\n') if line.strip()]
                
                # Prepare messages
                contacts_messages = []
                for phone in phone_numbers:
                    contacts_messages.append({
                        'name': phone,
                        'phone': phone,
                        'message': message_text
                    })
                
                self.log_message(f"Sending custom message to {len(contacts_messages)} recipients...")
                
                # Clear results
                self.results_text.config(state='normal')
                self.results_text.delete('1.0', 'end')
                self.results_text.config(state='disabled')
                
                # Send messages
                results = self.whatsapp.send_bulk_messages(contacts_messages)
                
                # Display results
                self.results_text.config(state='normal')
                for result in results:
                    status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
                    self.results_text.insert('end', f"{status}: {result['phone']} - {result['message']}\n")
                self.results_text.config(state='disabled')
                
                successful = len([r for r in results if r['success']])
                failed = len(results) - successful
                
                self.log_message(f"Custom messages sent: {successful} successful, {failed} failed")
                
            except Exception as e:
                self.log_message(f"Error sending custom messages: {str(e)}")
        
        # Confirm before sending
        if messagebox.askyesno("Confirm", "Send custom messages to all recipients?"):
            threading.Thread(target=send_thread, daemon=True).start()
    
    def test_chrome(self):
        """Test Chrome installation and show diagnostic information"""
        try:
            self.log_message("Testing Chrome installation...")
            
            # Test Chrome installation
            result = self.whatsapp.test_chrome_installation()
            
            # Create diagnostic window
            diag_window = tk.Toplevel(self.window)
            diag_window.title("Chrome Installation Diagnostic")
            diag_window.geometry("600x500")
            diag_window.grab_set()
            
            # Header
            header_frame = ttk.Frame(diag_window)
            header_frame.pack(fill='x', padx=10, pady=10)
            
            system_info = f"System: {result['system']}"
            chrome_status = "✓ Chrome Found" if result['chrome_found'] else "✗ Chrome Not Found"
            status_color = 'green' if result['chrome_found'] else 'red'
            
            ttk.Label(header_frame, text=system_info, font=('Arial', 12, 'bold')).pack(anchor='w')
            status_label = tk.Label(header_frame, text=chrome_status, font=('Arial', 12, 'bold'), fg=status_color)
            status_label.pack(anchor='w')
            
            # Diagnostics text
            text_frame = ttk.Frame(diag_window)
            text_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            text_widget = scrolledtext.ScrolledText(text_frame, wrap='word', font=('Courier', 10))
            text_widget.pack(fill='both', expand=True)
            
            # Add diagnostic information
            diagnostic_text = "\n".join(result['diagnostics'])
            text_widget.insert('1.0', diagnostic_text)
            text_widget.config(state='disabled')
            
            # Buttons
            button_frame = ttk.Frame(diag_window)
            button_frame.pack(fill='x', padx=10, pady=10)
            
            if not result['chrome_found']:
                ttk.Button(button_frame, text="Open Chrome Download Page", 
                          command=lambda: self.open_chrome_download()).pack(side='left', padx=5)
            
            ttk.Button(button_frame, text="Close", command=diag_window.destroy).pack(side='right', padx=5)
            
            # Log the result
            if result['chrome_found']:
                self.log_message(f"✓ Chrome diagnostic completed - Chrome found at {result['chrome_path']}")
            else:
                self.log_message("✗ Chrome diagnostic completed - Chrome not found")
                
        except Exception as e:
            self.log_message(f"Error during Chrome diagnostic: {str(e)}")
            messagebox.showerror("Error", f"Failed to run Chrome diagnostic: {str(e)}")
    
    def open_chrome_download(self):
        """Open Chrome download page"""
        import webbrowser
        webbrowser.open("https://www.google.com/chrome/")
    
    def clear_session(self):
        """Clear WhatsApp session data"""
        try:
            import shutil
            import platform
            import time
            
            if messagebox.askyesno("Confirm", 
                "Clear WhatsApp session data? You'll need to scan QR code again."):
                
                # Close existing driver first
                if self.whatsapp.driver:
                    self.log_message("Closing browser...")
                    self.whatsapp.close_driver()
                    time.sleep(2)  # Wait for browser to fully close
                
                # Get session directory
                session_dir = self.whatsapp.get_session_directory()
                
                if os.path.exists(session_dir):
                    self.log_message(f"Clearing session directory: {session_dir}")
                    
                    try:
                        # Windows-specific handling
                        if platform.system() == "Windows":
                            # On Windows, try multiple methods to remove the directory
                            self.log_message("Attempting Windows-compatible removal...")
                            
                            # Method 1: Try normal removal
                            try:
                                shutil.rmtree(session_dir)
                                self.log_message("✅ Session cleared successfully (method 1)")
                            except PermissionError as e:
                                self.log_message(f"Permission error, trying alternative method: {e}")
                                
                                # Method 2: Try with error handler
                                def handle_remove_readonly(func, path, exc):
                                    try:
                                        import stat
                                        os.chmod(path, stat.S_IWRITE)
                                        func(path)
                                    except Exception:
                                        pass
                                
                                try:
                                    shutil.rmtree(session_dir, onerror=handle_remove_readonly)
                                    self.log_message("✅ Session cleared successfully (method 2)")
                                except Exception as e2:
                                    self.log_message(f"Still having issues, trying method 3: {e2}")
                                    
                                    # Method 3: Manual file-by-file removal
                                    try:
                                        import stat
                                        for root, dirs, files in os.walk(session_dir, topdown=False):
                                            for file in files:
                                                file_path = os.path.join(root, file)
                                                try:
                                                    os.chmod(file_path, stat.S_IWRITE)
                                                    os.remove(file_path)
                                                except Exception:
                                                    pass
                                            for dir in dirs:
                                                dir_path = os.path.join(root, dir)
                                                try:
                                                    os.rmdir(dir_path)
                                                except Exception:
                                                    pass
                                        os.rmdir(session_dir)
                                        self.log_message("✅ Session cleared successfully (method 3)")
                                    except Exception as e3:
                                        self.log_message(f"⚠️ Partial clear only: {e3}")
                                        self.log_message("You may need to manually delete browser data")
                        else:
                            # Linux/Mac removal
                            shutil.rmtree(session_dir)
                            self.log_message("✅ Session cleared successfully")
                            
                    except Exception as e:
                        self.log_message(f"❌ Error clearing session: {str(e)}")
                        # Provide manual instructions
                        self.log_message("Manual cleanup instructions:")
                        self.log_message(f"1. Close this application completely")
                        self.log_message(f"2. Delete folder: {session_dir}")
                        self.log_message(f"3. Restart the application")
                        
                    self.status_var.set("Session cleared")
                else:
                    self.log_message("No session data found to clear")
                    self.status_var.set("No session data")
                    
        except Exception as e:
            error_msg = f"Failed to clear session: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
    
    def update_button_text(self, parent, old_text, new_text):
        """Update button text recursively"""
        try:
            for widget in parent.winfo_children():
                if isinstance(widget, ttk.Button) and widget.cget('text') == old_text:
                    widget.config(text=new_text)
                elif hasattr(widget, 'winfo_children'):
                    self.update_button_text(widget, old_text, new_text)
        except Exception:
            pass
    
    def set_button_state(self, parent, button_text, state):
        """Set button state recursively"""
        try:
            for widget in parent.winfo_children():
                if isinstance(widget, ttk.Button) and button_text in widget.cget('text'):
                    widget.config(state=state)
                elif hasattr(widget, 'winfo_children'):
                    self.set_button_state(widget, button_text, state)
        except Exception:
            pass
    
    def on_window_close(self):
        """Handle window close event"""
        try:
            # Close WhatsApp driver gracefully
            if hasattr(self, 'whatsapp') and self.whatsapp:
                self.whatsapp.close_driver()
            
            # Destroy the window
            self.window.destroy()
        except Exception as e:
            print(f"Error closing WhatsApp window: {e}")
            try:
                self.window.destroy()
            except:
                pass
    
    def on_reminder_tree_click(self, event):
        """Handle clicks on the reminder tree for checkbox functionality"""
        try:
            item = self.reminder_tree.identify('item', event.x, event.y)
            column = self.reminder_tree.identify('column', event.x, event.y)
            
            # Check if click was on the Select column
            if item and column == '#1':  # First column is Select
                if item in self.reminder_selections:
                    # Toggle selection
                    current_state = self.reminder_selections[item]['selected']
                    self.reminder_selections[item]['selected'] = not current_state
                    
                    # Update checkbox display
                    values = list(self.reminder_tree.item(item, 'values'))
                    values[0] = '☑' if not current_state else '☐'
                    self.reminder_tree.item(item, values=values)
                    
        except Exception as e:
            self.log_message(f"Error handling tree click: {e}")
    
    def select_all_reminders(self):
        """Select all students in the reminders list"""
        try:
            for item_id in self.reminder_selections:
                self.reminder_selections[item_id]['selected'] = True
                values = list(self.reminder_tree.item(item_id, 'values'))
                values[0] = '☑'
                self.reminder_tree.item(item_id, values=values)
            
            count = len(self.reminder_selections)
            self.log_message(f"Selected all {count} students for reminders")
            
        except Exception as e:
            self.log_message(f"Error selecting all: {e}")
    
    def deselect_all_reminders(self):
        """Deselect all students in the reminders list"""
        try:
            for item_id in self.reminder_selections:
                self.reminder_selections[item_id]['selected'] = False
                values = list(self.reminder_tree.item(item_id, 'values'))
                values[0] = '☐'
                self.reminder_tree.item(item_id, values=values)
            
            count = len(self.reminder_selections)
            self.log_message(f"Deselected all {count} students")
            
        except Exception as e:
            self.log_message(f"Error deselecting all: {e}")
    
    def __del__(self):
        """Cleanup when window is closed"""
        try:
            if hasattr(self, 'whatsapp') and self.whatsapp:
                self.whatsapp.close_driver()
        except Exception:
            pass
