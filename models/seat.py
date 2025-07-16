"""
Seat model for database operations
"""

from config.database import DatabaseManager


class Seat:
    """Seat model class"""
    
    def __init__(self, seat_id=None, row_number=None, gender_restriction=None):
        self.id = seat_id
        self.row_number = row_number
        self.gender_restriction = gender_restriction
        self.is_active = True
        self.db_manager = DatabaseManager()
    
    @classmethod
    def get_by_id(cls, seat_id):
        """Get seat by ID"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM seats WHERE id = ? AND is_active = 1"
        result = db_manager.execute_query(query, (seat_id,))
        
        if result:
            row = result[0]
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all(cls, active_only=True):
        """Get all seats"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM seats"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY id"
        
        results = db_manager.execute_query(query)
        return [cls._from_row(row) for row in results]
    
    @classmethod
    def get_by_gender(cls, gender):
        """Get seats available for specific gender"""
        db_manager = DatabaseManager()
        query = '''
            SELECT * FROM seats 
            WHERE (gender_restriction = ? OR gender_restriction = 'Any') 
            AND is_active = 1
            ORDER BY id
        '''
        results = db_manager.execute_query(query, (gender,))
        return [cls._from_row(row) for row in results]
    
    @classmethod
    def _from_row(cls, row):
        """Create Seat object from database row"""
        seat = cls()
        seat.id = row['id']
        seat.row_number = row['row_number']
        seat.gender_restriction = row['gender_restriction']
        seat.is_active = bool(row['is_active'])
        return seat
    
    def get_current_occupants(self):
        """Get current active occupants of this seat"""
        query = '''
            SELECT s.*, ss.start_date, ss.end_date, t.name as timeslot_name,
                   t.start_time, t.end_time
            FROM students s
            JOIN student_subscriptions ss ON s.id = ss.student_id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.seat_id = ? AND ss.is_active = 1 AND ss.end_date >= date('now')
            ORDER BY t.start_time
        '''
        return self.db_manager.execute_query(query, (self.id,))
    
    def is_available_for_timeslot(self, timeslot_id, start_date, end_date):
        """Check if seat is available for a specific timeslot and date range"""
        query = '''
            SELECT COUNT(*) as conflicts
            FROM student_subscriptions 
            WHERE seat_id = ? AND timeslot_id = ? AND is_active = 1
            AND NOT (end_date < ? OR start_date > ?)
        '''
        result = self.db_manager.execute_query(query, (self.id, timeslot_id, start_date, end_date))
        return result[0]['conflicts'] == 0 if result else False
    
    def get_occupancy_schedule(self):
        """Get detailed occupancy schedule for this seat"""
        query = '''
            SELECT ss.*, s.name as student_name, t.name as timeslot_name,
                   t.start_time, t.end_time
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.seat_id = ? AND ss.is_active = 1 AND ss.end_date >= date('now')
            ORDER BY t.start_time, ss.start_date
        '''
        return self.db_manager.execute_query(query, (self.id,))
    
    def __str__(self):
        return f"Seat {self.id} (Row {self.row_number}, {self.gender_restriction})"
    
    def __repr__(self):
        return f"Seat(id={self.id}, row={self.row_number}, gender='{self.gender_restriction}')"
