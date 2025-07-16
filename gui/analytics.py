"""
Analytics interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.database_manager import DatabaseOperations
from utils.excel_exporter import ExcelExporter


class AnalyticsFrame(ttk.Frame):
    """Analytics interface"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.db_ops = DatabaseOperations()
        self.exporter = ExcelExporter()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup user interface"""
        # Create notebook for different analytics views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Overview tab
        self.create_overview_tab()
        
        # Charts tab
        self.create_charts_tab()
        
        # Reports tab
        self.create_reports_tab()
    
    def create_overview_tab(self):
        """Create overview analytics tab"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(overview_frame, text="Current Statistics", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        # Create statistics display
        self.create_statistics_display(stats_frame)
        
        # Seat occupancy frame
        occupancy_frame = ttk.LabelFrame(overview_frame, text="Seat Occupancy", padding=10)
        occupancy_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create seat occupancy view
        self.create_seat_occupancy_view(occupancy_frame)
    
    def create_statistics_display(self, parent):
        """Create statistics display"""
        # Create grid of statistics
        stats_grid = ttk.Frame(parent)
        stats_grid.pack(fill='x')
        
        # Statistics variables
        self.total_students_var = tk.StringVar(value="0")
        self.total_seats_var = tk.StringVar(value="0")
        self.occupied_seats_var = tk.StringVar(value="0")
        self.unoccupied_seats_var = tk.StringVar(value="0")
        self.assigned_students_var = tk.StringVar(value="0")
        self.unassigned_students_var = tk.StringVar(value="0")
        self.total_books_var = tk.StringVar(value="0")
        self.active_borrowings_var = tk.StringVar(value="0")
        
        # Create stat boxes
        row = 0
        col = 0
        
        stats = [
            ("Total Students", self.total_students_var, "#FF6B6B"),
            ("Total Seats", self.total_seats_var, "#4ECDC4"),
            ("Occupied Seats", self.occupied_seats_var, "#45B7D1"),
            ("Unoccupied Seats", self.unoccupied_seats_var, "#96CEB4"),
            ("Assigned Students", self.assigned_students_var, "#FECA57"),
            ("Unassigned Students", self.unassigned_students_var, "#FF9FF3"),
            ("Total Books", self.total_books_var, "#54A0FF"),
            ("Active Borrowings", self.active_borrowings_var, "#5F27CD")
        ]
        
        for stat_name, stat_var, color in stats:
            stat_frame = tk.Frame(stats_grid, bg=color, relief='raised', bd=2)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            
            # Title
            title_label = tk.Label(stat_frame, text=stat_name, bg=color, fg='white', 
                                 font=('Arial', 10, 'bold'))
            title_label.pack(pady=5)
            
            # Value
            value_label = tk.Label(stat_frame, textvariable=stat_var, bg=color, fg='white',
                                 font=('Arial', 16, 'bold'))
            value_label.pack(pady=(0, 10))
            
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        # Configure column weights
        for i in range(4):
            stats_grid.columnconfigure(i, weight=1)
        
        # Refresh button
        ttk.Button(parent, text="Refresh Statistics", command=self.load_statistics).pack(pady=10)
    
    def create_seat_occupancy_view(self, parent):
        """Create seat occupancy visualization"""
        # Canvas for seat map
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill='both', expand=True)
        
        self.seat_canvas = tk.Canvas(canvas_frame, bg='white', height=400)
        self.seat_canvas.pack(fill='both', expand=True)
        
        # Legend
        legend_frame = ttk.Frame(parent)
        legend_frame.pack(fill='x', pady=5)
        
        tk.Label(legend_frame, text="Legend:", font=('Arial', 10, 'bold')).pack(side='left')
        
        # Available seat
        available_frame = tk.Frame(legend_frame)
        available_frame.pack(side='left', padx=10)
        tk.Canvas(available_frame, width=20, height=20, bg='lightgreen').pack(side='left')
        tk.Label(available_frame, text="Available").pack(side='left', padx=5)
        
        # Occupied seat
        occupied_frame = tk.Frame(legend_frame)
        occupied_frame.pack(side='left', padx=10)
        tk.Canvas(occupied_frame, width=20, height=20, bg='lightcoral').pack(side='left')
        tk.Label(occupied_frame, text="Occupied").pack(side='left', padx=5)
        
        # Girls only
        girls_frame = tk.Frame(legend_frame)
        girls_frame.pack(side='left', padx=10)
        tk.Canvas(girls_frame, width=20, height=20, bg='lightpink').pack(side='left')
        tk.Label(girls_frame, text="Girls Only").pack(side='left', padx=5)
        
        # Boys only
        boys_frame = tk.Frame(legend_frame)
        boys_frame.pack(side='left', padx=10)
        tk.Canvas(boys_frame, width=20, height=20, bg='lightblue').pack(side='left')
        tk.Label(boys_frame, text="Boys Only").pack(side='left', padx=5)
    
    def create_charts_tab(self):
        """Create charts tab"""
        charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(charts_frame, text="Charts")
        
        # Chart selection
        chart_control_frame = ttk.Frame(charts_frame)
        chart_control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(chart_control_frame, text="Chart Type:").pack(side='left')
        self.chart_type_var = tk.StringVar(value="Occupancy Rate")
        chart_combo = ttk.Combobox(chart_control_frame, textvariable=self.chart_type_var,
                                 values=["Occupancy Rate", "Revenue by Timeslot", "Student Gender Distribution", "Book Categories"],
                                 state='readonly')
        chart_combo.pack(side='left', padx=5)
        ttk.Button(chart_control_frame, text="Generate Chart", command=self.generate_chart).pack(side='left', padx=5)
        
        # Chart display frame
        self.chart_frame = ttk.Frame(charts_frame)
        self.chart_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_reports_tab(self):
        """Create reports tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        # Export options
        export_frame = ttk.LabelFrame(reports_frame, text="Export Options", padding=10)
        export_frame.pack(fill='x', padx=10, pady=10)
        
        # Export all data
        ttk.Button(export_frame, text="Export All Data to Excel", 
                  command=self.export_all_data).pack(side='left', padx=5)
        
        # Export students only
        ttk.Button(export_frame, text="Export Students Only", 
                  command=self.export_students).pack(side='left', padx=5)
        
        # Monthly report frame
        monthly_frame = ttk.LabelFrame(reports_frame, text="Monthly Report", padding=10)
        monthly_frame.pack(fill='x', padx=10, pady=10)
        
        # Month/Year selection
        selection_frame = ttk.Frame(monthly_frame)
        selection_frame.pack(fill='x')
        
        ttk.Label(selection_frame, text="Year:").pack(side='left')
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_spin = tk.Spinbox(selection_frame, from_=2020, to=2030, textvariable=self.year_var, width=10)
        year_spin.pack(side='left', padx=5)
        
        ttk.Label(selection_frame, text="Month:").pack(side='left', padx=(20, 0))
        self.month_var = tk.StringVar(value=str(datetime.now().month))
        month_spin = tk.Spinbox(selection_frame, from_=1, to=12, textvariable=self.month_var, width=10)
        month_spin.pack(side='left', padx=5)
        
        ttk.Button(selection_frame, text="Generate Monthly Report", 
                  command=self.generate_monthly_report).pack(side='left', padx=20)
        
        # Expiring subscriptions
        expiring_frame = ttk.LabelFrame(reports_frame, text="Expiring Subscriptions", padding=10)
        expiring_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Days selection
        days_frame = ttk.Frame(expiring_frame)
        days_frame.pack(fill='x')
        
        ttk.Label(days_frame, text="Show subscriptions expiring in next:").pack(side='left')
        self.expiry_days_var = tk.StringVar(value="7")
        days_spin = tk.Spinbox(days_frame, from_=1, to=30, textvariable=self.expiry_days_var, width=10)
        days_spin.pack(side='left', padx=5)
        ttk.Label(days_frame, text="days").pack(side='left')
        ttk.Button(days_frame, text="Show Expiring", command=self.show_expiring_subscriptions).pack(side='left', padx=20)
        
        # Expiring subscriptions tree
        expiring_columns = ('Student', 'Mobile', 'Seat', 'Timeslot', 'Expiry Date', 'Days Left')
        self.expiring_tree = ttk.Treeview(expiring_frame, columns=expiring_columns, show='headings', height=10)
        
        for col in expiring_columns:
            self.expiring_tree.heading(col, text=col)
            self.expiring_tree.column(col, width=100)
        
        # Scrollbar for expiring tree
        expiring_scrollbar = ttk.Scrollbar(expiring_frame, orient='vertical', command=self.expiring_tree.yview)
        self.expiring_tree.configure(yscrollcommand=expiring_scrollbar.set)
        
        self.expiring_tree.pack(side='left', fill='both', expand=True)
        expiring_scrollbar.pack(side='right', fill='y')
    
    def load_data(self):
        """Load all analytics data"""
        self.load_statistics()
        self.draw_seat_map()
        self.show_expiring_subscriptions()
    
    def load_statistics(self):
        """Load current statistics"""
        try:
            analytics = self.db_ops.get_analytics_data()
            
            self.total_students_var.set(str(analytics['total_students']))
            self.total_seats_var.set(str(analytics['total_seats']))
            self.occupied_seats_var.set(str(analytics['occupied_seats']))
            self.unoccupied_seats_var.set(str(analytics['unoccupied_seats']))
            self.assigned_students_var.set(str(analytics['assigned_students']))
            self.unassigned_students_var.set(str(analytics['unassigned_students']))
            self.total_books_var.set(str(analytics['total_books']))
            self.active_borrowings_var.set(str(analytics['active_borrowings']))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {str(e)}")
    
    def draw_seat_map(self):
        """Draw seat occupancy map"""
        try:
            self.seat_canvas.delete("all")
            
            # Get seat occupancy data
            from models.seat import Seat
            seats = Seat.get_all()
            
            # Draw seats in a grid layout (10 rows, varying columns)
            seat_size = 30
            gap = 5
            start_x = 20
            start_y = 20
            
            for seat in seats:
                # Calculate position based on seat number
                if seat.id <= 9:
                    # Row 1: seats 1-9
                    row = 0
                    col = seat.id - 1
                elif seat.id <= 71:
                    # Rows 2-9: seats 10-71
                    row = ((seat.id - 10) // 8) + 1
                    col = (seat.id - 10) % 8
                else:
                    # Row 10: seats 72-82
                    row = 9
                    col = seat.id - 72
                
                x = start_x + col * (seat_size + gap)
                y = start_y + row * (seat_size + gap)
                
                # Determine seat color
                occupants = seat.get_current_occupants()
                if occupants:
                    color = 'lightcoral'  # Occupied
                elif seat.gender_restriction == 'Female':
                    color = 'lightpink'  # Girls only
                elif seat.gender_restriction == 'Male':
                    color = 'lightblue'  # Boys only
                else:
                    color = 'lightgreen'  # Available
                
                # Draw seat
                self.seat_canvas.create_rectangle(x, y, x + seat_size, y + seat_size,
                                                fill=color, outline='black')
                self.seat_canvas.create_text(x + seat_size/2, y + seat_size/2,
                                           text=str(seat.id), font=('Arial', 8))
            
        except Exception as e:
            print(f"Error drawing seat map: {e}")
    
    def generate_chart(self):
        """Generate selected chart"""
        try:
            chart_type = self.chart_type_var.get()
            
            # Clear existing chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if chart_type == "Occupancy Rate":
                self.create_occupancy_chart(ax)
            elif chart_type == "Revenue by Timeslot":
                self.create_revenue_chart(ax)
            elif chart_type == "Student Gender Distribution":
                self.create_gender_chart(ax)
            elif chart_type == "Book Categories":
                self.create_book_categories_chart(ax)
            
            # Embed chart in tkinter
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate chart: {str(e)}")
    
    def create_occupancy_chart(self, ax):
        """Create occupancy rate chart"""
        from models.timeslot import Timeslot
        
        timeslots = Timeslot.get_all()
        names = [ts.name for ts in timeslots]
        rates = [ts.get_occupancy_rate() for ts in timeslots]
        
        ax.bar(names, rates, color='skyblue')
        ax.set_title('Seat Occupancy Rate by Timeslot')
        ax.set_ylabel('Occupancy Rate (%)')
        ax.set_xlabel('Timeslot')
        plt.xticks(rotation=45)
        plt.tight_layout()
    
    def create_revenue_chart(self, ax):
        """Create revenue by timeslot chart"""
        # This would require database queries to get revenue data
        # For now, create a placeholder
        ax.text(0.5, 0.5, 'Revenue Chart\n(To be implemented)', 
               ha='center', va='center', transform=ax.transAxes, fontsize=16)
        ax.set_title('Revenue by Timeslot')
    
    def create_gender_chart(self, ax):
        """Create gender distribution pie chart"""
        from models.student import Student
        
        students = Student.get_all()
        male_count = len([s for s in students if s.gender == 'Male'])
        female_count = len([s for s in students if s.gender == 'Female'])
        
        if male_count > 0 or female_count > 0:
            ax.pie([male_count, female_count], labels=['Male', 'Female'], 
                  colors=['lightblue', 'lightpink'], autopct='%1.1f%%')
            ax.set_title('Student Gender Distribution')
        else:
            ax.text(0.5, 0.5, 'No student data available', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def create_book_categories_chart(self, ax):
        """Create book categories chart"""
        from models.book import Book
        from collections import Counter
        
        books = Book.get_all()
        categories = [book.category or 'Uncategorized' for book in books]
        category_counts = Counter(categories)
        
        if category_counts:
            categories = list(category_counts.keys())
            counts = list(category_counts.values())
            
            ax.bar(categories, counts, color='lightgreen')
            ax.set_title('Books by Category')
            ax.set_ylabel('Number of Books')
            ax.set_xlabel('Category')
            plt.xticks(rotation=45)
            plt.tight_layout()
        else:
            ax.text(0.5, 0.5, 'No book data available', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def export_all_data(self):
        """Export all data to Excel"""
        try:
            success, filepath = self.exporter.export_all_data()
            if success:
                messagebox.showinfo("Export Successful", f"Data exported to:\n{filepath}")
            else:
                messagebox.showerror("Export Failed", filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_students(self):
        """Export students data only"""
        try:
            success, filepath = self.exporter.export_students_data()
            if success:
                messagebox.showinfo("Export Successful", f"Students data exported to:\n{filepath}")
            else:
                messagebox.showerror("Export Failed", filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def generate_monthly_report(self):
        """Generate monthly financial report"""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            
            success, filepath = self.exporter.export_financial_report(year, month)
            if success:
                messagebox.showinfo("Report Generated", f"Monthly report generated:\n{filepath}")
            else:
                messagebox.showerror("Report Failed", filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def show_expiring_subscriptions(self):
        """Show expiring subscriptions"""
        try:
            # Clear existing items
            for item in self.expiring_tree.get_children():
                self.expiring_tree.delete(item)
            
            days = int(self.expiry_days_var.get())
            from models.subscription import Subscription
            
            expiring_subs = Subscription.get_expiring_soon(days)
            
            for sub in expiring_subs:
                # Calculate days left
                from datetime import datetime
                end_date = datetime.strptime(sub['end_date'], '%Y-%m-%d').date()
                days_left = (end_date - date.today()).days
                
                self.expiring_tree.insert('', 'end', values=(
                    sub['student_name'],
                    sub['mobile_number'],
                    f"Seat {sub['seat_number']}",
                    sub['timeslot_name'],
                    sub['end_date'],
                    days_left
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expiring subscriptions: {str(e)}")
    
    def refresh(self):
        """Refresh the interface"""
        self.load_data()
