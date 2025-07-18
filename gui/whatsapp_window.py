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
        
        # Create notebook for different functions
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Login tab
        self.create_login_tab(notebook)
        
        # Reminders tab
        self.create_reminders_tab(notebook)
        
        # Custom messages tab
        self.create_custom_messages_tab(notebook)
    
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
        """Add message to log"""
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')
    
    def initialize_whatsapp(self):
        """Initialize WhatsApp Web"""
        def init_thread():
            try:
                self.log_message("Initializing WhatsApp Web...")
                self.status_var.set("Initializing...")
                
                # Initialize driver
                success, message = self.whatsapp.initialize_driver()
                if not success:
                    self.log_message(f"Failed to initialize: {message}")
                    self.status_var.set("Failed")
                    return
                
                # Login to WhatsApp
                success, message = self.whatsapp.login_to_whatsapp()
                self.log_message(message)
                
                if "scan the QR code" in message:
                    self.status_var.set("Waiting for QR scan")
                    self.log_message("Please scan the QR code in the browser window...")
                    
                    # Wait for login
                    success, message = self.whatsapp.wait_for_login(120)
                    self.log_message(message)
                    
                    if success:
                        self.status_var.set("Connected")
                    else:
                        self.status_var.set("Failed")
                elif success:
                    self.status_var.set("Connected")
                else:
                    self.status_var.set("Failed")
                    
            except Exception as e:
                self.log_message(f"Error: {str(e)}")
                self.status_var.set("Error")
        
        # Run in separate thread to avoid blocking UI
        threading.Thread(target=init_thread, daemon=True).start()
    
    def check_status(self):
        """Check WhatsApp connection status"""
        if self.whatsapp.is_logged_in:
            self.status_var.set("Connected")
            self.log_message("WhatsApp is connected and ready")
        else:
            self.status_var.set("Not connected")
            self.log_message("WhatsApp is not connected")
    
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
            
            if messagebox.askyesno("Confirm", 
                "Clear WhatsApp session data? You'll need to scan QR code again."):
                
                # Close existing driver first
                if self.whatsapp.driver:
                    self.whatsapp.close_driver()
                
                # Remove session directory
                session_dir = "./whatsapp_session"
                if os.path.exists(session_dir):
                    shutil.rmtree(session_dir)
                    self.log_message("Session data cleared successfully")
                    self.status_var.set("Session cleared - need to login again")
                else:
                    self.log_message("No session data found to clear")
                    
        except Exception as e:
            self.log_message(f"Error clearing session: {str(e)}")
            messagebox.showerror("Error", f"Failed to clear session: {str(e)}")
    
    def __del__(self):
        """Cleanup when window is closed"""
        try:
            self.whatsapp.close_driver()
        except Exception:
            pass
