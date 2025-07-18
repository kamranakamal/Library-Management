"""
Student management interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import os
import subprocess
from datetime import date, datetime, timedelta
from models.student import Student
from models.subscription import Subscription
from models.seat import Seat
from models.timeslot import Timeslot
from utils.validators import Validators, ValidationError


class StudentManagementFrame(ttk.Frame):
    """Student management interface"""
    
    def __init__(self, parent):
        super().__init__(parent)
        # Initialize data containers
        self.timeslots = {}
        self.available_seats = {}
        self.current_student_id = None
        
        self.setup_ui()
        self.load_data()
    
    def set_today_date(self):
        """Set registration date to today"""
        self.reg_date_var.set(str(date.today()))
    
    def pick_registration_date(self):
        """Open date picker for registration date"""
        self.open_date_picker(self.reg_date_var, "Select Registration Date")
    
    def open_date_picker(self, date_var, title="Select Date"):
        """Open a simple date picker dialog"""
        from tkinter import simpledialog
        
        # Create date picker dialog
        date_dialog = tk.Toplevel(self)
        date_dialog.title(title)
        date_dialog.geometry("300x250")
        date_dialog.resizable(False, False)
        
        # Make dialog modal
        date_dialog.transient(self)
        date_dialog.grab_set()
        
        # Center the dialog
        date_dialog.update_idletasks()
        x = (date_dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (date_dialog.winfo_screenheight() // 2) - (250 // 2)
        date_dialog.geometry(f"300x250+{x}+{y}")
        
        # Current date or selected date
        try:
            current_date = datetime.strptime(date_var.get(), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            current_date = date.today()
        
        # Date picker frame
        picker_frame = ttk.LabelFrame(date_dialog, text="Select Date", padding=10)
        picker_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Year selection
        year_frame = ttk.Frame(picker_frame)
        year_frame.pack(fill='x', pady=5)
        ttk.Label(year_frame, text="Year:").pack(side='left')
        year_var = tk.StringVar(value=str(current_date.year))
        year_spin = tk.Spinbox(year_frame, from_=2000, to=2050, textvariable=year_var, width=10)
        year_spin.pack(side='right')
        
        # Month selection
        month_frame = ttk.Frame(picker_frame)
        month_frame.pack(fill='x', pady=5)
        ttk.Label(month_frame, text="Month:").pack(side='left')
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        month_var = tk.StringVar(value=months[current_date.month - 1])
        month_combo = ttk.Combobox(month_frame, textvariable=month_var, values=months, state='readonly', width=12)
        month_combo.pack(side='right')
        
        # Day selection
        day_frame = ttk.Frame(picker_frame)
        day_frame.pack(fill='x', pady=5)
        ttk.Label(day_frame, text="Day:").pack(side='left')
        day_var = tk.StringVar(value=str(current_date.day))
        day_spin = tk.Spinbox(day_frame, from_=1, to=31, textvariable=day_var, width=10)
        day_spin.pack(side='right')
        
        # Preview
        preview_frame = ttk.Frame(picker_frame)
        preview_frame.pack(fill='x', pady=10)
        ttk.Label(preview_frame, text="Selected Date:").pack(side='left')
        preview_var = tk.StringVar()
        preview_label = ttk.Label(preview_frame, textvariable=preview_var, font=('Arial', 10, 'bold'))
        preview_label.pack(side='right')
        
        def update_preview(*args):
            try:
                selected_month = months.index(month_var.get()) + 1
                selected_date = date(int(year_var.get()), selected_month, int(day_var.get()))
                preview_var.set(selected_date.strftime('%Y-%m-%d'))
            except (ValueError, IndexError):
                preview_var.set("Invalid Date")
        
        # Bind preview updates
        year_var.trace('w', update_preview)
        month_var.trace('w', update_preview)
        day_var.trace('w', update_preview)
        
        # Initial preview
        update_preview()
        
        # Buttons
        button_frame = ttk.Frame(picker_frame)
        button_frame.pack(fill='x', pady=10)
        
        def apply_date():
            try:
                selected_month = months.index(month_var.get()) + 1
                selected_date = date(int(year_var.get()), selected_month, int(day_var.get()))
                date_var.set(selected_date.strftime('%Y-%m-%d'))
                date_dialog.destroy()
            except (ValueError, IndexError):
                messagebox.showerror("Invalid Date", "Please select a valid date.")
        
        def cancel_date():
            date_dialog.destroy()
        
        ttk.Button(button_frame, text="Apply", command=apply_date).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel_date).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Today", 
                  command=lambda: [date_var.set(str(date.today())), date_dialog.destroy()]).pack(side='left')
    
    def setup_ui(self):
        """Setup user interface"""
        # Create main paned window
        self.paned_window = ttk.PanedWindow(self, orient='horizontal')
        self.paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - Student form
        self.create_student_form()
        
        # Right panel - Student list and subscriptions
        self.create_student_list()
    
    def create_student_form(self):
        """Create student form panel"""
        # Left frame for form
        form_frame = ttk.LabelFrame(self.paned_window, text="Student Information", padding=10)
        self.paned_window.add(form_frame, weight=1)
        
        # Form fields
        row = 0
        
        # Name
        ttk.Label(form_frame, text="Name *:").grid(row=row, column=0, sticky='w', pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Father's Name
        ttk.Label(form_frame, text="Father's Name *:").grid(row=row, column=0, sticky='w', pady=2)
        self.father_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.father_name_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Gender
        ttk.Label(form_frame, text="Gender *:").grid(row=row, column=0, sticky='w', pady=2)
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(form_frame, textvariable=self.gender_var, values=['Male', 'Female'], state='readonly', width=28)
        gender_combo.grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Mobile Number
        ttk.Label(form_frame, text="Mobile Number *:").grid(row=row, column=0, sticky='w', pady=2)
        self.mobile_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.mobile_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Aadhaar Number
        ttk.Label(form_frame, text="Aadhaar Number:").grid(row=row, column=0, sticky='w', pady=2)
        self.aadhaar_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.aadhaar_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=row, column=0, sticky='w', pady=2)
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Locker Number
        ttk.Label(form_frame, text="Locker Number:").grid(row=row, column=0, sticky='w', pady=2)
        self.locker_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.locker_var, width=30).grid(row=row, column=1, pady=2, sticky='ew')
        row += 1
        
        # Registration Date
        ttk.Label(form_frame, text="Registration Date *:").grid(row=row, column=0, sticky='w', pady=2)
        reg_date_frame = ttk.Frame(form_frame)
        reg_date_frame.grid(row=row, column=1, pady=2, sticky='ew')
        
        self.reg_date_var = tk.StringVar()
        # Set default to today's date
        self.reg_date_var.set(str(date.today()))
        reg_date_entry = ttk.Entry(reg_date_frame, textvariable=self.reg_date_var, width=25)
        reg_date_entry.grid(row=0, column=0, sticky='ew')
        
        # Date picker buttons
        ttk.Button(reg_date_frame, text="Today", 
                  command=self.set_today_date, width=8).grid(row=0, column=1, padx=(5,0))
        ttk.Button(reg_date_frame, text="Pick Date", 
                  command=self.pick_registration_date, width=10).grid(row=0, column=2, padx=(5,0))
        
        reg_date_frame.columnconfigure(0, weight=1)
        
        # Format hint
        ttk.Label(form_frame, text="(YYYY-MM-DD format)", 
                 font=('Arial', 8), foreground='gray').grid(row=row+1, column=1, sticky='w')
        row += 2
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10, sticky='ew')
        
        ttk.Button(button_frame, text="Save Student", command=self.save_student).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete Student", command=self.delete_student).grid(row=0, column=2, padx=5)
        
        # Status label
        row += 1
        self.status_label = ttk.Label(form_frame, text="Ready to create new student", 
                                     font=('Arial', 9), foreground='blue')
        self.status_label.grid(row=row, column=0, columnspan=2, pady=5)
        
        # Configure column weights
        form_frame.columnconfigure(1, weight=1)
        
        # Subscription section
        self.create_subscription_form(form_frame, row + 1)
    
    def create_subscription_form(self, parent, start_row):
        """Create subscription form section"""
        # Separator
        ttk.Separator(parent, orient='horizontal').grid(row=start_row, column=0, columnspan=2, sticky='ew', pady=10)
        start_row += 1
        
        # Subscription header
        ttk.Label(parent, text="Add New Subscription", font=('Arial', 10, 'bold')).grid(row=start_row, column=0, columnspan=2, pady=5)
        ttk.Label(parent, text="(Works for both new and existing students)", 
                 font=('Arial', 8), foreground='gray').grid(row=start_row+1, column=0, columnspan=2)
        start_row += 2
        
        # Timeslot
        ttk.Label(parent, text="Timeslot:").grid(row=start_row, column=0, sticky='w', pady=2)
        self.timeslot_var = tk.StringVar()
        self.timeslot_combo = ttk.Combobox(parent, textvariable=self.timeslot_var, state='readonly', width=28)
        self.timeslot_combo.grid(row=start_row, column=1, pady=2, sticky='ew')
        self.timeslot_combo.bind('<<ComboboxSelected>>', self.on_timeslot_selected)
        start_row += 1
        
        # Available Seats
        ttk.Label(parent, text="Available Seats:").grid(row=start_row, column=0, sticky='w', pady=2)
        self.seat_var = tk.StringVar()
        self.seat_combo = ttk.Combobox(parent, textvariable=self.seat_var, state='readonly', width=28)
        self.seat_combo.grid(row=start_row, column=1, pady=2, sticky='ew')
        start_row += 1
        
        # Duration
        ttk.Label(parent, text="Duration (months):").grid(row=start_row, column=0, sticky='w', pady=2)
        self.duration_var = tk.StringVar(value="1")
        ttk.Entry(parent, textvariable=self.duration_var, width=30).grid(row=start_row, column=1, pady=2, sticky='ew')
        start_row += 1
        
        # Amount
        ttk.Label(parent, text="Amount:").grid(row=start_row, column=0, sticky='w', pady=2)
        self.amount_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.amount_var, width=30).grid(row=start_row, column=1, pady=2, sticky='ew')
        start_row += 1
        
        # Subscription buttons
        sub_button_frame = ttk.Frame(parent)
        sub_button_frame.grid(row=start_row, column=0, columnspan=2, pady=10, sticky='ew')
        
        ttk.Button(sub_button_frame, text="Add Subscription", command=self.add_subscription).grid(row=0, column=0, padx=5)
        ttk.Button(sub_button_frame, text="Renew Subscription", command=self.renew_subscription).grid(row=0, column=1, padx=5)
        ttk.Button(sub_button_frame, text="Generate Receipt", command=self.generate_receipt).grid(row=0, column=2, padx=5)
    
    def create_student_list(self):
        """Create student list panel"""
        # Right frame for list
        list_frame = ttk.LabelFrame(self.paned_window, text="Students", padding=10)
        self.paned_window.add(list_frame, weight=2)
        
        # Search frame
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky='w')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_students).grid(row=0, column=2, padx=2)
        ttk.Button(search_frame, text="Refresh", command=self.load_data).grid(row=0, column=3, padx=2)
        
        # Configure search frame column weights
        search_frame.columnconfigure(1, weight=1)
        
        # Student list
        columns = ('ID', 'Name', 'Gender', 'Mobile', 'Registration Date', 'Active Subscriptions')
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.student_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.student_tree.xview)
        self.student_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for tree and scrollbars
        self.student_tree.grid(row=1, column=0, sticky='nsew')
        v_scrollbar.grid(row=1, column=1, sticky='ns')
        h_scrollbar.grid(row=2, column=0, sticky='ew')
        
        # Configure grid weights
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Bind selection event
        self.student_tree.bind('<<TreeviewSelect>>', self.on_student_select)
        
        # Subscriptions frame
        self.create_subscriptions_view(list_frame)
    
    def create_subscriptions_view(self, parent):
        """Create subscriptions view"""
        # Subscriptions frame
        subs_frame = ttk.LabelFrame(parent, text="Student Subscriptions", padding=5)
        subs_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Subscriptions tree
        sub_columns = ('Receipt', 'Seat', 'Timeslot', 'Start Date', 'End Date', 'Amount', 'Status')
        self.subscription_tree = ttk.Treeview(subs_frame, columns=sub_columns, show='headings', height=6)
        
        for col in sub_columns:
            self.subscription_tree.heading(col, text=col)
            if col == 'Timeslot':
                self.subscription_tree.column(col, width=150)  # Wider for time info
            else:
                self.subscription_tree.column(col, width=80)
        
        self.subscription_tree.grid(row=0, column=0, columnspan=4, sticky='nsew')
        
        # Subscription management buttons
        button_frame = ttk.Frame(subs_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=5, sticky='ew')
        
        ttk.Button(button_frame, text="Edit Subscription", 
                  command=self.edit_subscription).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Renew Subscription", 
                  command=self.renew_subscription).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete Subscription", 
                  command=self.delete_subscription).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="View Receipt", 
                  command=self.view_receipt).grid(row=0, column=3, padx=5)
        
        # Bind subscription selection event
        self.subscription_tree.bind('<<TreeviewSelect>>', self.on_subscription_select)
        
        # Configure grid weights for subscriptions frame
        subs_frame.rowconfigure(0, weight=1)
        subs_frame.columnconfigure(0, weight=1)
    
    def load_data(self):
        """Load students and related data"""
        self.load_students()
        self.load_timeslots()
    
    def load_students(self):
        """Load students into the tree"""
        # Clear existing items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        try:
            students = Student.get_all()
            for student in students:
                # Get active subscriptions count
                active_subs = len(student.get_active_subscriptions())
                
                self.student_tree.insert('', 'end', values=(
                    student.id,
                    student.name,
                    student.gender,
                    student.mobile_number,
                    student.registration_date,
                    active_subs
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {str(e)}")
    
    def load_timeslots(self):
        """Load timeslots into combo box"""
        try:
            timeslots = Timeslot.get_all()
            timeslot_values = [f"{ts.name} ({ts.start_time}-{ts.end_time}) - Rs. {ts.price}" for ts in timeslots]
            self.timeslot_combo['values'] = timeslot_values
            
            # Store timeslot objects for reference
            self.timeslots = {f"{ts.name} ({ts.start_time}-{ts.end_time}) - Rs. {ts.price}": ts for ts in timeslots}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load timeslots: {str(e)}")
    
    def on_timeslot_selected(self, event):
        """Handle timeslot selection"""
        if not self.timeslot_var.get() or not self.gender_var.get():
            return
        
        try:
            # Get selected timeslot
            selected_timeslot = self.timeslots[self.timeslot_var.get()]
            
            # Get available seats for the gender and timeslot
            available_seats_data = selected_timeslot.get_available_seats(self.gender_var.get())
            
            # Create seat objects from data and update combo box
            self.available_seats = {}
            seat_values = []
            
            for seat_data in available_seats_data:
                seat_id = seat_data['id']
                row_number = seat_data['row_number']
                seat_label = f"Seat {seat_id} (Row {row_number})"
                seat_values.append(seat_label)
                
                # Create a simple seat object for reference
                from collections import namedtuple
                Seat = namedtuple('Seat', ['id', 'row_number'])
                self.available_seats[seat_label] = Seat(seat_id, row_number)
            
            self.seat_combo['values'] = seat_values
            
            # Set amount from timeslot price
            self.amount_var.set(str(selected_timeslot.price))
            
            # Clear current seat selection
            self.seat_var.set("")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load available seats: {str(e)}")
    
    def on_student_select(self, event):
        """Handle student selection"""
        selection = self.student_tree.selection()
        if not selection:
            return
        
        try:
            # Get selected student
            item = self.student_tree.item(selection[0])
            student_id = item['values'][0]
            
            student = Student.get_by_id(student_id)
            if student:
                # Populate form
                self.name_var.set(student.name)
                self.father_name_var.set(student.father_name)
                self.gender_var.set(student.gender)
                self.mobile_var.set(student.mobile_number)
                self.aadhaar_var.set(student.aadhaar_number or "")
                self.email_var.set(student.email or "")
                self.locker_var.set(student.locker_number or "")
                self.reg_date_var.set(student.registration_date)
                
                # Update status label
                self.status_label.config(text=f"Editing: {student.name} (ID: {student.id})", 
                                       foreground='green')
                
                # Load subscriptions
                self.load_student_subscriptions(student_id)
                
                # Update available seats
                self.on_timeslot_selected(None)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load student details: {str(e)}")
    
    def load_student_subscriptions(self, student_id):
        """Load subscriptions for selected student"""
        # Clear existing items
        for item in self.subscription_tree.get_children():
            self.subscription_tree.delete(item)
        
        try:
            subscriptions = Subscription.get_by_student_id(student_id, active_only=False)
            
            for sub in subscriptions:
                # Skip inactive (deleted) subscriptions
                if not sub.is_active:
                    continue
                    
                # Get related data with error handling
                try:
                    seat = Seat.get_by_id(sub.seat_id)
                    timeslot = Timeslot.get_by_id(sub.timeslot_id)
                    
                    # Format timeslot display with time information
                    if timeslot:
                        timeslot_display = f"{timeslot.name} ({timeslot.start_time} - {timeslot.end_time})"
                    else:
                        timeslot_display = "N/A"
                    
                except Exception as e:
                    # Log error without cluttering console
                    import logging
                    logging.error(f"Failed to load data for subscription {sub.receipt_number}: {e}")
                    seat = None
                    timeslot = None
                    timeslot_display = "Error Loading"
                
                status = "Active" if sub.is_active and not sub.is_expired() else "Expired"
                
                self.subscription_tree.insert('', 'end', values=(
                    sub.receipt_number,
                    f"Seat {seat.id}" if seat else "N/A",
                    timeslot_display,
                    sub.start_date,
                    sub.end_date,
                    f"Rs. {sub.amount_paid}",
                    status
                ))
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load subscriptions: {str(e)}")
            logging.error(f"Failed to load subscriptions for student {student_id}: {e}")
    
    def save_student(self):
        """Save student information (create new or update existing)"""
        try:
            # Validate basic student data
            student_data = {
                'name': self.name_var.get(),
                'father_name': self.father_name_var.get(),
                'gender': self.gender_var.get(),
                'mobile_number': self.mobile_var.get(),
                'aadhaar_number': self.aadhaar_var.get(),
                'email': self.email_var.get(),
                'locker_number': self.locker_var.get(),
                'registration_date': self.reg_date_var.get()
            }
            
            validated_data = Validators.validate_student_data(student_data)
            
            # Check if this is updating an existing student
            selection = self.student_tree.selection()
            if selection:
                # Update existing student
                item = self.student_tree.item(selection[0])
                student_id = item['values'][0]
                student = Student.get_by_id(student_id)
                
                if student:
                    for key, value in validated_data.items():
                        setattr(student, key, value)
                    student.save()
                    
                    messagebox.showinfo("Success", "Student updated successfully!")
                    self.load_students()
                    return
            
            # Create new student
            student = Student(**validated_data)
            student_id = student.save()
            
            messagebox.showinfo("Success", 
                f"Student '{validated_data['name']}' created successfully!\n"
                f"You can now add subscriptions using the 'Add Subscription' button.")
            self.load_students()
            
            # Select the newly created student in the tree
            self.select_student_by_id(student_id)
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save student: {str(e)}")
    
    def select_student_by_id(self, student_id):
        """Select a student in the tree by their ID"""
        for item in self.student_tree.get_children():
            item_values = self.student_tree.item(item)['values']
            if item_values[0] == student_id:
                self.student_tree.selection_set(item)
                self.student_tree.focus(item)
                self.on_student_select(None)  # Trigger selection event
                break
    
    def clear_form(self):
        """Clear the form"""
        self.name_var.set("")
        self.father_name_var.set("")
        self.gender_var.set("")
        self.mobile_var.set("")
        self.aadhaar_var.set("")
        self.email_var.set("")
        self.locker_var.set("")
        self.reg_date_var.set("")
        self.timeslot_var.set("")
        self.seat_var.set("")
        self.duration_var.set("1")
        self.amount_var.set("")
        
        # Reset status label
        self.status_label.config(text="Ready to create new student", foreground='blue')
        
        # Clear student tree selection
        self.student_tree.selection_remove(self.student_tree.selection())
        
        # Clear subscriptions tree
        for item in self.subscription_tree.get_children():
            self.subscription_tree.delete(item)
    
    def delete_student(self):
        """Delete selected student"""
        selection = self.student_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a student to delete")
            return
        
        try:
            # Confirm deletion
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
                item = self.student_tree.item(selection[0])
                student_id = item['values'][0]
                
                student = Student.get_by_id(student_id)
                if student:
                    student.delete()
                    messagebox.showinfo("Success", "Student deleted successfully!")
                    self.load_students()
                    self.clear_form()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete student: {str(e)}")
    
    def add_subscription(self):
        """Add subscription for student"""
        try:
            # Validate subscription data first
            if not self.timeslot_var.get():
                messagebox.showwarning("Warning", "Please select a timeslot")
                return
            
            if not self.seat_var.get():
                messagebox.showwarning("Warning", "Please select a seat")
                return
            
            if not self.amount_var.get():
                messagebox.showwarning("Warning", "Please enter the subscription amount")
                return
            
            # Determine if we're working with an existing student or creating new
            student_id = None
            selection = self.student_tree.selection()
            
            if selection:
                # Existing student selected
                item = self.student_tree.item(selection[0])
                student_id = item['values'][0]
                student = Student.get_by_id(student_id)
                
                if not student:
                    messagebox.showerror("Error", "Selected student not found")
                    return
            else:
                # Check if student form has data for creating new student
                if not self.name_var.get():
                    messagebox.showwarning("Warning", 
                        "Please either:\n"
                        "1. Select an existing student from the list, OR\n"
                        "2. Fill in the student information to create a new student")
                    return
                
                # Create new student
                student_data = {
                    'name': self.name_var.get(),
                    'father_name': self.father_name_var.get(),
                    'gender': self.gender_var.get(),
                    'mobile_number': self.mobile_var.get(),
                    'aadhaar_number': self.aadhaar_var.get(),
                    'email': self.email_var.get(),
                    'locker_number': self.locker_var.get(),
                    'registration_date': self.reg_date_var.get()
                }
                
                validated_data = Validators.validate_student_data(student_data)
                student = Student(**validated_data)
                student_id = student.save()
            
            # Get selected timeslot and seat
            selected_timeslot = self.timeslots[self.timeslot_var.get()]
            seat_text = self.seat_var.get()
            seat_id = int(seat_text.split()[1])  # Extract seat number
            
            # Calculate dates
            duration_months = int(self.duration_var.get())
            start_date = date.today()
            from datetime import timedelta
            end_date = start_date + timedelta(days=30 * duration_months)
            
            # Create subscription
            subscription = Subscription(
                student_id=student_id,
                seat_id=seat_id,
                timeslot_id=selected_timeslot.id,
                start_date=start_date,
                end_date=end_date,
                amount_paid=float(self.amount_var.get())
            )
            
            # Validate subscription (includes overlap checking)
            errors = subscription.validate()
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            
            subscription.save()
            
            messagebox.showinfo("Success", 
                f"Subscription added successfully!\n"
                f"Receipt Number: {subscription.receipt_number}")
            
            # Refresh interface
            self.load_students()
            self.load_student_subscriptions(student_id)
            self.select_student_by_id(student_id)
            
            # Clear subscription form but keep student data
            self.clear_subscription_form()
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add subscription: {str(e)}")
    
    def clear_subscription_form(self):
        """Clear only the subscription form fields, keep student data"""
        self.timeslot_var.set("")
        self.seat_var.set("")
        self.duration_var.set("1")
        self.amount_var.set("")
    
    def generate_receipt(self):
        """Generate PDF receipt"""
        try:
            # Get selected subscription
            selection = self.subscription_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a subscription to generate receipt")
                return
            
            messagebox.showinfo("Info", "Receipt generation will be implemented with full PDF functionality")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate receipt: {str(e)}")
    
    def renew_subscription(self):
        """Renew subscription for selected student"""
        try:
            # Check if a student is selected
            selection = self.student_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a student to renew subscription")
                return
            
            # Get selected student
            item = self.student_tree.item(selection[0])
            student_id = item['values'][0]
            
            student = Student.get_by_id(student_id)
            if not student:
                messagebox.showerror("Error", "Student not found")
                return
            
            # Check for active subscriptions
            active_subscriptions = student.get_active_subscriptions()
            if not active_subscriptions:
                messagebox.showwarning("Warning", 
                    "This student has no active subscriptions to renew.\n"
                    "Please use 'Add Subscription' to create a new subscription.")
                return
            
            # Get the most recent active subscription
            latest_subscription = max(active_subscriptions, key=lambda s: s.end_date)
            
            # Populate form with existing subscription details
            timeslot = latest_subscription.get_timeslot()
            seat = latest_subscription.get_seat()
            
            # Find and set the timeslot
            for display_name, ts in self.timeslots.items():
                if ts.id == timeslot.id:
                    self.timeslot_var.set(display_name)
                    break
            
            # Trigger timeslot selection to load seats
            self.on_timeslot_selected(None)
            
            # Set the seat
            seat_display = f"Seat {seat.seat_number}"
            self.seat_var.set(seat_display)
            
            # Set default duration and amount (user can modify)
            self.duration_var.set("1")
            self.amount_var.set(str(latest_subscription.amount_paid))
            
            messagebox.showinfo("Ready to Renew", 
                f"Subscription details loaded for {student.name}.\n"
                f"Current subscription: {timeslot.start_time}-{timeslot.end_time}, {seat_display}\n"
                f"Modify duration/amount if needed, then click 'Add Subscription' to renew.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare subscription renewal: {str(e)}")
    
    
    def search_students(self):
        """Search students"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_students()
            return
        
        try:
            # Clear existing items
            for item in self.student_tree.get_children():
                self.student_tree.delete(item)
            
            students = Student.search(search_term)
            for student in students:
                active_subs = len(student.get_active_subscriptions())
                
                self.student_tree.insert('', 'end', values=(
                    student.id,
                    student.name,
                    student.gender,
                    student.mobile_number,
                    student.registration_date,
                    active_subs
                ))
        
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
    
    def refresh(self):
        """Refresh the interface"""
        self.load_data()
    
    def on_subscription_select(self, event):
        """Handle subscription selection"""
        selection = self.subscription_tree.selection()
        if selection:
            # Enable subscription management buttons based on selection
            pass
    
    def get_selected_subscription(self):
        """Get the currently selected subscription"""
        selection = self.subscription_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a subscription first.")
            return None
        
        # Get selected student
        student_selection = self.student_tree.selection()
        if not student_selection:
            messagebox.showwarning("No Student", "Please select a student first.")
            return None
        
        try:
            # Get student ID
            student_item = self.student_tree.item(student_selection[0])
            student_id = student_item['values'][0]
            
            # Get subscription data from tree
            subscription_item = self.subscription_tree.item(selection[0])
            receipt_number = subscription_item['values'][0]
            
            # Find the subscription by receipt number
            subscriptions = Subscription.get_by_student_id(student_id, active_only=False)
            for sub in subscriptions:
                if sub.receipt_number == receipt_number:
                    return sub
            
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get subscription: {str(e)}")
            return None
    
    def edit_subscription(self):
        """Edit selected subscription"""
        subscription = self.get_selected_subscription()
        if not subscription:
            return
        
        # Create edit dialog
        dialog = SubscriptionEditDialog(self, subscription)
        self.wait_window(dialog)
        
        # Refresh if subscription was updated
        if hasattr(dialog, 'updated') and dialog.updated:
            student_selection = self.student_tree.selection()
            if student_selection:
                student_item = self.student_tree.item(student_selection[0])
                student_id = student_item['values'][0]
                self.load_student_subscriptions(student_id)
                self.load_students()  # Refresh student list to update subscription count
    
    def renew_subscription(self):
        """Renew selected subscription"""
        subscription = self.get_selected_subscription()
        if not subscription:
            return
        
        # Create renewal dialog
        dialog = SubscriptionRenewalDialog(self, subscription)
        self.wait_window(dialog)
        
        # Refresh if subscription was renewed
        if hasattr(dialog, 'renewed') and dialog.renewed:
            student_selection = self.student_tree.selection()
            if student_selection:
                student_item = self.student_tree.item(student_selection[0])
                student_id = student_item['values'][0]
                self.load_student_subscriptions(student_id)
                self.load_students()  # Refresh student list to update subscription count
    
    def delete_subscription(self):
        """Delete selected subscription"""
        subscription = self.get_selected_subscription()
        if not subscription:
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete subscription {subscription.receipt_number}?\n\n"
            f"This action cannot be undone!"
        )
        
        if result:
            try:
                subscription.delete()
                messagebox.showinfo("Success", "Subscription deleted successfully!")
                
                # Refresh displays
                student_selection = self.student_tree.selection()
                if student_selection:
                    student_item = self.student_tree.item(student_selection[0])
                    student_id = student_item['values'][0]
                    self.load_student_subscriptions(student_id)
                    self.load_students()  # Refresh student list to update subscription count
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete subscription: {str(e)}")
    
    def view_receipt(self):
        """View receipt for selected subscription"""
        subscription = self.get_selected_subscription()
        if not subscription:
            return
        
        try:
            from utils.pdf_generator import PDFGenerator
            
            # Get student data
            student = Student.get_by_id(subscription.student_id)
            seat = Seat.get_by_id(subscription.seat_id)
            timeslot = Timeslot.get_by_id(subscription.timeslot_id)
            
            if not all([student, seat, timeslot]):
                messagebox.showerror("Error", "Failed to get complete subscription data")
                return
            
            # Generate PDF
            pdf_generator = PDFGenerator()
            filename = f"receipt_{subscription.receipt_number}.pdf"
            
            success, result = pdf_generator.generate_subscription_receipt(
                subscription, student, seat, timeslot, filename
            )
            
            if success:
                messagebox.showinfo("Success", f"Receipt saved as {filename}")
                # Open the PDF file
                import subprocess
                import os
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(result)
                    elif os.name == 'posix':  # Linux/Mac
                        subprocess.run(['xdg-open', result], check=True)
                except Exception as e:
                    print(f"Could not open PDF: {e}")
            else:
                messagebox.showerror("Error", f"Failed to generate receipt: {result}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate receipt: {str(e)}")


class SubscriptionEditDialog(tk.Toplevel):
    """Dialog for editing subscription details"""
    
    def __init__(self, parent, subscription):
        super().__init__(parent)
        self.subscription = subscription
        self.updated = False
        
        self.title("Edit Subscription")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text="Edit Subscription Details", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill='x', pady=10)
        
        # Receipt number (read-only)
        ttk.Label(fields_frame, text="Receipt Number:").grid(row=0, column=0, sticky='w', pady=5)
        self.receipt_label = ttk.Label(fields_frame, text="", foreground='blue')
        self.receipt_label.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Start date
        ttk.Label(fields_frame, text="Start Date:").grid(row=1, column=0, sticky='w', pady=5)
        self.start_date_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.start_date_var, width=25).grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # End date
        ttk.Label(fields_frame, text="End Date:").grid(row=2, column=0, sticky='w', pady=5)
        self.end_date_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.end_date_var, width=25).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Amount paid
        ttk.Label(fields_frame, text="Amount Paid:").grid(row=3, column=0, sticky='w', pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.amount_var, width=25).grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Status
        ttk.Label(fields_frame, text="Status:").grid(row=4, column=0, sticky='w', pady=5)
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(fields_frame, textvariable=self.status_var, 
                                   values=['Active', 'Inactive'], state='readonly', width=22)
        status_combo.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="Save Changes", 
                  command=self.save_changes).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.destroy).pack(side='right', padx=5)
    
    def load_data(self):
        """Load subscription data into form"""
        self.receipt_label.config(text=self.subscription.receipt_number)
        self.start_date_var.set(self.subscription.start_date)
        self.end_date_var.set(self.subscription.end_date)
        self.amount_var.set(str(self.subscription.amount_paid))
        self.status_var.set('Active' if self.subscription.is_active else 'Inactive')
    
    def save_changes(self):
        """Save subscription changes"""
        try:
            # Validate dates
            from datetime import datetime
            start_date = datetime.strptime(self.start_date_var.get(), '%Y-%m-%d').date()
            end_date = datetime.strptime(self.end_date_var.get(), '%Y-%m-%d').date()
            
            if end_date <= start_date:
                messagebox.showerror("Error", "End date must be after start date")
                return
            
            # Validate amount
            try:
                amount = float(self.amount_var.get())
                if amount < 0:
                    raise ValueError("Amount cannot be negative")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
                return
            
            # Update subscription
            self.subscription.start_date = self.start_date_var.get()
            self.subscription.end_date = self.end_date_var.get()
            self.subscription.amount_paid = amount
            self.subscription.is_active = (self.status_var.get() == 'Active')
            
            self.subscription.save()
            
            self.updated = True
            messagebox.showinfo("Success", "Subscription updated successfully!")
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update subscription: {str(e)}")


class SubscriptionRenewalDialog(tk.Toplevel):
    """Dialog for renewing subscription"""
    
    def __init__(self, parent, subscription):
        super().__init__(parent)
        self.subscription = subscription
        self.renewed = False
        
        self.title("Renew Subscription")
        self.geometry("450x350")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text="Renew Subscription", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Current subscription info
        info_frame = ttk.LabelFrame(main_frame, text="Current Subscription", padding=10)
        info_frame.pack(fill='x', pady=10)
        
        ttk.Label(info_frame, text=f"Receipt: {self.subscription.receipt_number}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Current End Date: {self.subscription.end_date}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Current Amount: Rs. {self.subscription.amount_paid}").pack(anchor='w')
        
        # Renewal form
        renewal_frame = ttk.LabelFrame(main_frame, text="Renewal Details", padding=10)
        renewal_frame.pack(fill='x', pady=10)
        
        # Duration
        ttk.Label(renewal_frame, text="Extend by (days):").grid(row=0, column=0, sticky='w', pady=5)
        self.days_var = tk.StringVar(value="30")
        ttk.Entry(renewal_frame, textvariable=self.days_var, width=10).grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Quick duration buttons
        duration_frame = ttk.Frame(renewal_frame)
        duration_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Button(duration_frame, text="1 Month", width=8,
                  command=lambda: self.days_var.set("30")).pack(side='left', padx=2)
        ttk.Button(duration_frame, text="3 Months", width=8,
                  command=lambda: self.days_var.set("90")).pack(side='left', padx=2)
        ttk.Button(duration_frame, text="6 Months", width=8,
                  command=lambda: self.days_var.set("180")).pack(side='left', padx=2)
        
        # Amount
        ttk.Label(renewal_frame, text="Amount:").grid(row=2, column=0, sticky='w', pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(renewal_frame, textvariable=self.amount_var, width=15).grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # New end date (calculated)
        ttk.Label(renewal_frame, text="New End Date:").grid(row=3, column=0, sticky='w', pady=5)
        self.new_end_date_label = ttk.Label(renewal_frame, text="", foreground='blue')
        self.new_end_date_label.grid(row=3, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Bind days change to update end date
        self.days_var.trace('w', self.calculate_new_end_date)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="Renew Subscription", 
                  command=self.renew_subscription).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.destroy).pack(side='right', padx=5)
    
    def load_data(self):
        """Load default renewal data"""
        # Get timeslot to suggest amount
        timeslot = Timeslot.get_by_id(self.subscription.timeslot_id)
        if timeslot:
            self.amount_var.set(str(timeslot.price))
        
        self.calculate_new_end_date()
    
    def calculate_new_end_date(self, *args):
        """Calculate and display new end date"""
        try:
            days = int(self.days_var.get())
            from datetime import datetime, timedelta
            
            current_end = datetime.strptime(self.subscription.end_date, '%Y-%m-%d').date()
            new_end = current_end + timedelta(days=days)
            
            self.new_end_date_label.config(text=str(new_end))
        except (ValueError, TypeError):
            self.new_end_date_label.config(text="Invalid days")
    
    def renew_subscription(self):
        """Renew the subscription"""
        try:
            # Validate inputs
            days = int(self.days_var.get())
            if days <= 0:
                messagebox.showerror("Error", "Days must be positive")
                return
            
            amount = float(self.amount_var.get())
            if amount < 0:
                messagebox.showerror("Error", "Amount cannot be negative")
                return
            
            # Calculate new end date
            from datetime import datetime, timedelta
            current_end = datetime.strptime(self.subscription.end_date, '%Y-%m-%d').date()
            new_end = current_end + timedelta(days=days)
            
            # Create renewal (new subscription record)
            new_subscription = Subscription(
                student_id=self.subscription.student_id,
                seat_id=self.subscription.seat_id,
                timeslot_id=self.subscription.timeslot_id,
                start_date=str(current_end + timedelta(days=1)),
                end_date=str(new_end),
                amount_paid=amount,
                payment_date=str(date.today()),
                is_active=True
            )
            
            new_subscription.save()
            
            # Generate receipt
            try:
                from utils.pdf_generator import PDFGenerator
                student = Student.get_by_id(self.subscription.student_id)
                seat = Seat.get_by_id(self.subscription.seat_id)
                timeslot = Timeslot.get_by_id(self.subscription.timeslot_id)
                
                pdf_generator = PDFGenerator()
                filename = f"renewal_receipt_{new_subscription.receipt_number}.pdf"
                
                success, result = pdf_generator.generate_renewal_receipt(
                    new_subscription, student, seat, timeslot, filename
                )
                
                if success:
                    logging.info(f"Renewal receipt generated: {result}")
                else:
                    logging.error(f"Receipt generation failed: {result}")
                    
            except Exception as e:
                logging.error(f"Receipt generation failed: {e}")
            
            self.renewed = True
            messagebox.showinfo("Success", f"Subscription renewed successfully!\nNew receipt: {new_subscription.receipt_number}")
            self.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for days and amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to renew subscription: {str(e)}")
