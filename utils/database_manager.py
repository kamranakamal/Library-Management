"""
Database management utilities
"""

from config.database import DatabaseManager
from models.student import Student
from models.timeslot import Timeslot
from models.seat import Seat
from models.book import Book


class DatabaseOperations:
    """High-level database operations"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_available_seats_for_student(self, gender, timeslot_id):
        """Get available seats for a student based on gender and timeslot"""
        # Get the new timeslot details
        new_timeslot = Timeslot.get_by_id(timeslot_id)
        if not new_timeslot:
            return []
        
        # Get seats restricted to the student's gender
        seats = Seat.get_by_gender(gender)
        
        # Filter seats that are available for the timeslot
        available_seats = []
        for seat in seats:
            # Check if seat has any conflicting subscriptions based on time overlap
            query = '''
                SELECT ss.*, t.start_time, t.end_time
                FROM student_subscriptions ss
                JOIN timeslots t ON ss.timeslot_id = t.id
                WHERE ss.seat_id = ? AND ss.is_active = 1
                AND ss.end_date >= date('now')
            '''
            result = self.db_manager.execute_query(query, (seat.id,))
            
            # Check for time conflicts with existing subscriptions
            has_conflict = False
            for existing_sub in result:
                if new_timeslot.check_overlap(existing_sub['start_time'], existing_sub['end_time']):
                    has_conflict = True
                    break
            
            if not has_conflict:
                available_seats.append(seat)
        
        return available_seats
    
    def check_timeslot_conflicts(self, student_id, new_timeslot_id, start_date, end_date):
        """Check if new timeslot conflicts with student's existing subscriptions"""
        # Get the new timeslot details
        new_timeslot = Timeslot.get_by_id(new_timeslot_id)
        if not new_timeslot:
            return True, "Invalid timeslot"
        
        # Get student's active subscriptions
        query = '''
            SELECT ss.*, t.start_time, t.end_time
            FROM student_subscriptions ss
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.student_id = ? AND ss.is_active = 1
            AND NOT (ss.end_date < ? OR ss.start_date > ?)
        '''
        
        conflicting_subs = self.db_manager.execute_query(
            query, (student_id, start_date, end_date)
        )
        
        for sub in conflicting_subs:
            # Check time overlap
            if new_timeslot.check_overlap(sub['start_time'], sub['end_time']):
                return True, "Time conflict with existing subscription"
        
        return False, None
    
    def get_analytics_data(self):
        """Get comprehensive analytics data"""
        analytics = {}
        
        # Total students
        analytics['total_students'] = len(Student.get_all())
        
        # Total seats
        analytics['total_seats'] = len(Seat.get_all())
        
        # Occupied seats (with active subscriptions)
        query = '''
            SELECT COUNT(DISTINCT ss.seat_id) as occupied_seats
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            WHERE ss.is_active = 1 
            AND s.is_active = 1
            AND ss.end_date >= date('now')
        '''
        result = self.db_manager.execute_query(query)
        analytics['occupied_seats'] = result[0]['occupied_seats'] if result else 0
        
        # Unoccupied seats
        analytics['unoccupied_seats'] = analytics['total_seats'] - analytics['occupied_seats']
        
        # Slots per seat
        query = '''
            SELECT ss.seat_id, COUNT(*) as slot_count
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            WHERE ss.is_active = 1 
            AND s.is_active = 1
            AND ss.end_date >= date('now')
            GROUP BY ss.seat_id
        '''
        seats_usage = self.db_manager.execute_query(query)
        analytics['seats_usage'] = {row['seat_id']: row['slot_count'] for row in seats_usage}
        
        # Students with assignments vs unassigned
        query = '''
            SELECT COUNT(DISTINCT ss.student_id) as assigned_students
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            WHERE ss.is_active = 1 
            AND s.is_active = 1
            AND ss.end_date >= date('now')
        '''
        result = self.db_manager.execute_query(query)
        analytics['assigned_students'] = result[0]['assigned_students'] if result else 0
        analytics['unassigned_students'] = analytics['total_students'] - analytics['assigned_students']
        
        # Total books and borrowings
        analytics['total_books'] = len(Book.get_all())
        
        query = '''
            SELECT COUNT(*) as active_borrowings
            FROM book_borrowings 
            WHERE is_returned = 0
        '''
        result = self.db_manager.execute_query(query)
        analytics['active_borrowings'] = result[0]['active_borrowings'] if result else 0
        
        return analytics
    
    def get_monthly_statistics(self, year, month):
        """Get statistics for a specific month"""
        # Revenue for the month
        query = '''
            SELECT SUM(ss.amount_paid) as monthly_revenue
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            WHERE strftime('%Y', ss.start_date) = ? 
            AND strftime('%m', ss.start_date) = ?
            AND ss.is_active = 1 AND s.is_active = 1
        '''
        result = self.db_manager.execute_query(query, (str(year), f"{month:02d}"))
        monthly_revenue = result[0]['monthly_revenue'] if result and result[0]['monthly_revenue'] else 0
        
        # New registrations
        query = '''
            SELECT COUNT(*) as new_registrations
            FROM students 
            WHERE strftime('%Y', registration_date) = ? 
            AND strftime('%m', registration_date) = ?
            AND is_active = 1
        '''
        result = self.db_manager.execute_query(query, (str(year), f"{month:02d}"))
        new_registrations = result[0]['new_registrations'] if result else 0
        
        # Book borrowings
        query = '''
            SELECT COUNT(*) as monthly_borrowings
            FROM book_borrowings bb
            JOIN students s ON bb.student_id = s.id
            WHERE strftime('%Y', bb.borrow_date) = ? 
            AND strftime('%m', bb.borrow_date) = ?
            AND s.is_active = 1
        '''
        result = self.db_manager.execute_query(query, (str(year), f"{month:02d}"))
        monthly_borrowings = result[0]['monthly_borrowings'] if result else 0
        
        return {
            'revenue': monthly_revenue,
            'new_registrations': new_registrations,
            'book_borrowings': monthly_borrowings
        }
    
    def get_revenue_by_timeslot(self, year=None, month=None):
        """Get revenue breakdown by timeslot for a specific period"""
        if year and month:
            # Monthly revenue by timeslot
            query = '''
                SELECT t.name as timeslot_name, t.start_time, t.end_time,
                       SUM(ss.amount_paid) as revenue, COUNT(ss.id) as subscription_count
                FROM student_subscriptions ss
                JOIN students s ON ss.student_id = s.id
                JOIN timeslots t ON ss.timeslot_id = t.id
                WHERE strftime('%Y', ss.start_date) = ? 
                AND strftime('%m', ss.start_date) = ?
                AND ss.is_active = 1 AND s.is_active = 1
                GROUP BY t.id, t.name, t.start_time, t.end_time
                ORDER BY t.start_time
            '''
            result = self.db_manager.execute_query(query, (str(year), f"{month:02d}"))
        else:
            # All-time revenue by timeslot
            query = '''
                SELECT t.name as timeslot_name, t.start_time, t.end_time,
                       SUM(ss.amount_paid) as revenue, COUNT(ss.id) as subscription_count
                FROM student_subscriptions ss
                JOIN students s ON ss.student_id = s.id
                JOIN timeslots t ON ss.timeslot_id = t.id
                WHERE ss.is_active = 1 AND s.is_active = 1
                GROUP BY t.id, t.name, t.start_time, t.end_time
                ORDER BY t.start_time
            '''
            result = self.db_manager.execute_query(query)
        
        return result
    
    def get_current_month_revenue(self):
        """Get total revenue for current month"""
        from datetime import date
        current_date = date.today()
        stats = self.get_monthly_statistics(current_date.year, current_date.month)
        return stats['revenue']
    
    def backup_database(self, backup_path):
        """Create database backup"""
        import shutil
        try:
            shutil.copy2(self.db_manager.db_path, backup_path)
            return True, "Backup created successfully"
        except Exception as e:
            return False, f"Backup failed: {str(e)}"
    
    def restore_database(self, backup_path):
        """Restore database from backup"""
        import shutil
        try:
            shutil.copy2(backup_path, self.db_manager.db_path)
            return True, "Database restored successfully"
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
