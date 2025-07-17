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
        self.refresh_callback = None  # Callback for when timeslots are updated
        self.setup_ui()
        self.load_data()
    
    def set_refresh_callback(self, callback):
        """Set callback function to refresh other interfaces when timeslots change"""
        self.refresh_callback = callback
    
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
        
        # Create time options (24-hour format)
        time_options = self._generate_time_options()
        
        start_time_combo = ttk.Combobox(form_frame, textvariable=self.start_time_var, 
                                       values=time_options, state='readonly', width=22)
        start_time_combo.grid(row=row, column=1, pady=2)
        ttk.Label(form_frame, text="Select from dropdown", font=('Arial', 8)).grid(row=row, column=2, sticky='w', padx=5)
        row += 1
        
        # End Time
        ttk.Label(form_frame, text="End Time *:").grid(row=row, column=0, sticky='w', pady=2)
        self.end_time_var = tk.StringVar()
        
        end_time_combo = ttk.Combobox(form_frame, textvariable=self.end_time_var, 
                                     values=time_options, state='readonly', width=22)
        end_time_combo.grid(row=row, column=1, pady=2)
        ttk.Label(form_frame, text="Select from dropdown", font=('Arial', 8)).grid(row=row, column=2, sticky='w', padx=5)
        row += 1
        
        # Help text for overnight timeslots
        help_label = ttk.Label(form_frame, text="💡 For overnight timeslots: Start 21:00, End 05:00 (next day)", 
                              font=('Arial', 8), foreground='blue')
        help_label.grid(row=row, column=0, columnspan=3, sticky='w', pady=(0, 5))
        row += 1
        
        # Quick preset buttons
        preset_frame = ttk.LabelFrame(form_frame, text="Quick Presets", padding=5)
        preset_frame.grid(row=row, column=0, columnspan=3, sticky='ew', pady=5)
        row += 1
        
        # Preset buttons
        preset_row = 0
        
        # Morning shift
        ttk.Button(preset_frame, text="Morning (06:00-12:00)", 
                  command=lambda: self._set_preset("06:00", "12:00")).grid(row=preset_row, column=0, padx=2, pady=2)
        ttk.Button(preset_frame, text="Afternoon (12:00-18:00)", 
                  command=lambda: self._set_preset("12:00", "18:00")).grid(row=preset_row, column=1, padx=2, pady=2)
        ttk.Button(preset_frame, text="Evening (18:00-21:00)", 
                  command=lambda: self._set_preset("18:00", "21:00")).grid(row=preset_row, column=2, padx=2, pady=2)
        preset_row += 1
        
        # Night and extended shifts
        ttk.Button(preset_frame, text="Night (21:00-05:00)", 
                  command=lambda: self._set_preset("21:00", "05:00")).grid(row=preset_row, column=0, padx=2, pady=2)
        ttk.Button(preset_frame, text="Early Morning (05:00-09:00)", 
                  command=lambda: self._set_preset("05:00", "09:00")).grid(row=preset_row, column=1, padx=2, pady=2)
        ttk.Button(preset_frame, text="Late Night (22:00-06:00)", 
                  command=lambda: self._set_preset("22:00", "06:00")).grid(row=preset_row, column=2, padx=2, pady=2)
        
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
        self.lockers_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(form_frame, text="Yes, lockers are available", 
                       variable=self.lockers_var).grid(row=row, column=1, sticky='w', pady=2)
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
        
        # Refresh button        ttk.Button(list_frame, text="Refresh", command=self.load_data).grid(row=2, column=0, pady=10)
    
    def _generate_time_options(self):
        """Generate time options for dropdown (every 30 minutes)"""
        time_options = []
        
        # Generate times from 00:00 to 23:30 in 30-minute intervals
        for hour in range(24):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                time_options.append(time_str)
        
        # Add some common specific times that might be used
        common_times = ["05:00", "05:30", "06:00", "06:30", "07:00", "07:30", "08:00", "08:30", 
                       "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
                       "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
                       "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
                       "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"]
        
        # Remove duplicates and sort
        all_times = list(set(time_options))
        all_times.sort()
        
        return all_times

    def _set_preset(self, start_time, end_time):
        """Set preset start and end times"""
        self.start_time_var.set(start_time)
        self.end_time_var.set(end_time)

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
                
                # Format time display for overnight timeslots
                start_time = timeslot.start_time
                end_time = timeslot.end_time
                
                # Check if it's an overnight timeslot
                try:
                    from datetime import time
                    if isinstance(start_time, str):
                        start_hour = int(start_time.split(':')[0])
                    else:
                        start_hour = start_time.hour if hasattr(start_time, 'hour') else 0
                        
                    if isinstance(end_time, str):
                        end_hour = int(end_time.split(':')[0])
                    else:
                        end_hour = end_time.hour if hasattr(end_time, 'hour') else 0
                    
                    # If start time is greater than end time, it's overnight
                    time_display = f"{start_time} - {end_time}"
                    if start_hour > end_hour or (start_hour > 18 and end_hour < 12):
                        time_display = f"{start_time} - {end_time} (next day)"
                except:
                    time_display = f"{start_time} - {end_time}"
                
                self.timeslot_tree.insert('', 'end', values=(
                    timeslot.id,
                    timeslot.name,
                    start_time,
                    end_time,
                    f"₹{timeslot.price}",
                    f"{timeslot.duration_months} months",
                    "Yes" if timeslot.lockers_available else "No",
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
                self.lockers_var.set(timeslot.lockers_available)
        
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
            
            # Get lockers availability (boolean value)
            lockers_available = self.lockers_var.get()
            
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
                timeslot.lockers_available = lockers_available
            else:
                # Create new
                timeslot = Timeslot(
                    name=name,
                    start_time=start_time,
                    end_time=end_time,
                    price=price,
                    duration_months=duration,
                    lockers_available=lockers_available
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
            
            # Refresh other interfaces that depend on timeslots
            if self.refresh_callback:
                self.refresh_callback()
            
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
        self.lockers_var.set(False)
    
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
                    
                    # Refresh other interfaces that depend on timeslots
                    if self.refresh_callback:
                        self.refresh_callback()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete timeslot: {str(e)}")
    
    def refresh(self):
        """Refresh the interface"""
        self.load_data()
