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
from config.database import DatabaseManager


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
        
        # Available Seats tab
        self.create_available_seats_tab()
    
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
        self.monthly_revenue_var = tk.StringVar(value="Rs. 0")
        
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
            ("Active Borrowings", self.active_borrowings_var, "#5F27CD"),
            ("Monthly Revenue", self.monthly_revenue_var, "#2ECC71")
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
            if col >= 3:  # Changed from 4 to 3 for better layout with 9 items
                col = 0
                row += 1
        
        # Configure column weights
        for i in range(3):  # Changed from 4 to 3
            stats_grid.columnconfigure(i, weight=1)
        
        # Refresh button
        ttk.Button(parent, text="Refresh Statistics", command=self.load_statistics).pack(pady=10)
    
    def create_seat_occupancy_view(self, parent):
        """Create seat occupancy visualization"""
        # Controls frame
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill='x', pady=5)
        
        ttk.Button(controls_frame, text="Refresh Seat Map", 
                  command=self.refresh_seat_map).pack(side='left', padx=5)
        
        ttk.Label(controls_frame, text="Real-time seat occupancy status", 
                 font=('Arial', 9, 'italic')).pack(side='left', padx=20)
        
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
        
        # Date selection for revenue chart
        ttk.Label(chart_control_frame, text="Month/Year:").pack(side='left', padx=(20, 5))
        self.chart_year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(chart_control_frame, textvariable=self.chart_year_var,
                                values=[str(y) for y in range(2020, 2030)], width=8, state='readonly')
        year_combo.pack(side='left', padx=2)
        
        self.chart_month_var = tk.StringVar(value=str(datetime.now().month))
        month_combo = ttk.Combobox(chart_control_frame, textvariable=self.chart_month_var,
                                 values=[str(m) for m in range(1, 13)], width=5, state='readonly')
        month_combo.pack(side='left', padx=2)
        
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
    
    def create_available_seats_tab(self):
        """Create available seats by timeslots tab"""
        seats_frame = ttk.Frame(self.notebook)
        self.notebook.add(seats_frame, text="Available Seats")
        
        # Controls frame
        controls_frame = ttk.LabelFrame(seats_frame, text="View Options", padding=10)
        controls_frame.pack(fill='x', padx=10, pady=10)
        
        # Timeslot selection
        ttk.Label(controls_frame, text="Select Timeslot:").pack(side='left')
        self.timeslot_var = tk.StringVar()
        self.timeslot_combo = ttk.Combobox(controls_frame, textvariable=self.timeslot_var, 
                                          state='readonly', width=30)
        self.timeslot_combo.pack(side='left', padx=10)
        
        ttk.Button(controls_frame, text="Show Available Seats", 
                  command=self.show_available_seats).pack(side='left', padx=10)
        
        ttk.Button(controls_frame, text="Show All Timeslots", 
                  command=self.show_all_timeslots_availability).pack(side='left', padx=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(seats_frame, text="Available Seats", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Available seats tree
        seats_columns = ('Seat ID', 'Row', 'Gender Restriction', 'Status')
        self.available_seats_tree = ttk.Treeview(results_frame, columns=seats_columns, show='headings', height=15)
        
        for col in seats_columns:
            self.available_seats_tree.heading(col, text=col)
            self.available_seats_tree.column(col, width=120)
        
        # Scrollbar for seats tree
        seats_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.available_seats_tree.yview)
        self.available_seats_tree.configure(yscrollcommand=seats_scrollbar.set)
        
        self.available_seats_tree.pack(side='left', fill='both', expand=True)
        seats_scrollbar.pack(side='right', fill='y')
        
        # Summary frame
        summary_frame = ttk.LabelFrame(seats_frame, text="Summary", padding=10)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        self.summary_var = tk.StringVar(value="Select a timeslot to view available seats")
        ttk.Label(summary_frame, textvariable=self.summary_var, font=('Arial', 10)).pack()
        
        # Load timeslots
        self.load_timeslots_for_availability()
    
    def load_data(self):
        """Load all analytics data"""
        self.load_statistics()
        self.draw_seat_map()
        self.show_expiring_subscriptions()
        self.load_timeslots_for_availability()
    
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
            
            # Get current month's revenue
            monthly_revenue = self.db_ops.get_current_month_revenue()
            self.monthly_revenue_var.set(f"Rs. {monthly_revenue:,.0f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {str(e)}")
    
    def draw_seat_map(self):
        """Draw seat occupancy map"""
        try:
            self.seat_canvas.delete("all")
            
            # Get seat occupancy data
            from models.seat import Seat
            seats = Seat.get_all()
            
            # Debug: Count occupied seats
            occupied_count = 0
            
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
                    occupied_count += 1
                    # Debug: Print occupied seats
                    if seat.id in [2, 3]:  # Focus on problematic seats
                        print(f"DEBUG: Seat {seat.id} shows {len(occupants)} occupants in analytics")
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
            
            print(f"DEBUG: Analytics seat map drawn with {occupied_count} occupied seats")
            
        except Exception as e:
            print(f"Error drawing seat map: {e}")
            import traceback
            traceback.print_exc()
    
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
        try:
            # Get selected year and month from the controls
            selected_year = int(self.chart_year_var.get()) if hasattr(self, 'chart_year_var') else datetime.now().year
            selected_month = int(self.chart_month_var.get()) if hasattr(self, 'chart_month_var') else datetime.now().month
            
            # Get revenue data for selected month
            revenue_data = self.db_ops.get_revenue_by_timeslot(selected_year, selected_month)
            
            if not revenue_data:
                month_name = datetime(selected_year, selected_month, 1).strftime("%B %Y")
                ax.text(0.5, 0.5, f'No revenue data available for {month_name}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_title(f'Revenue by Timeslot - {month_name}')
                return
            
            # Extract data for plotting
            timeslot_names = []
            revenues = []
            colors = plt.cm.Set3(range(len(revenue_data)))  # Use colormap for variety
            
            for item in revenue_data:
                # Create readable timeslot label
                timeslot_label = f"{item['timeslot_name']}\n({item['start_time']}-{item['end_time']})"
                timeslot_names.append(timeslot_label)
                revenues.append(float(item['revenue']))
            
            # Create bar chart
            bars = ax.bar(timeslot_names, revenues, color=colors)
            
            # Customize chart
            month_name = datetime(selected_year, selected_month, 1).strftime("%B %Y")
            ax.set_title(f'Revenue by Timeslot - {month_name}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Timeslots', fontsize=12)
            ax.set_ylabel('Revenue (Rs.)', fontsize=12)
            
            # Format y-axis to show rupee values
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Rs. {x:,.0f}'))
            
            # Add value labels on bars
            for bar, revenue in zip(bars, revenues):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(revenues)*0.01,
                       f'Rs. {revenue:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Add total revenue annotation
            total_revenue = sum(revenues)
            ax.text(0.02, 0.98, f'Total: Rs. {total_revenue:,.0f}', 
                   transform=ax.transAxes, fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                   verticalalignment='top')
            
            # Adjust layout to prevent label cutoff
            plt.tight_layout()
            
        except Exception as e:
            ax.text(0.5, 0.5, f'Error loading revenue data:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('Revenue by Timeslot - Error')
    
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
        self.load_timeslots_for_availability()
    
    def refresh_seat_map(self):
        """Refresh only the seat map visualization"""
        try:
            self.draw_seat_map()
            print("Seat map refreshed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh seat map: {str(e)}")
    
    def load_timeslots_for_availability(self):
        """Load timeslots for the available seats view"""
        try:
            from models.timeslot import Timeslot
            timeslots = Timeslot.get_all()
            
            # Populate timeslot combo
            timeslot_names = [f"{ts.name} ({ts.start_time}-{ts.end_time})" for ts in timeslots]
            self.timeslot_combo['values'] = timeslot_names
            
            # Store timeslots for reference
            self.timeslots_data = {f"{ts.name} ({ts.start_time}-{ts.end_time})": ts for ts in timeslots}
            
        except Exception as e:
            print(f"Error loading timeslots: {str(e)}")
    
    def show_available_seats(self):
        """Show available seats for selected timeslot"""
        try:
            # Clear existing items
            for item in self.available_seats_tree.get_children():
                self.available_seats_tree.delete(item)
            
            selected_timeslot_name = self.timeslot_var.get()
            if not selected_timeslot_name:
                messagebox.showwarning("Warning", "Please select a timeslot")
                return
            
            # Get selected timeslot
            timeslot = self.timeslots_data.get(selected_timeslot_name)
            if not timeslot:
                messagebox.showerror("Error", "Invalid timeslot selected")
                return
            
            # Get all seats
            from models.seat import Seat
            all_seats = Seat.get_all()
            
            available_count = 0
            occupied_count = 0
            male_available = 0
            female_available = 0
            any_available = 0
            
            for seat in all_seats:
                # Check if seat has any conflicting subscriptions for this timeslot
                is_available = self.is_seat_available_for_timeslot(seat, timeslot)
                
                if is_available:
                    status = "Available"
                    available_count += 1
                    
                    if seat.gender_restriction == 'Male':
                        male_available += 1
                    elif seat.gender_restriction == 'Female':
                        female_available += 1
                    else:
                        any_available += 1
                        
                    # Insert available seat
                    self.available_seats_tree.insert('', 'end', values=(
                        seat.id,
                        seat.row_number,
                        seat.gender_restriction,
                        status
                    ), tags=('available',))
                else:
                    occupied_count += 1
            
            # Configure tag colors
            self.available_seats_tree.tag_configure('available', background='lightgreen')
            
            # Update summary
            summary_text = (f"Timeslot: {selected_timeslot_name}\n"
                          f"Available Seats: {available_count} | Occupied: {occupied_count}\n"
                          f"Available by Gender - Male: {male_available}, Female: {female_available}, Any: {any_available}")
            self.summary_var.set(summary_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load available seats: {str(e)}")
    
    def show_all_timeslots_availability(self):
        """Show availability summary for all timeslots"""
        try:
            # Clear existing items
            for item in self.available_seats_tree.get_children():
                self.available_seats_tree.delete(item)
            
            from models.timeslot import Timeslot
            from models.seat import Seat
            
            timeslots = Timeslot.get_all()
            all_seats = Seat.get_all()
            total_seats = len(all_seats)
            
            # Change column headers for summary view
            self.available_seats_tree.heading('Seat ID', text='Timeslot')
            self.available_seats_tree.heading('Row', text='Time')
            self.available_seats_tree.heading('Gender Restriction', text='Available Seats')
            self.available_seats_tree.heading('Status', text='Occupancy Rate')
            
            total_available = 0
            
            for timeslot in timeslots:
                available_count = 0
                
                # Count available seats for this timeslot
                for seat in all_seats:
                    if self.is_seat_available_for_timeslot(seat, timeslot):
                        available_count += 1
                
                occupied_count = total_seats - available_count
                occupancy_rate = (occupied_count / total_seats) * 100 if total_seats > 0 else 0
                
                # Insert timeslot summary
                self.available_seats_tree.insert('', 'end', values=(
                    timeslot.name,
                    f"{timeslot.start_time}-{timeslot.end_time}",
                    f"{available_count}/{total_seats}",
                    f"{occupancy_rate:.1f}%"
                ), tags=('summary',))
                
                total_available += available_count
            
            # Configure tag colors
            self.available_seats_tree.tag_configure('summary', background='lightblue')
            
            # Update summary
            avg_availability = (total_available / (len(timeslots) * total_seats)) * 100 if timeslots and total_seats > 0 else 0
            summary_text = (f"All Timeslots Summary\n"
                          f"Total Seats: {total_seats} | Average Availability: {avg_availability:.1f}%\n"
                          f"Click 'Show Available Seats' after selecting a specific timeslot for detailed view")
            self.summary_var.set(summary_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load timeslots summary: {str(e)}")
    
    def is_seat_available_for_timeslot(self, seat, timeslot):
        """Check if a seat is available for a specific timeslot"""
        try:
            from datetime import date, timedelta
            
            # Check current date availability (we'll check for next 30 days as default)
            start_date = date.today()
            end_date = start_date + timedelta(days=30)
            
            # Get existing subscriptions for this seat that might conflict
            db_manager = DatabaseManager()
            query = '''
                SELECT ss.*, t.start_time, t.end_time
                FROM student_subscriptions ss
                JOIN students s ON ss.student_id = s.id
                JOIN timeslots t ON ss.timeslot_id = t.id
                WHERE ss.seat_id = ? AND ss.is_active = 1 AND s.is_active = 1
                AND ss.end_date >= date('now')
            '''
            existing_subs = db_manager.execute_query(query, (seat.id,))
            
            # Check for time conflicts with the target timeslot
            for sub in existing_subs:
                if timeslot.check_overlap(sub['start_time'], sub['end_time']):
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error checking seat availability: {str(e)}")
            return False
