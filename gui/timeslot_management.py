"""
Timeslot management interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from models.timeslot import Timeslot
from utils.validators import Validators, ValidationError


class TimeslotManagementFrame(ttk.Frame):
    """Timeslot management interface"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup user interface"""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel - Form
        self.create_form_panel(main_frame)
        
        # Right panel - List
        self.create_list_panel(main_frame)
    
    def create_form_panel(self, parent):
        """Create timeslot form panel"""
        form_frame = ttk.LabelFrame(parent, text="Timeslot Information", padding=10)
        form_frame.pack(side='left', fill='y', padx=(0, 10))
        
        row = 0
        
        # Name
        ttk.Label(form_frame, text="Timeslot Name *:").grid(row=row, column=0, sticky='w', pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var, width=25).grid(row=row, column=1, pady=2)
        row += 1
        
        # Start Time
        ttk.Label(form_frame, text="Start Time *:").grid(row=row, column=0, sticky='w', pady=2)
        self.start_time_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.start_time_var, width=25).grid(row=row, column=1, pady=2)
        ttk.Label(form_frame, text="(HH:MM format)", font=('Arial', 8)).grid(row=row, column=2, sticky='w', padx=5)
        row += 1
        
        # End Time
        ttk.Label(form_frame, text="End Time *:").grid(row=row, column=0, sticky='w', pady=2)
        self.end_time_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.end_time_var, width=25).grid(row=row, column=1, pady=2)
        ttk.Label(form_frame, text="(HH:MM format)", font=('Arial', 8)).grid(row=row, column=2, sticky='w', padx=5)
        row += 1
        
        # Price
        ttk.Label(form_frame, text="Price (₹) *:").grid(row=row, column=0, sticky='w', pady=2)
        self.price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.price_var, width=25).grid(row=row, column=1, pady=2)
        row += 1
        
        # Duration
        ttk.Label(form_frame, text="Duration (months) *:").grid(row=row, column=0, sticky='w', pady=2)
        self.duration_var = tk.StringVar(value="1")
        ttk.Entry(form_frame, textvariable=self.duration_var, width=25).grid(row=row, column=1, pady=2)
        row += 1
        
        # Lockers Available
        ttk.Label(form_frame, text="Lockers Available:").grid(row=row, column=0, sticky='w', pady=2)
        self.lockers_var = tk.StringVar(value="0")
        ttk.Entry(form_frame, textvariable=self.lockers_var, width=25).grid(row=row, column=1, pady=2)
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Save Timeslot", command=self.save_timeslot).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete Timeslot", command=self.delete_timeslot).grid(row=0, column=2, padx=5)
        
        # Current timeslot ID (for editing)
        self.current_timeslot_id = None
    
    def create_list_panel(self, parent):
        """Create timeslot list panel"""
        list_frame = ttk.LabelFrame(parent, text="Timeslots", padding=10)
        list_frame.pack(side='right', fill='both', expand=True)
        
        # Timeslot tree
        columns = ('ID', 'Name', 'Start Time', 'End Time', 'Price', 'Duration', 'Lockers', 'Occupancy')
        self.timeslot_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.timeslot_tree.heading(col, text=col)
            if col == 'Name':
                self.timeslot_tree.column(col, width=150)
            elif col in ['Start Time', 'End Time']:
                self.timeslot_tree.column(col, width=80)
            else:
                self.timeslot_tree.column(col, width=70)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.timeslot_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.timeslot_tree.xview)
        self.timeslot_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.timeslot_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Bind selection event
        self.timeslot_tree.bind('<<TreeviewSelect>>', self.on_timeslot_select)
        
        # Refresh button
        ttk.Button(list_frame, text="Refresh", command=self.load_data).grid(row=2, column=0, pady=10)
    
    def load_data(self):
        """Load timeslots into the tree"""
        # Clear existing items
        for item in self.timeslot_tree.get_children():
            self.timeslot_tree.delete(item)
        
        try:
            timeslots = Timeslot.get_all()
            for timeslot in timeslots:
                # Calculate occupancy rate
                occupancy_rate = timeslot.get_occupancy_rate()
                
                self.timeslot_tree.insert('', 'end', values=(
                    timeslot.id,
                    timeslot.name,
                    timeslot.start_time,
                    timeslot.end_time,
                    f"₹{timeslot.price}",
                    f"{timeslot.duration_months} months",
                    timeslot.lockers_available,
                    f"{occupancy_rate:.1f}%"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load timeslots: {str(e)}")
    
    def on_timeslot_select(self, event):
        """Handle timeslot selection"""
        selection = self.timeslot_tree.selection()
        if not selection:
            return
        
        try:
            # Get selected timeslot
            item = self.timeslot_tree.item(selection[0])
            timeslot_id = item['values'][0]
            
            timeslot = Timeslot.get_by_id(timeslot_id)
            if timeslot:
                # Populate form
                self.current_timeslot_id = timeslot.id
                self.name_var.set(timeslot.name)
                self.start_time_var.set(timeslot.start_time)
                self.end_time_var.set(timeslot.end_time)
                self.price_var.set(str(timeslot.price))
                self.duration_var.set(str(timeslot.duration_months))
                self.lockers_var.set(str(timeslot.lockers_available))
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load timeslot details: {str(e)}")
    
    def save_timeslot(self):
        """Save timeslot"""
        try:
            # Validate input
            name = self.name_var.get().strip()
            if not name:
                raise ValidationError("Timeslot name is required")
            
            start_time = Validators.validate_time(self.start_time_var.get(), "Start time")
            end_time = Validators.validate_time(self.end_time_var.get(), "End time")
            price = Validators.validate_amount(self.price_var.get())
            duration = Validators.validate_duration_months(self.duration_var.get())
            
            # Validate lockers available (must be non-negative integer)
            lockers_str = self.lockers_var.get().strip()
            if not lockers_str:
                lockers = 0
            else:
                try:
                    lockers = int(lockers_str)
                    if lockers < 0:
                        raise ValidationError("Number of lockers cannot be negative")
                except ValueError:
                    raise ValidationError("Number of lockers must be a valid integer")
            
            # Create or update timeslot
            if self.current_timeslot_id:
                # Update existing
                timeslot = Timeslot.get_by_id(self.current_timeslot_id)
                if not timeslot:
                    raise Exception("Timeslot not found")
                
                timeslot.name = name
                timeslot.start_time = start_time
                timeslot.end_time = end_time
                timeslot.price = price
                timeslot.duration_months = duration
                timeslot.lockers_available = lockers
                timeslot.lockers_available = lockers
            else:
                # Create new
                timeslot = Timeslot(
                    name=name,
                    start_time=start_time,
                    end_time=end_time,
                    price=price,
                    duration_months=duration,
                    lockers_available=lockers
                )
            
            # Validate timeslot
            errors = timeslot.validate()
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            
            timeslot.save()
            
            messagebox.showinfo("Success", "Timeslot saved successfully!")
            self.load_data()
            self.clear_form()
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save timeslot: {str(e)}")
    
    def clear_form(self):
        """Clear the form"""
        self.current_timeslot_id = None
        self.name_var.set("")
        self.start_time_var.set("")
        self.end_time_var.set("")
        self.price_var.set("")
        self.duration_var.set("1")
        self.lockers_var.set("0")
    
    def delete_timeslot(self):
        """Delete selected timeslot"""
        if not self.current_timeslot_id:
            messagebox.showwarning("Warning", "Please select a timeslot to delete")
            return
        
        try:
            # Confirm deletion
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this timeslot?"):
                timeslot = Timeslot.get_by_id(self.current_timeslot_id)
                if timeslot:
                    timeslot.delete()
                    messagebox.showinfo("Success", "Timeslot deleted successfully!")
                    self.load_data()
                    self.clear_form()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete timeslot: {str(e)}")
    
    def refresh(self):
        """Refresh the interface"""
        self.load_data()
