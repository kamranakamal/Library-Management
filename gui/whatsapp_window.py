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
        self.window.geometry("800x600")
        self.window.grab_set()  # Make window modal
        
        # Start periodic status checker
        self.start_status_monitor()
        
        # Create notebook for different functions
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
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
        def monitor():
            if hasattr(self, 'window') and self.window.winfo_exists():
                # Only check if we have a driver initialized
                if self.whatsapp.driver:
                    try:
                        # Use the comprehensive status check
                        is_logged_in, status_message = self.whatsapp.check_login_status()
                        
                        # Update status based on result
                        if is_logged_in and not self.whatsapp.is_logged_in:
                            self.whatsapp.is_logged_in = True
                            self.status_var.set("Connected")
                            self.log_message("✅ Login detected - WhatsApp Web connected!")
                        elif not is_logged_in and self.whatsapp.is_logged_in:
                            self.whatsapp.is_logged_in = False
                            if "QR code" in status_message:
                                self.status_var.set("Waiting for QR scan")
                                # Don't log every time to avoid spam
                            else:
                                self.status_var.set("Connection lost")
                                self.log_message(f"❌ Connection lost: {status_message}")
                                
                    except Exception as e:
                        # Driver might be closed or other error
                        if "session deleted" in str(e).lower():
                            self.whatsapp.is_logged_in = False
                            self.status_var.set("Browser closed")
                            self.log_message("Browser session ended")
                
                # Schedule next check
                self.window.after(5000, monitor)  # Check every 5 seconds
        
        # Start the monitor
        self.window.after(1000, monitor)  # Start after 1 second
    
    def create_login_tab(self, parent):
        """Create WhatsApp login tab"""
        login_frame = ttk.Frame(parent)
        parent.add(login_frame, text="Login")
        
        # Instructions
        instructions = """
WhatsApp Web Login Instructions:

1. Click 'Initialize WhatsApp' to open WhatsApp Web
2. Scan the QR code with your phone's WhatsApp
3. Wait for login confirmation
4. Once logged in, you can send automated messages

Note: Keep this window open while using WhatsApp automation.
        """.strip()
        
        ttk.Label(login_frame, text=instructions, justify='left', font=('Arial', 10)).pack(pady=20)
        
        # Status display
        self.status_var = tk.StringVar(value="Not connected")
        status_frame = ttk.Frame(login_frame)
        status_frame.pack(pady=10)
        
        ttk.Label(status_frame, text="Status:").pack(side='left')
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 10, 'bold'))
        status_label.pack(side='left', padx=5)
        
        # Buttons
        button_frame = ttk.Frame(login_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Initialize WhatsApp", command=self.initialize_whatsapp).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Check Status", command=self.check_status).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Force Refresh", command=self.force_status_check).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Close WhatsApp", command=self.close_whatsapp).pack(side='left', padx=5)
        
        # Diagnostic frame
        diagnostic_frame = ttk.Frame(login_frame)
        diagnostic_frame.pack(pady=10)
        
        ttk.Button(diagnostic_frame, text="Test Chrome Installation", command=self.test_chrome).pack(side='left', padx=5)
        ttk.Button(diagnostic_frame, text="Clear Session Data", command=self.clear_session).pack(side='left', padx=5)
        
        # Log display
        log_frame = ttk.LabelFrame(login_frame, text="Log", padding=10)
        log_frame.pack(fill='both', expand=True, pady=20)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        self.log_text.pack(fill='both', expand=True)
    
    def create_reminders_tab(self, parent):
        """Create subscription reminders tab"""
        reminders_frame = ttk.Frame(parent)
        parent.add(reminders_frame, text="Subscription Reminders")
        
        # Options frame
        options_frame = ttk.LabelFrame(reminders_frame, text="Reminder Options", padding=10)
        options_frame.pack(fill='x', pady=10)
        
        # Days before expiry
        ttk.Label(options_frame, text="Send reminders for subscriptions expiring in:").pack(anchor='w')
        days_frame = ttk.Frame(options_frame)
        days_frame.pack(fill='x', pady=5)
        
        self.reminder_days_var = tk.StringVar(value="7")
        tk.Spinbox(days_frame, from_=1, to=30, textvariable=self.reminder_days_var, width=10).pack(side='left')
        ttk.Label(days_frame, text="days").pack(side='left', padx=5)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(reminders_frame, text="Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        # Expiring subscriptions tree
        columns = ('Student', 'Mobile', 'Seat', 'Timeslot', 'Expiry Date', 'Days Left')
        self.reminder_tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.reminder_tree.heading(col, text=col)
            self.reminder_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=self.reminder_tree.yview)
        self.reminder_tree.configure(yscrollcommand=scrollbar.set)
        
        self.reminder_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons
        button_frame = ttk.Frame(reminders_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Load Expiring Subscriptions", 
                  command=self.load_expiring_subscriptions).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Send Reminders", 
                  command=self.send_subscription_reminders).pack(side='left', padx=5)
    
    def create_cancellations_tab(self, parent):
        """Create subscription cancellations tab"""
        cancellations_frame = ttk.Frame(parent)
        parent.add(cancellations_frame, text="Subscription Cancellations")
        
        # Instructions
        instructions = """
This feature sends cancellation notifications to students whose subscriptions have expired.
The message includes readmission contact information and encourages them to return.
        """.strip()
        
        ttk.Label(cancellations_frame, text=instructions, justify='left', 
                 font=('Arial', 10), wraplength=700).pack(pady=10)
        
        # Options frame
        options_frame = ttk.LabelFrame(cancellations_frame, text="Cancellation Options", padding=10)
        options_frame.pack(fill='x', pady=10)
        
        # Days since expiry
        ttk.Label(options_frame, text="Send cancellations for subscriptions expired within:").pack(anchor='w')
        days_frame = ttk.Frame(options_frame)
        days_frame.pack(fill='x', pady=5)
        
        self.cancellation_days_var = tk.StringVar(value="7")
        tk.Spinbox(days_frame, from_=1, to=30, textvariable=self.cancellation_days_var, width=10).pack(side='left')
        ttk.Label(days_frame, text="days").pack(side='left', padx=5)
        
        # Warning frame
        warning_frame = ttk.Frame(options_frame)
        warning_frame.pack(fill='x', pady=10)
        
        warning_text = "⚠️ This will send cancellation messages to expired students. Use carefully!"
        ttk.Label(warning_frame, text=warning_text, foreground='red', font=('Arial', 10, 'bold')).pack()
        
        # Preview frame
        preview_frame = ttk.LabelFrame(cancellations_frame, text="Expired Subscriptions", padding=10)
        preview_frame.pack(fill='both', expand=True, pady=10)
        
        # Expired subscriptions tree
        columns = ('Student', 'Mobile', 'Seat', 'Timeslot', 'Expired Date', 'Days Expired')
        self.cancellation_tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.cancellation_tree.heading(col, text=col)
            self.cancellation_tree.column(col, width=100)
        
        scrollbar2 = ttk.Scrollbar(preview_frame, orient='vertical', command=self.cancellation_tree.yview)
        self.cancellation_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.cancellation_tree.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
        # Buttons
        button_frame = ttk.Frame(cancellations_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Load Expired Subscriptions", 
                  command=self.load_expired_subscriptions).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Send Cancellation Messages", 
                  command=self.send_cancellation_messages).pack(side='left', padx=5)
    
    def create_custom_messages_tab(self, parent):
        """Create custom messages tab"""
        custom_frame = ttk.Frame(parent)
        parent.add(custom_frame, text="Custom Messages")
        
        # Message composition
        compose_frame = ttk.LabelFrame(custom_frame, text="Compose Message", padding=10)
        compose_frame.pack(fill='x', pady=10)
        
        # Recipients
        ttk.Label(compose_frame, text="Recipients (one phone number per line):").pack(anchor='w')
        self.recipients_text = tk.Text(compose_frame, height=5, width=50)
        self.recipients_text.pack(fill='x', pady=5)
        
        # Message
        ttk.Label(compose_frame, text="Message:").pack(anchor='w', pady=(10, 0))
        self.message_text = tk.Text(compose_frame, height=8, width=50)
        self.message_text.pack(fill='x', pady=5)
        
        # Send button
        ttk.Button(compose_frame, text="Send Messages", command=self.send_custom_messages).pack(pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(custom_frame, text="Results", padding=10)
        results_frame.pack(fill='both', expand=True, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=10, state='disabled')
        self.results_text.pack(fill='both', expand=True)
    
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
        def update_status(status):
            """Thread-safe status update"""
            def update():
                self.status_var.set(status)
            self.window.after(0, update)
        
        def init_thread():
            try:
                self.log_message("Starting WhatsApp Web initialization...")
                update_status("Initializing...")
                
                # Initialize driver
                self.log_message("Setting up Chrome driver...")
                success, message = self.whatsapp.initialize_driver()
                self.log_message(f"Driver initialization: {message}")
                
                if not success:
                    self.log_message(f"Failed to initialize driver: {message}")
                    update_status("Failed")
                    return
                
                self.log_message("Driver initialized successfully. Opening WhatsApp Web...")
                
                # Login to WhatsApp
                success, message = self.whatsapp.login_to_whatsapp()
                self.log_message(f"Login attempt: {message}")
                
                if "scan the QR code" in message:
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
                            # Check if logged in (short wait)
                            wait_short = WebDriverWait(self.whatsapp.driver, 5)
                            wait_short.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]')))
                            self.whatsapp.is_logged_in = True
                            update_status("Connected")
                            self.log_message("✅ WhatsApp Web successfully connected!")
                            return
                        except TimeoutException:
                            # Still waiting, update progress
                            remaining = int(timeout - (time.time() - start_time))
                            if remaining > 0:
                                update_status(f"Waiting for QR scan ({remaining}s)")
                                if remaining % 10 == 0:  # Log every 10 seconds
                                    self.log_message(f"Still waiting for QR code scan... ({remaining} seconds remaining)")
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
                    
            except Exception as e:
                error_msg = f"Initialization error: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                update_status("Error")
                import traceback
                self.log_message(f"Stack trace: {traceback.format_exc()}")
        
        # Run in separate thread to avoid blocking UI
        self.log_message("Starting WhatsApp initialization in background...")
        threading.Thread(target=init_thread, daemon=True).start()
    
    def check_status(self):
        """Check WhatsApp connection status"""
        def check_thread():
            try:
                if not self.whatsapp.driver:
                    self.window.after(0, lambda: self.status_var.set("Not connected"))
                    self.log_message("WhatsApp driver not initialized")
                    return
                
                # Try to check if still logged in by looking for chat list
                try:
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    from selenium.webdriver.common.by import By
                    from selenium.common.exceptions import TimeoutException
                    
                    wait = WebDriverWait(self.whatsapp.driver, 10)
                    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]')))
                    
                    self.whatsapp.is_logged_in = True
                    self.window.after(0, lambda: self.status_var.set("Connected"))
                    self.log_message("✅ WhatsApp is connected and ready")
                    
                except TimeoutException:
                    # Check if on login page (QR code visible)
                    try:
                        self.whatsapp.driver.find_element(By.XPATH, '//canvas')
                        self.whatsapp.is_logged_in = False
                        self.window.after(0, lambda: self.status_var.set("Waiting for QR scan"))
                        self.log_message("⏳ QR code visible - need to scan")
                    except:
                        self.whatsapp.is_logged_in = False
                        self.window.after(0, lambda: self.status_var.set("Connection lost"))
                        self.log_message("❌ Connection lost or page not loaded properly")
                        
                except Exception as e:
                    self.whatsapp.is_logged_in = False
                    self.window.after(0, lambda: self.status_var.set("Error"))
                    self.log_message(f"❌ Error checking status: {str(e)}")
                    
            except Exception as e:
                self.window.after(0, lambda: self.status_var.set("Error"))
                self.log_message(f"❌ Status check failed: {str(e)}")
        
        # Run status check in background thread
        threading.Thread(target=check_thread, daemon=True).start()
    
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
        try:
            # Clear existing items
            for item in self.reminder_tree.get_children():
                self.reminder_tree.delete(item)
            
            days = int(self.reminder_days_var.get())
            expiring_subs = Subscription.get_expiring_soon(days)
            
            for sub in expiring_subs:
                from datetime import datetime, date
                end_date = datetime.strptime(sub['end_date'], '%Y-%m-%d').date()
                days_left = (end_date - date.today()).days
                
                self.reminder_tree.insert('', 'end', values=(
                    sub['student_name'],
                    sub['mobile_number'],
                    f"Seat {sub['seat_number']}",
                    sub['timeslot_name'],
                    sub['end_date'],
                    days_left
                ))
            
            self.log_message(f"Loaded {len(expiring_subs)} expiring subscriptions")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expiring subscriptions: {str(e)}")
    
    def send_subscription_reminders(self):
        """Send subscription reminder messages"""
        if not self.whatsapp.is_logged_in:
            messagebox.showwarning("Warning", "Please login to WhatsApp first")
            return
        
        def send_thread():
            try:
                days = int(self.reminder_days_var.get())
                expiring_subs = Subscription.get_expiring_soon(days)
                
                if not expiring_subs:
                    self.log_message("No expiring subscriptions found")
                    return
                
                self.log_message(f"Sending reminders to {len(expiring_subs)} students...")
                
                results = self.whatsapp.send_subscription_reminders(expiring_subs)
                
                successful = len([r for r in results if r['success']])
                failed = len(results) - successful
                
                self.log_message(f"Reminders sent: {successful} successful, {failed} failed")
                
                # Show detailed results
                for result in results:
                    status = "✓" if result['success'] else "✗"
                    self.log_message(f"{status} {result['name']}: {result['message']}")
                
            except Exception as e:
                self.log_message(f"Error sending reminders: {str(e)}")
        
        # Confirm before sending
        if messagebox.askyesno("Confirm", "Send subscription reminders to all expiring students?"):
            threading.Thread(target=send_thread, daemon=True).start()
    
    def load_expired_subscriptions(self):
        """Load expired subscriptions for cancellation messages"""
        try:
            days = int(self.cancellation_days_var.get())
            from models.subscription import Subscription
            
            expired_subs = Subscription.get_expired_subscriptions(days_expired=days)
            
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
            self.log_message(f"Error loading expired subscriptions: {str(e)}")
            messagebox.showerror("Error", f"Failed to load expired subscriptions: {str(e)}")
    
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
    
    def __del__(self):
        """Cleanup when window is closed"""
        try:
            self.whatsapp.close_driver()
        except Exception:
            pass
