"""
Timeslot model for database operations
"""

from datetime import time
from config.database import DatabaseManager


class Timeslot:
    """Timeslot model class"""
    
    def __init__(self, name=None, start_time=None, end_time=None, price=None,
                 duration_months=1, lockers_available=False, timeslot_id=None):
        self.id = timeslot_id
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.price = price
        self.duration_months = duration_months
        self.lockers_available = bool(lockers_available)
        self.is_active = True
        self.db_manager = DatabaseManager()
    
    def save(self):
        """Save timeslot to database"""
        if self.id:
            return self._update()
        else:
            return self._create()
    
    def _create(self):
        """Create new timeslot record"""
        query = '''
            INSERT INTO timeslots (
                name, start_time, end_time, price, duration_months, lockers_available
            ) VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (
            self.name, self.start_time, self.end_time,
            self.price, self.duration_months, self.lockers_available
        )
        
        self.id = self.db_manager.execute_query(query, params)
        return self.id
    
    def _update(self):
        """Update existing timeslot record"""
        query = '''
            UPDATE timeslots SET
                name = ?, start_time = ?, end_time = ?, price = ?,
                duration_months = ?, lockers_available = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        params = (
            self.name, self.start_time, self.end_time, self.price,
            self.duration_months, self.lockers_available, self.id
        )
        
        self.db_manager.execute_query(query, params)
        return self.id
    
    def delete(self):
        """Soft delete timeslot (mark as inactive)"""
        if not self.id:
            raise ValueError("Cannot delete timeslot without ID")
        
        query = "UPDATE timeslots SET is_active = 0 WHERE id = ?"
        self.db_manager.execute_query(query, (self.id,))
        self.is_active = False
    
    @classmethod
    def get_by_id(cls, timeslot_id):
        """Get timeslot by ID"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM timeslots WHERE id = ? AND is_active = 1"
        result = db_manager.execute_query(query, (timeslot_id,))
        
        if result:
            row = result[0]
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all(cls, active_only=True):
        """Get all timeslots"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM timeslots"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY start_time"
        
        results = db_manager.execute_query(query)
        return [cls._from_row(row) for row in results]
    
    @classmethod
    def _from_row(cls, row):
        """Create Timeslot object from database row"""
        timeslot = cls()
        timeslot.id = row['id']
        timeslot.name = row['name']
        timeslot.start_time = row['start_time']
        timeslot.end_time = row['end_time']
        timeslot.price = row['price']
        timeslot.duration_months = row['duration_months']
        timeslot.lockers_available = bool(row['lockers_available'])
        timeslot.is_active = bool(row['is_active'])
        return timeslot
    
    def check_overlap(self, other_start, other_end):
        """Check if this timeslot overlaps with another time range"""
        if not all([self.start_time, self.end_time, other_start, other_end]):
            return False
        
        # Convert to comparable format if needed
        self_start = self._parse_time(self.start_time)
        self_end = self._parse_time(self.end_time)
        other_start = self._parse_time(other_start)
        other_end = self._parse_time(other_end)
        
        # Check for overlap
        return not (self_end <= other_start or self_start >= other_end)
    
    def _parse_time(self, time_value):
        """Parse time value to time object"""
        if isinstance(time_value, str):
            # Assume format "HH:MM"
            try:
                hour, minute = map(int, time_value.split(':'))
                return time(hour, minute)
            except ValueError:
                return None
        elif isinstance(time_value, time):
            return time_value
        return None
    
    def get_available_seats(self, gender):
        """Get available seats for this timeslot based on gender"""
        query = '''
            SELECT s.id, s.row_number
            FROM seats s
            WHERE s.is_active = 1 
            AND (s.gender_restriction = ? OR s.gender_restriction = 'Any')
            AND s.id NOT IN (
                SELECT DISTINCT ss.seat_id 
                FROM student_subscriptions ss
                JOIN students st ON ss.student_id = st.id
                WHERE ss.timeslot_id = ? 
                AND ss.is_active = 1
                AND st.is_active = 1
                AND ss.end_date >= date('now')
            )
            ORDER BY s.id
        '''
        return self.db_manager.execute_query(query, (gender, self.id))
    
    def get_occupancy_rate(self):
        """Get occupancy rate for this timeslot"""
        query = '''
            SELECT COUNT(*) as occupied_seats,
                   (SELECT COUNT(*) FROM seats WHERE is_active = 1) as total_seats
            FROM student_subscriptions 
            WHERE timeslot_id = ? AND is_active = 1 AND end_date >= date('now')
        '''
        result = self.db_manager.execute_query(query, (self.id,))
        if result:
            row = result[0]
            occupied = row['occupied_seats']
            total = row['total_seats']
            return (occupied / total * 100) if total > 0 else 0
        return 0
    
    def validate(self):
        """Validate timeslot data"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Timeslot name is required")
        
        if not self.start_time:
            errors.append("Start time is required")
        
        if not self.end_time:
            errors.append("End time is required")
        
        if self.start_time and self.end_time:
            start = self._parse_time(self.start_time)
            end = self._parse_time(self.end_time)
            if start and end and start >= end:
                errors.append("End time must be after start time")
        
        if not self.price or self.price <= 0:
            errors.append("Price must be greater than 0")
        
        if self.duration_months < 1:
            errors.append("Duration must be at least 1 month")
        
        return errors
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"
    
    def __repr__(self):
        return f"Timeslot(id={self.id}, name='{self.name}', price={self.price})"
