"""
Seat management interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from models.seat import Seat
from models.subscription import Subscription
from config.database import DatabaseManager


class SeatManagementFrame(ttk.Frame):
    """Seat management interface"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup user interface"""
        # Create main paned window
        self.paned_window = ttk.PanedWindow(self, orient='horizontal')
        self.paned_window.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - Seat editor
        self.create_seat_editor()
        
        # Right panel - Seat grid view
        self.create_seat_grid()
    
    def create_seat_editor(self):
        """Create seat editor panel"""
        # Left frame for seat editing
        editor_frame = ttk.LabelFrame(self.paned_window, text="Seat Editor", padding=10)
        self.paned_window.add(editor_frame, weight=1)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(editor_frame, text="Editor Mode", padding=5)
        mode_frame.pack(fill='x', pady=(0, 10))
        
        self.editor_mode = tk.StringVar(value="edit")
        ttk.Radiobutton(mode_frame, text="Edit Existing Seat", variable=self.editor_mode, 
                       value="edit", command=self.change_editor_mode).pack(side='left', padx=5)
        ttk.Radiobutton(mode_frame, text="Add New Seat", variable=self.editor_mode, 
                       value="add", command=self.change_editor_mode).pack(side='left', padx=5)
        
        # Seat information
        info_frame = ttk.LabelFrame(editor_frame, text="Seat Information", padding=10)
        info_frame.pack(fill='x', pady=(0, 10))
        
        # Seat ID
        ttk.Label(info_frame, text="Seat ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.seat_id_var = tk.StringVar()
        self.seat_id_entry = ttk.Entry(info_frame, textvariable=self.seat_id_var, state='readonly', width=15)
        self.seat_id_entry.grid(row=0, column=1, pady=2, sticky='w')
        
        # Row Number
        ttk.Label(info_frame, text="Row Number:").grid(row=1, column=0, sticky='w', pady=2)
        self.row_number_var = tk.StringVar()
        self.row_entry = ttk.Entry(info_frame, textvariable=self.row_number_var, state='readonly', width=15)
        self.row_entry.grid(row=1, column=1, pady=2, sticky='w')
        
        # Gender Restriction
        ttk.Label(info_frame, text="Gender Restriction:").grid(row=2, column=0, sticky='w', pady=2)
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(info_frame, textvariable=self.gender_var, 
                                   values=['Male', 'Female', 'Any'], state='disabled', width=15)
        self.gender_combo.grid(row=2, column=1, pady=2, sticky='w')
        
        # Current Status
        ttk.Label(info_frame, text="Current Status:").grid(row=3, column=0, sticky='w', pady=2)
        self.status_var = tk.StringVar(value="Select mode and seat")
        status_label = ttk.Label(info_frame, textvariable=self.status_var, foreground='blue')
        status_label.grid(row=3, column=1, pady=2, sticky='w')
        
        # Buttons
        button_frame = ttk.Frame(info_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky='ew')
        
        self.save_btn = ttk.Button(button_frame, text="Save Seat", command=self.save_seat)
        self.save_btn.pack(side='left', padx=5)
        
        self.update_btn = ttk.Button(button_frame, text="Update Gender", command=self.update_seat_gender)
        self.update_btn.pack(side='left', padx=5)
        
        self.delete_btn = ttk.Button(button_frame, text="Delete Seat", command=self.delete_seat)
        self.delete_btn.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="View Occupancy", command=self.view_seat_occupancy).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Selection", command=self.clear_selection).pack(side='left', padx=5)
        
        # Diagnostic buttons
        diagnostic_frame = ttk.Frame(info_frame)
        diagnostic_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky='ew')
        
        ttk.Button(diagnostic_frame, text="Diagnose Seat", command=self.diagnose_seat_occupancy).pack(side='left', padx=5)
        ttk.Button(diagnostic_frame, text="Cleanup Expired", command=self.cleanup_expired_subscriptions).pack(side='left', padx=5)
        
        # Initially disable all buttons
        self.save_btn.config(state='disabled')
        self.update_btn.config(state='disabled')
        self.delete_btn.config(state='disabled')
        
        # Occupancy Details
        occupancy_frame = ttk.LabelFrame(editor_frame, text="Current Occupancy", padding=10)
        occupancy_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Occupancy tree
        columns = ('Timeslot', 'Student', 'Start Date', 'End Date', 'Status')
        self.occupancy_tree = ttk.Treeview(occupancy_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.occupancy_tree.heading(col, text=col)
            self.occupancy_tree.column(col, width=100)
        
        # Scrollbars for occupancy tree
        v_scrollbar = ttk.Scrollbar(occupancy_frame, orient='vertical', command=self.occupancy_tree.yview)
        h_scrollbar = ttk.Scrollbar(occupancy_frame, orient='horizontal', command=self.occupancy_tree.xview)
        self.occupancy_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for tree and scrollbars
        self.occupancy_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        occupancy_frame.rowconfigure(0, weight=1)
        occupancy_frame.columnconfigure(0, weight=1)
    
    def create_seat_grid(self):
        """Create seat grid visualization"""
        # Right frame for seat grid
        grid_frame = ttk.LabelFrame(self.paned_window, text="Seat Layout", padding=10)
        self.paned_window.add(grid_frame, weight=2)
        
        # Control frame
        control_frame = ttk.Frame(grid_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(control_frame, text="Refresh Layout", command=self.load_data).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Reset All Seats", command=self.reset_all_seats).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Fix Occupancy Issues", command=self.cleanup_expired_subscriptions).pack(side='left', padx=5)
        
        # Legend
        legend_frame = ttk.Frame(control_frame)
        legend_frame.pack(side='right')
        
        tk.Label(legend_frame, text="Legend:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        # Male seats
        male_frame = tk.Frame(legend_frame)
        male_frame.pack(side='left', padx=5)
        tk.Canvas(male_frame, width=20, height=20, bg='lightblue').pack(side='left')
        tk.Label(male_frame, text="Male").pack(side='left', padx=2)
        
        # Female seats
        female_frame = tk.Frame(legend_frame)
        female_frame.pack(side='left', padx=5)
        tk.Canvas(female_frame, width=20, height=20, bg='lightpink').pack(side='left')
        tk.Label(female_frame, text="Female").pack(side='left', padx=2)
        
        # Any gender
        any_frame = tk.Frame(legend_frame)
        any_frame.pack(side='left', padx=5)
        tk.Canvas(any_frame, width=20, height=20, bg='lightgreen').pack(side='left')
        tk.Label(any_frame, text="Any").pack(side='left', padx=2)
        
        # Occupied seats
        occupied_frame = tk.Frame(legend_frame)
        occupied_frame.pack(side='left', padx=5)
        tk.Canvas(occupied_frame, width=20, height=20, bg='lightcoral').pack(side='left')
        tk.Label(occupied_frame, text="Occupied").pack(side='left', padx=2)
        
        # Canvas for seat layout
        canvas_frame = ttk.Frame(grid_frame)
        canvas_frame.pack(fill='both', expand=True)
        
        self.seat_canvas = tk.Canvas(canvas_frame, bg='white')
        
        # Canvas scrollbars
        canvas_v_scroll = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.seat_canvas.yview)
        canvas_h_scroll = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.seat_canvas.xview)
        self.seat_canvas.configure(yscrollcommand=canvas_v_scroll.set, xscrollcommand=canvas_h_scroll.set)
        
        # Grid layout for canvas and scrollbars
        self.seat_canvas.grid(row=0, column=0, sticky='nsew')
        canvas_v_scroll.grid(row=0, column=1, sticky='ns')
        canvas_h_scroll.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        
        # Configure canvas scroll region
        self.seat_canvas.bind('<Configure>', self.on_canvas_configure)
    
    def on_canvas_configure(self, event):
        """Configure canvas scroll region"""
        self.seat_canvas.configure(scrollregion=self.seat_canvas.bbox("all"))
    
    def load_data(self):
        """Load seat data"""
        self.draw_seat_layout()
        self.clear_selection()
    
    def draw_seat_layout(self):
        """Draw seat layout on canvas"""
        try:
            self.seat_canvas.delete("all")
            
            # Get all seats
            seats = Seat.get_all()
            if not seats:
                self.seat_canvas.create_text(200, 200, text="No seats found", 
                                           font=('Arial', 16), fill='red')
                return
            
            # Define layout parameters
            seat_size = 40
            gap = 5
            seats_per_row = 10
            start_x = 60
            start_y = 40
            
            # Group seats by row for proper layout
            rows = {}
            for seat in seats:
                row_num = seat.row_number
                if row_num not in rows:
                    rows[row_num] = []
                rows[row_num].append(seat)
            
            # Draw seats row by row
            for row_num in sorted(rows.keys()):
                row_seats = sorted(rows[row_num], key=lambda s: s.id)
                
                # Calculate row position
                y = start_y + (row_num - 1) * (seat_size + gap + 20)  # Extra space for row labels
                
                # Draw row label
                self.seat_canvas.create_text(start_x - 30, y + seat_size/2, 
                                           text=f"Row {row_num}", anchor='e', 
                                           font=('Arial', 10, 'bold'))
                
                # Draw seats in the row
                seats_in_current_row = 0
                for seat in row_seats:
                    x = start_x + (seats_in_current_row % seats_per_row) * (seat_size + gap)
                    
                    # Move to next row if too many seats
                    if seats_in_current_row > 0 and seats_in_current_row % seats_per_row == 0:
                        y += seat_size + gap
                    
                    # Determine seat color based on gender restriction and occupancy
                    color = self.get_seat_color(seat)
                    
                    # Draw seat rectangle
                    seat_rect = self.seat_canvas.create_rectangle(
                        x, y, x + seat_size, y + seat_size,
                        fill=color, outline='black', width=2
                    )
                    
                    # Draw seat number
                    self.seat_canvas.create_text(
                        x + seat_size/2, y + seat_size/2,
                        text=str(seat.id), font=('Arial', 9, 'bold')
                    )
                    
                    # Bind click event
                    self.seat_canvas.tag_bind(seat_rect, '<Button-1>', 
                                            lambda e, s=seat: self.select_seat(s))
                    
                    seats_in_current_row += 1
            
            # Update canvas scroll region
            self.seat_canvas.configure(scrollregion=self.seat_canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to draw seat layout: {str(e)}")
    
    def get_seat_color(self, seat):
        """Get color for seat based on gender restriction and occupancy"""
        # Check if seat is currently occupied
        occupied = self.is_seat_occupied(seat.id)
        
        if occupied:
            return 'lightcoral'  # Occupied
        elif seat.gender_restriction == 'Male':
            return 'lightblue'  # Male only
        elif seat.gender_restriction == 'Female':
            return 'lightpink'  # Female only
        else:
            return 'lightgreen'  # Any gender
    
    def is_seat_occupied(self, seat_id):
        """Check if seat is currently occupied"""
        try:
            from datetime import date
            
            # Get all subscriptions for this seat that are marked as active in the database
            db_manager = DatabaseManager()
            query = '''
                SELECT ss.*, s.name as student_name, s.is_active as student_active 
                FROM student_subscriptions ss
                JOIN students s ON ss.student_id = s.id
                WHERE ss.seat_id = ? AND ss.is_active = 1
            '''
            raw_subscriptions = db_manager.execute_query(query, (seat_id,))
            
            # Filter subscriptions to only include those that are truly current
            current_subscriptions = []
            today = date.today()
            
            for row in raw_subscriptions:
                end_date = date.fromisoformat(row['end_date']) if row['end_date'] else None
                student_active = bool(row['student_active'])
                
                # A subscription is truly active if:
                # 1. The subscription itself is marked active
                # 2. The student is still active
                # 3. The end date hasn't passed
                if end_date and end_date >= today and student_active:
                    current_subscriptions.append(row)
            
            return len(current_subscriptions) > 0
            
        except Exception as e:
            print(f"Error checking seat occupancy for seat {seat_id}: {str(e)}")
            return False
    
    def select_seat(self, seat):
        """Select a seat for editing"""
        try:
            # Make sure we're in edit mode
            self.editor_mode.set("edit")
            self.change_editor_mode()
            
            self.seat_id_var.set(str(seat.id))
            self.row_number_var.set(str(seat.row_number))
            self.gender_var.set(seat.gender_restriction)
            
            # Check if seat is occupied
            occupied = self.is_seat_occupied(seat.id)
            
            # Update status and button state based on occupancy
            if occupied:
                self.status_var.set("Currently Occupied - Cannot Edit")
                self.update_btn.config(state='disabled')
                self.delete_btn.config(state='disabled')
                self.gender_combo.config(state='disabled')
            else:
                self.status_var.set("Available - Can Edit")
                self.update_btn.config(state='normal')
                self.delete_btn.config(state='normal')
                self.gender_combo.config(state='readonly')
            
            # Load occupancy details
            self.load_seat_occupancy(seat.id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select seat: {str(e)}")
    
    def change_editor_mode(self):
        """Change editor mode between edit and add"""
        mode = self.editor_mode.get()
        
        if mode == "edit":
            # Edit existing seat mode
            self.seat_id_entry.config(state='readonly')
            self.row_entry.config(state='readonly')
            self.gender_combo.config(state='disabled')
            self.save_btn.config(state='disabled')
            self.update_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
            self.status_var.set("Select a seat to edit")
            self.clear_selection()
        
        elif mode == "add":
            # Add new seat mode
            self.seat_id_entry.config(state='normal')
            self.row_entry.config(state='normal')
            self.gender_combo.config(state='readonly')
            self.save_btn.config(state='normal')
            self.update_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
            self.status_var.set("Enter new seat details")
            self.clear_selection()
    
    def save_seat(self):
        """Save new seat or update existing seat"""
        mode = self.editor_mode.get()
        
        if mode == "add":
            return self.create_new_seat()
        elif mode == "edit":
            return self.update_seat_gender()
    
    def create_new_seat(self):
        """Create a new seat"""
        try:
            # Validate inputs
            seat_id_str = self.seat_id_var.get().strip()
            row_number_str = self.row_number_var.get().strip()
            gender = self.gender_var.get()
            
            if not seat_id_str:
                messagebox.showwarning("Warning", "Please enter a seat ID")
                return
            
            if not row_number_str:
                messagebox.showwarning("Warning", "Please enter a row number")
                return
            
            if not gender:
                messagebox.showwarning("Warning", "Please select a gender restriction")
                return
            
            try:
                seat_id = int(seat_id_str)
                row_number = int(row_number_str)
            except ValueError:
                messagebox.showerror("Error", "Seat ID and Row Number must be valid integers")
                return
            
            if seat_id <= 0 or row_number <= 0:
                messagebox.showerror("Error", "Seat ID and Row Number must be positive integers")
                return
            
            # Check if seat ID already exists
            existing_seat = Seat.get_by_id(seat_id)
            if existing_seat:
                messagebox.showerror("Error", f"Seat ID {seat_id} already exists")
                return
            
            # Confirm creation
            if not messagebox.askyesno("Confirmation", 
                f"Create new seat {seat_id} in row {row_number} with {gender} restriction?"):
                return
            
            # Create new seat
            new_seat = Seat(seat_id=seat_id, row_number=row_number, gender_restriction=gender)
            new_seat.save()
            
            messagebox.showinfo("Success", f"Seat {seat_id} created successfully!")
            
            # Refresh the display
            self.load_data()
            
            # Switch to edit mode and select the new seat
            self.editor_mode.set("edit")
            self.change_editor_mode()
            self.select_seat(new_seat)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create seat: {str(e)}")
    
    def load_seat_occupancy(self, seat_id):
        """Load occupancy details for selected seat"""
        # Clear existing items
        for item in self.occupancy_tree.get_children():
            self.occupancy_tree.delete(item)
        
        try:
            from datetime import date
            today = date.today()
            
            # Get all subscriptions for this seat (active and expired)
            subscriptions = Subscription.get_by_seat_id(seat_id, active_only=False)
            
            for sub in subscriptions:
                # Get related data
                from models.student import Student
                from models.timeslot import Timeslot
                
                student = Student.get_by_id(sub.student_id)
                timeslot = Timeslot.get_by_id(sub.timeslot_id)
                
                if student and timeslot:
                    # Determine detailed status
                    status_parts = []
                    
                    if not student.is_active:
                        status_parts.append("Student Inactive")
                    
                    if not sub.is_active:
                        status_parts.append("Sub Deactivated")
                    
                    if sub.is_expired():
                        status_parts.append("Expired")
                    
                    if not status_parts:
                        status_parts.append("Active")
                    
                    status = " | ".join(status_parts)
                    
                    # Color coding based on status
                    if "Active" in status and len(status_parts) == 1:
                        # True active subscription
                        tag = "active"
                    elif "Expired" in status or "Deactivated" in status:
                        # Problematic subscription
                        tag = "problem"
                    else:
                        tag = "inactive"
                    
                    item = self.occupancy_tree.insert('', 'end', values=(
                        timeslot.name,
                        student.name,
                        sub.start_date,
                        sub.end_date,
                        status
                    ), tags=(tag,))
            
            # Configure tag colors
            self.occupancy_tree.tag_configure("active", background="lightgreen")
            self.occupancy_tree.tag_configure("problem", background="lightcoral")
            self.occupancy_tree.tag_configure("inactive", background="lightgray")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load seat occupancy: {str(e)}")
    
    def update_seat_gender(self):
        """Update seat gender restriction"""
        seat_id = self.seat_id_var.get()
        if not seat_id:
            messagebox.showwarning("Warning", "Please select a seat to update")
            return
        
        try:
            seat = Seat.get_by_id(int(seat_id))
            if not seat:
                messagebox.showerror("Error", "Seat not found")
                return
            
            # Double-check if seat is occupied (safety check)
            if self.is_seat_occupied(seat.id):
                messagebox.showerror("Error", 
                    f"Cannot modify seat {seat.id} - it is currently occupied by active subscriptions.\n"
                    f"Please wait for all subscriptions to expire or deactivate them first.")
                return
            
            new_gender = self.gender_var.get()
            if not new_gender:
                messagebox.showwarning("Warning", "Please select a gender restriction")
                return
            
            # Confirm the change
            if not messagebox.askyesno("Confirmation", 
                f"Change seat {seat.id} gender restriction from '{seat.gender_restriction}' to '{new_gender}'?"):
                return
            
            # Update seat gender
            seat.gender_restriction = new_gender
            seat.save()
            
            messagebox.showinfo("Success", f"Seat {seat.id} gender restriction updated to {new_gender}")
            
            # Refresh the display
            self.draw_seat_layout()
            self.select_seat(seat)  # Reselect the seat to refresh info
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update seat: {str(e)}")
    
    def view_seat_occupancy(self):
        """View detailed seat occupancy"""
        seat_id = self.seat_id_var.get()
        if not seat_id:
            messagebox.showwarning("Warning", "Please select a seat to view occupancy")
            return
        
        # The occupancy is already displayed in the tree, just show a summary
        occupancy_count = len(self.occupancy_tree.get_children())
        if occupancy_count > 0:
            messagebox.showinfo("Seat Occupancy", 
                f"Seat {seat_id} has {occupancy_count} subscription(s).\n"
                f"Details are shown in the occupancy table below.")
        else:
            messagebox.showinfo("Seat Occupancy", f"Seat {seat_id} has no subscriptions.")
    
    def clear_selection(self):
        """Clear seat selection"""
        self.seat_id_var.set("")
        self.row_number_var.set("")
        self.gender_var.set("")
        
        mode = self.editor_mode.get()
        if mode == "edit":
            self.status_var.set("Select a seat to edit")
            self.update_btn.config(state='disabled')
            self.save_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
            self.gender_combo.config(state='disabled')
        elif mode == "add":
            self.status_var.set("Enter new seat details")
            self.update_btn.config(state='disabled')
            self.save_btn.config(state='normal')
            self.delete_btn.config(state='disabled')
            self.gender_combo.config(state='readonly')
        
        # Clear occupancy tree
        for item in self.occupancy_tree.get_children():
            self.occupancy_tree.delete(item)
    
    def reset_all_seats(self):
        """Reset all seats to default configuration"""
        if not messagebox.askyesno("Confirmation", 
            "This will reset all seats to their default gender configuration:\n"
            "• Row 1 and 10: Seats 1-9 and 72-82 for Girls\n"
            "• Row 2-9: Seats 10-71 for Boys\n\n"
            "Occupied seats will NOT be changed.\n"
            "Are you sure you want to continue?"):
            return
        
        try:
            seats = Seat.get_all()
            updated_count = 0
            skipped_count = 0
            
            for seat in seats:
                # Skip occupied seats
                if self.is_seat_occupied(seat.id):
                    skipped_count += 1
                    continue
                
                # Apply default configuration
                if seat.id <= 9 or (72 <= seat.id <= 82):
                    # Girls seats (Row 1 and 10)
                    if seat.gender_restriction != 'Female':
                        seat.gender_restriction = 'Female'
                        seat.save()
                        updated_count += 1
                elif 10 <= seat.id <= 71:
                    # Boys seats (Row 2-9)
                    if seat.gender_restriction != 'Male':
                        seat.gender_restriction = 'Male'
                        seat.save()
                        updated_count += 1
            
            message = f"Reset completed!\n• {updated_count} seats updated\n• {skipped_count} occupied seats skipped"
            messagebox.showinfo("Reset Complete", message)
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset seats: {str(e)}")
    
    def delete_seat(self):
        """Delete the selected seat"""
        seat_id = self.seat_id_var.get()
        if not seat_id:
            messagebox.showwarning("Warning", "Please select a seat to delete")
            return
        
        try:
            seat = Seat.get_by_id(int(seat_id))
            if not seat:
                messagebox.showerror("Error", "Seat not found")
                return
            
            # Double-check if seat is occupied (safety check)
            if self.is_seat_occupied(seat.id):
                messagebox.showerror("Error", 
                    f"Cannot delete seat {seat.id} - it is currently occupied by active subscriptions.\n"
                    f"Please wait for all subscriptions to expire or deactivate them first.")
                return
            
            # Confirm deletion
            if not messagebox.askyesno("Confirmation", 
                f"Are you sure you want to delete seat {seat.id}?\n\n"
                f"This action cannot be undone!"):
                return
            
            # Delete seat from database
            query = "UPDATE seats SET is_active = 0 WHERE id = ?"
            seat.db_manager.execute_query(query, (seat.id,))
            
            messagebox.showinfo("Success", f"Seat {seat.id} has been deleted successfully!")
            
            # Refresh the display and clear selection
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete seat: {str(e)}")
    
    def refresh(self):
        """Refresh the seat management interface"""
        self.load_data()
    
    def cleanup_expired_subscriptions(self):
        """Clean up expired subscriptions that might be causing false 'occupied' status"""
        try:
            from datetime import date
            
            db_manager = DatabaseManager()
            
            # Find subscriptions that are marked as active but have expired
            query = '''
                SELECT ss.id, ss.seat_id, ss.end_date, s.name as student_name
                FROM student_subscriptions ss
                JOIN students s ON ss.student_id = s.id
                WHERE ss.is_active = 1 AND ss.end_date < date('now')
            '''
            expired_active = db_manager.execute_query(query)
            
            if expired_active:
                expired_count = len(expired_active)
                
                response = messagebox.askyesno("Cleanup Expired Subscriptions", 
                    f"Found {expired_count} subscriptions that are marked active but have expired.\n\n"
                    f"This might be causing seats to show as occupied when they shouldn't be.\n\n"
                    f"Would you like to mark these expired subscriptions as inactive?")
                
                if response:
                    # Mark expired subscriptions as inactive
                    cleanup_query = "UPDATE student_subscriptions SET is_active = 0 WHERE is_active = 1 AND end_date < date('now')"
                    db_manager.execute_query(cleanup_query)
                    
                    messagebox.showinfo("Success", 
                        f"Marked {expired_count} expired subscriptions as inactive.\n\n"
                        f"Seats should now show correct availability status.")
                    
                    # Refresh the display
                    self.load_data()
            else:
                messagebox.showinfo("No Issues Found", 
                    "No expired subscriptions found that are still marked as active.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cleanup expired subscriptions: {str(e)}")
    
    def diagnose_seat_occupancy(self, seat_id=None):
        """Diagnose seat occupancy issues for debugging"""
        if not seat_id:
            seat_id = self.seat_id_var.get()
            
        if not seat_id:
            messagebox.showwarning("Warning", "Please select a seat to diagnose")
            return
            
        try:
            from datetime import date
            
            db_manager = DatabaseManager()
            
            # Get detailed information about this seat's subscriptions
            query = '''
                SELECT ss.*, s.name as student_name, s.is_active as student_active, t.name as timeslot_name
                FROM student_subscriptions ss
                JOIN students s ON ss.student_id = s.id
                JOIN timeslots t ON ss.timeslot_id = t.id
                WHERE ss.seat_id = ?
                ORDER BY ss.end_date DESC
            '''
            all_subscriptions = db_manager.execute_query(query, (seat_id,))
            
            if not all_subscriptions:
                messagebox.showinfo("Seat Diagnosis", f"Seat {seat_id}: No subscriptions found.")
                return
            
            # Analyze each subscription
            today = date.today()
            diagnosis_text = f"Seat {seat_id} Diagnosis:\n\n"
            
            active_count = 0
            for sub in all_subscriptions:
                end_date = date.fromisoformat(sub['end_date']) if sub['end_date'] else None
                is_active = bool(sub['is_active'])
                student_active = bool(sub['student_active'])
                
                status_parts = []
                if is_active:
                    status_parts.append("DB Active")
                else:
                    status_parts.append("DB Inactive")
                    
                if end_date:
                    if end_date >= today:
                        status_parts.append("Not Expired")
                        if is_active and student_active:
                            active_count += 1
                    else:
                        status_parts.append("EXPIRED")
                        
                if student_active:
                    status_parts.append("Student Active")
                else:
                    status_parts.append("Student Inactive")
                
                diagnosis_text += f"• {sub['student_name']} ({sub['timeslot_name']})\n"
                diagnosis_text += f"  End Date: {sub['end_date']} | Status: {' | '.join(status_parts)}\n\n"
            
            diagnosis_text += f"Current Status: {'OCCUPIED' if active_count > 0 else 'AVAILABLE'}\n"
            diagnosis_text += f"Active Subscriptions: {active_count}"
            
            # Show diagnosis in a scrollable dialog
            diagnosis_window = tk.Toplevel()
            diagnosis_window.title(f"Seat {seat_id} Diagnosis")
            diagnosis_window.geometry("600x400")
            
            text_frame = ttk.Frame(diagnosis_window)
            text_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap='word', font=('Courier', 10))
            scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            text_widget.insert('1.0', diagnosis_text)
            text_widget.config(state='disabled')
            
            # Add cleanup button if needed
            if any(sub['is_active'] and date.fromisoformat(sub['end_date']) < today for sub in all_subscriptions):
                ttk.Button(diagnosis_window, text="Cleanup Expired Subscriptions", 
                          command=lambda: [diagnosis_window.destroy(), self.cleanup_expired_subscriptions()]).pack(pady=5)
            
            ttk.Button(diagnosis_window, text="Close", command=diagnosis_window.destroy).pack(pady=5)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to diagnose seat: {str(e)}")
