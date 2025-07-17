"""
Student management interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
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
        
        ttk.Button(reg_date_frame, text="Today", 
                  command=self.set_today_date, width=8).grid(row=0, column=1, padx=(5,0))
        
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
        ttk.Label(parent, text="Add Subscription", font=('Arial', 10, 'bold')).grid(row=start_row, column=0, columnspan=2, pady=5)
        start_row += 1
        
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
            self.subscription_tree.column(col, width=80)
        
        self.subscription_tree.grid(row=0, column=0, sticky='nsew')
        
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
            timeslot_values = [f"{ts.name} ({ts.start_time}-{ts.end_time}) - ₹{ts.price}" for ts in timeslots]
            self.timeslot_combo['values'] = timeslot_values
            
            # Store timeslot objects for reference
            self.timeslots = {f"{ts.name} ({ts.start_time}-{ts.end_time}) - ₹{ts.price}": ts for ts in timeslots}
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
                # Get related data
                seat = Seat.get_by_id(sub.seat_id)
                timeslot = Timeslot.get_by_id(sub.timeslot_id)
                
                status = "Active" if sub.is_active and not sub.is_expired() else "Expired"
                
                self.subscription_tree.insert('', 'end', values=(
                    sub.receipt_number,
                    f"Seat {seat.id}" if seat else "N/A",
                    timeslot.name if timeslot else "N/A",
                    sub.start_date,
                    sub.end_date,
                    f"₹{sub.amount_paid}",
                    status
                ))
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load subscriptions: {str(e)}")
    
    def save_student(self):
        """Save student with mandatory subscription for new students"""
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
            
            # Check if this is a new student or update
            if hasattr(self, 'current_student_id') and self.current_student_id:
                # Update existing student
                student = Student.get_by_id(self.current_student_id)
                if student:
                    for key, value in validated_data.items():
                        setattr(student, key, value)
                    student.save()
                    
                    messagebox.showinfo("Success", "Student updated successfully!")
                    self.load_students()
                    self.clear_form()
                    return
            
            # For NEW students, we must create a subscription
            # First validate that subscription details are provided
            if not self.timeslot_var.get():
                messagebox.showerror("Error", 
                    "For new students, you MUST select a timeslot.\n"
                    "Please select a timeslot to create their subscription.")
                return
            
            if not self.seat_var.get():
                messagebox.showerror("Error", 
                    "For new students, you MUST select a seat.\n"
                    "Please select a seat for their subscription.")
                return
            
            if not self.amount_var.get():
                messagebox.showerror("Error", 
                    "For new students, you MUST enter subscription amount.\n"
                    "Please enter the amount for their subscription.")
                return
            
            # Create the student first
            student = Student(**validated_data)
            student_id = student.save()
            
            # Now create the mandatory subscription
            self.create_mandatory_subscription(student_id, validated_data['name'])
            
            messagebox.showinfo("Success", 
                f"Student '{validated_data['name']}' and subscription created successfully!")
            self.load_students()
            self.clear_form()
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save student: {str(e)}")
    
    def create_mandatory_subscription(self, student_id, student_name):
        """Create mandatory subscription for new student"""
        try:
            # Get selected timeslot
            timeslot_key = self.timeslot_var.get()
            if timeslot_key not in self.timeslots:
                raise Exception("Invalid timeslot selected")
            
            selected_timeslot = self.timeslots[timeslot_key]
            
            # Get selected seat
            seat_key = self.seat_var.get()
            if seat_key not in self.available_seats:
                raise Exception("Invalid seat selected")
            
            selected_seat = self.available_seats[seat_key]
            
            # Get subscription details
            duration = int(self.duration_var.get())
            amount = float(self.amount_var.get())
            
            # Calculate dates
            from datetime import date, timedelta
            start_date = date.today()
            end_date = start_date + timedelta(days=30 * duration)
            
            # Create subscription
            subscription = Subscription(
                student_id=student_id,
                seat_id=selected_seat.id,
                timeslot_id=selected_timeslot.id,
                start_date=start_date,
                end_date=end_date,
                amount_paid=amount
            )
            
            # Validate and save subscription
            errors = subscription.validate()
            if errors:
                raise Exception(f"Subscription validation failed: {', '.join(errors)}")
            
            subscription.save()
            
        except Exception as e:
            # If subscription creation fails, we should delete the student
            try:
                student = Student.get_by_id(student_id)
                if student:
                    student.delete()
            except:
                pass
            raise Exception(f"Failed to create subscription: {e}")
    
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
            # Validate student exists
            if not self.name_var.get():
                messagebox.showwarning("Warning", "Please create or select a student first")
                return
            
            # Get or create student
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
            
            # Validate subscription data
            if not self.timeslot_var.get():
                messagebox.showwarning("Warning", "Please select a timeslot")
                return
            
            if not self.seat_var.get():
                messagebox.showwarning("Warning", "Please select a seat")
                return
            
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
            
            # Validate subscription
            errors = subscription.validate()
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            
            subscription.save()
            
            messagebox.showinfo("Success", "Subscription added successfully!")
            self.load_students()
            self.load_student_subscriptions(student_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add subscription: {str(e)}")
    
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
