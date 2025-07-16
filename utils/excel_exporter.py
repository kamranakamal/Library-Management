"""
Excel export utilities
"""

import os
from datetime import datetime
import pandas as pd
from config.settings import EXPORTS_DIR
from utils.database_manager import DatabaseOperations


class ExcelExporter:
    """Export data to Excel files"""
    
    def __init__(self):
        self.db_ops = DatabaseOperations()
        self.ensure_exports_directory()
    
    def ensure_exports_directory(self):
        """Ensure exports directory exists"""
        if not os.path.exists(EXPORTS_DIR):
            os.makedirs(EXPORTS_DIR)
    
    def export_all_data(self):
        """Export all database data to Excel"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"library_data_export_{timestamp}.xlsx"
            filepath = os.path.join(EXPORTS_DIR, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Export students
                students_data = self._get_students_data()
                students_df = pd.DataFrame(students_data)
                students_df.to_excel(writer, sheet_name='Students', index=False)
                
                # Export subscriptions
                subscriptions_data = self._get_subscriptions_data()
                subscriptions_df = pd.DataFrame(subscriptions_data)
                subscriptions_df.to_excel(writer, sheet_name='Subscriptions', index=False)
                
                # Export seats
                seats_data = self._get_seats_data()
                seats_df = pd.DataFrame(seats_data)
                seats_df.to_excel(writer, sheet_name='Seats', index=False)
                
                # Export timeslots
                timeslots_data = self._get_timeslots_data()
                timeslots_df = pd.DataFrame(timeslots_data)
                timeslots_df.to_excel(writer, sheet_name='Timeslots', index=False)
                
                # Export books
                books_data = self._get_books_data()
                books_df = pd.DataFrame(books_data)
                books_df.to_excel(writer, sheet_name='Books', index=False)
                
                # Export borrowings
                borrowings_data = self._get_borrowings_data()
                borrowings_df = pd.DataFrame(borrowings_data)
                borrowings_df.to_excel(writer, sheet_name='Borrowings', index=False)
                
                # Export analytics
                analytics_data = self._get_analytics_data()
                analytics_df = pd.DataFrame(analytics_data)
                analytics_df.to_excel(writer, sheet_name='Analytics', index=False)
            
            return True, filepath
        
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def export_students_data(self):
        """Export only students data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"students_export_{timestamp}.xlsx"
            filepath = os.path.join(EXPORTS_DIR, filename)
            
            students_data = self._get_students_data()
            students_df = pd.DataFrame(students_data)
            students_df.to_excel(filepath, index=False)
            
            return True, filepath
        
        except Exception as e:
            return False, f"Students export failed: {str(e)}"
    
    def export_financial_report(self, year=None, month=None):
        """Export financial report"""
        try:
            if year is None:
                year = datetime.now().year
            if month is None:
                month = datetime.now().month
            
            filename = f"financial_report_{year}_{month:02d}.xlsx"
            filepath = os.path.join(EXPORTS_DIR, filename)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Monthly summary
                monthly_stats = self.db_ops.get_monthly_statistics(year, month)
                summary_df = pd.DataFrame([monthly_stats])
                summary_df.to_excel(writer, sheet_name='Monthly Summary', index=False)
                
                # Detailed subscriptions for the month
                subscriptions_data = self._get_monthly_subscriptions(year, month)
                subscriptions_df = pd.DataFrame(subscriptions_data)
                subscriptions_df.to_excel(writer, sheet_name='Subscriptions', index=False)
                
                # Revenue breakdown by timeslot
                revenue_breakdown = self._get_revenue_breakdown(year, month)
                revenue_df = pd.DataFrame(revenue_breakdown)
                revenue_df.to_excel(writer, sheet_name='Revenue Breakdown', index=False)
            
            return True, filepath
        
        except Exception as e:
            return False, f"Financial report export failed: {str(e)}"
    
    def _get_students_data(self):
        """Get students data for export"""
        query = '''
            SELECT 
                s.id, s.name, s.father_name, s.gender, s.mobile_number,
                s.aadhaar_number, s.email, s.locker_number, s.registration_date,
                COUNT(ss.id) as total_subscriptions,
                SUM(CASE WHEN ss.is_active = 1 AND ss.end_date >= date('now') THEN 1 ELSE 0 END) as active_subscriptions
            FROM students s
            LEFT JOIN student_subscriptions ss ON s.id = ss.student_id
            WHERE s.is_active = 1
            GROUP BY s.id
            ORDER BY s.name
        '''
        return [dict(row) for row in self.db_ops.db_manager.execute_query(query)]
    
    def _get_subscriptions_data(self):
        """Get subscriptions data for export"""
        query = '''
            SELECT 
                ss.id, ss.receipt_number, s.name as student_name, s.mobile_number,
                seat.id as seat_number, t.name as timeslot_name,
                ss.start_date, ss.end_date, ss.amount_paid,
                CASE WHEN ss.end_date >= date('now') THEN 'Active' ELSE 'Expired' END as status
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            JOIN seats seat ON ss.seat_id = seat.id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.is_active = 1
            ORDER BY ss.start_date DESC
        '''
        return [dict(row) for row in self.db_ops.db_manager.execute_query(query)]
    
    def _get_seats_data(self):
        """Get seats data for export"""
        query = '''
            SELECT 
                s.id, s.row_number, s.gender_restriction,
                COUNT(ss.id) as total_bookings,
                COUNT(CASE WHEN ss.is_active = 1 AND ss.end_date >= date('now') THEN 1 END) as current_bookings
            FROM seats s
            LEFT JOIN student_subscriptions ss ON s.id = ss.seat_id
            WHERE s.is_active = 1
            GROUP BY s.id
            ORDER BY s.id
        '''
        return [dict(row) for row in self.db_ops.db_manager.execute_query(query)]
    
    def _get_timeslots_data(self):
        """Get timeslots data for export"""
        query = '''
            SELECT 
                t.id, t.name, t.start_time, t.end_time, t.price, t.duration_months,
                COUNT(ss.id) as total_subscriptions,
                COUNT(CASE WHEN ss.is_active = 1 AND ss.end_date >= date('now') THEN 1 END) as active_subscriptions
            FROM timeslots t
            LEFT JOIN student_subscriptions ss ON t.id = ss.timeslot_id
            WHERE t.is_active = 1
            GROUP BY t.id
            ORDER BY t.start_time
        '''
        return [dict(row) for row in self.db_ops.db_manager.execute_query(query)]
    
    def _get_books_data(self):
        """Get books data for export"""
        query = '''
            SELECT 
                b.id, b.title, b.author, b.isbn, b.category,
                b.total_copies, b.available_copies,
                COUNT(bb.id) as total_borrowings,
                COUNT(CASE WHEN bb.is_returned = 0 THEN 1 END) as current_borrowings
            FROM books b
            LEFT JOIN book_borrowings bb ON b.id = bb.book_id
            WHERE b.is_active = 1
            GROUP BY b.id
            ORDER BY b.title
        '''
        return [dict(row) for row in self.db_ops.db_manager.execute_query(query)]
    
    def _get_borrowings_data(self):
        """Get book borrowings data for export"""
        query = '''
            SELECT 
                bb.id, s.name as student_name, s.mobile_number,
                b.title as book_title, b.author as book_author,
                bb.borrow_date, bb.return_date, bb.due_date,
                bb.fine_amount, bb.is_returned
            FROM book_borrowings bb
            JOIN students s ON bb.student_id = s.id
            JOIN books b ON bb.book_id = b.id
            ORDER BY bb.borrow_date DESC
        '''
        return [dict(row) for row in self.db_ops.db_manager.execute_query(query)]
    
    def _get_analytics_data(self):
        """Get analytics data for export"""
        analytics = self.db_ops.get_analytics_data()
        return [
            {'Metric': 'Total Students', 'Value': analytics['total_students']},
            {'Metric': 'Total Seats', 'Value': analytics['total_seats']},
            {'Metric': 'Occupied Seats', 'Value': analytics['occupied_seats']},
            {'Metric': 'Unoccupied Seats', 'Value': analytics['unoccupied_seats']},
            {'Metric': 'Assigned Students', 'Value': analytics['assigned_students']},
            {'Metric': 'Unassigned Students', 'Value': analytics['unassigned_students']},
            {'Metric': 'Total Books', 'Value': analytics['total_books']},
            {'Metric': 'Active Borrowings', 'Value': analytics['active_borrowings']},
        ]
    
    def _get_monthly_subscriptions(self, year, month):
        """Get subscriptions for specific month"""
        query = '''
            SELECT 
                ss.receipt_number, s.name as student_name,
                seat.id as seat_number, t.name as timeslot_name,
                ss.start_date, ss.end_date, ss.amount_paid
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            JOIN seats seat ON ss.seat_id = seat.id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE strftime('%Y', ss.start_date) = ? 
            AND strftime('%m', ss.start_date) = ?
            AND ss.is_active = 1
            ORDER BY ss.start_date
        '''
        return [dict(row) for row in self.db_ops.db_manager.execute_query(
            query, (str(year), f"{month:02d}")
        )]
    
    def _get_revenue_breakdown(self, year, month):
        """Get revenue breakdown by timeslot for specific month"""
        query = '''
            SELECT 
                t.name as timeslot_name, t.price,
                COUNT(ss.id) as subscriptions_count,
                SUM(ss.amount_paid) as total_revenue
            FROM student_subscriptions ss
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE strftime('%Y', ss.start_date) = ? 
            AND strftime('%m', ss.start_date) = ?
            AND ss.is_active = 1
            GROUP BY t.id, t.name, t.price
            ORDER BY total_revenue DESC
        '''
        return [dict(row) for row in self.db_ops.db_manager.execute_query(
            query, (str(year), f"{month:02d}")
        )]
