"""
Student subscription model for database operations
"""

from datetime import date, timedelta
from config.database import DatabaseManager


class Subscription:
    """Student subscription model class"""
    
    def __init__(self, student_id=None, seat_id=None, timeslot_id=None,
                 start_date=None, end_date=None, amount_paid=None,
                 receipt_number=None, receipt_path=None, subscription_id=None):
        self.id = subscription_id
        self.student_id = student_id
        self.seat_id = seat_id
        self.timeslot_id = timeslot_id
        self.start_date = start_date
        self.end_date = end_date
        self.amount_paid = amount_paid
        self.receipt_number = receipt_number
        self.receipt_path = receipt_path
        self.is_active = True
        self.db_manager = DatabaseManager()
    
    def save(self):
        """Save subscription to database"""
        if self.id:
            return self._update()
        else:
            return self._create()
    
    def _create(self):
        """Create new subscription record"""
        # Generate receipt number if not provided
        if not self.receipt_number:
            self.receipt_number = self._generate_receipt_number()
        
        query = '''
            INSERT INTO student_subscriptions (
                student_id, seat_id, timeslot_id, start_date, end_date,
                amount_paid, receipt_number, receipt_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            self.student_id, self.seat_id, self.timeslot_id,
            self.start_date, self.end_date, self.amount_paid,
            self.receipt_number, self.receipt_path
        )
        
        self.id = self.db_manager.execute_query(query, params)
        return self.id
    
    def _update(self):
        """Update existing subscription record"""
        query = '''
            UPDATE student_subscriptions SET
                student_id = ?, seat_id = ?, timeslot_id = ?, start_date = ?,
                end_date = ?, amount_paid = ?, receipt_number = ?, receipt_path = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        params = (
            self.student_id, self.seat_id, self.timeslot_id,
            self.start_date, self.end_date, self.amount_paid,
            self.receipt_number, self.receipt_path, self.id
        )
        
        self.db_manager.execute_query(query, params)
        return self.id
    
    def _generate_receipt_number(self):
        """Generate unique receipt number"""
        # Format: RCP-YYYYMMDD-NNNN
        today = date.today()
        date_str = today.strftime("%Y%m%d")
        
        # Get count of receipts for today
        query = '''
            SELECT COUNT(*) as count 
            FROM student_subscriptions 
            WHERE receipt_number LIKE ?
        '''
        pattern = f"RCP-{date_str}-%"
        result = self.db_manager.execute_query(query, (pattern,))
        count = result[0]['count'] if result else 0
        
        return f"RCP-{date_str}-{count + 1:04d}"
    
    def delete(self):
        """Soft delete subscription (mark as inactive)"""
        if not self.id:
            raise ValueError("Cannot delete subscription without ID")
        
        query = "UPDATE student_subscriptions SET is_active = 0 WHERE id = ?"
        self.db_manager.execute_query(query, (self.id,))
        self.is_active = False
    
    @classmethod
    def get_by_id(cls, subscription_id):
        """Get subscription by ID"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM student_subscriptions WHERE id = ?"
        result = db_manager.execute_query(query, (subscription_id,))
        
        if result:
            row = result[0]
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_by_student_id(cls, student_id, active_only=True):
        """Get subscriptions by student ID"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM student_subscriptions WHERE student_id = ?"
        if active_only:
            query += " AND is_active = 1 AND end_date >= date('now')"
        query += " ORDER BY start_date DESC"
        
        results = db_manager.execute_query(query, (student_id,))
        return [cls._from_row(row) for row in results]
    
    @classmethod
    def get_by_seat_id(cls, seat_id, active_only=True):
        """Get subscriptions by seat ID"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM student_subscriptions WHERE seat_id = ?"
        if active_only:
            query += " AND is_active = 1 AND end_date >= date('now')"
        query += " ORDER BY start_date DESC"
        
        results = db_manager.execute_query(query, (seat_id,))
        return [cls._from_row(row) for row in results]
    
    @classmethod
    def get_expiring_soon(cls, days=7):
        """Get subscriptions expiring within specified days"""
        db_manager = DatabaseManager()
        expiry_date = date.today() + timedelta(days=days)
        
        query = '''
            SELECT ss.*, s.name as student_name, s.mobile_number,
                   seat.id as seat_number, t.name as timeslot_name
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            JOIN seats seat ON ss.seat_id = seat.id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.is_active = 1 AND ss.end_date BETWEEN date('now') AND ?
            ORDER BY ss.end_date
        '''
        
        results = db_manager.execute_query(query, (expiry_date,))
        return results
    
    @classmethod
    def _from_row(cls, row):
        """Create Subscription object from database row"""
        from datetime import datetime
        
        subscription = cls()
        subscription.id = row['id']
        subscription.student_id = row['student_id']
        subscription.seat_id = row['seat_id']
        subscription.timeslot_id = row['timeslot_id']
        
        # Handle date conversion from string to date object
        if isinstance(row['start_date'], str):
            subscription.start_date = datetime.strptime(row['start_date'], '%Y-%m-%d').date()
        else:
            subscription.start_date = row['start_date']
            
        if isinstance(row['end_date'], str):
            subscription.end_date = datetime.strptime(row['end_date'], '%Y-%m-%d').date()
        else:
            subscription.end_date = row['end_date']
        
        subscription.amount_paid = row['amount_paid']
        subscription.receipt_number = row['receipt_number']
        subscription.receipt_path = row['receipt_path']
        subscription.is_active = bool(row['is_active'])
        return subscription
    
    def check_overlap_with_student_subscriptions(self):
        """Check if this subscription overlaps with student's other subscriptions"""
        query = '''
            SELECT COUNT(*) as conflicts
            FROM student_subscriptions 
            WHERE student_id = ? AND seat_id = ? AND is_active = 1
            AND NOT (end_date < ? OR start_date > ?)
            AND id != ?
        '''
        params = (
            self.student_id, self.seat_id, self.start_date, 
            self.end_date, self.id or 0
        )
        
        result = self.db_manager.execute_query(query, params)
        return result[0]['conflicts'] > 0 if result else False
    
    def renew(self, months=None):
        """Renew subscription for specified months"""
        if not months:
            # Get timeslot duration
            from models.timeslot import Timeslot
            timeslot = Timeslot.get_by_id(self.timeslot_id)
            months = timeslot.duration_months if timeslot else 1
        
        # Create new subscription starting from current end date
        new_subscription = Subscription(
            student_id=self.student_id,
            seat_id=self.seat_id,
            timeslot_id=self.timeslot_id,
            start_date=self.end_date,
            end_date=self.end_date + timedelta(days=30 * months),
            amount_paid=self.amount_paid
        )
        
        return new_subscription.save()
    
    def is_expired(self):
        """Check if subscription is expired"""
        return self.end_date < date.today()
    
    def days_until_expiry(self):
        """Get number of days until expiry"""
        return (self.end_date - date.today()).days
    
    def validate(self):
        """Validate subscription data"""
        errors = []
        
        if not self.student_id:
            errors.append("Student ID is required")
        
        if not self.seat_id:
            errors.append("Seat ID is required")
        
        if not self.timeslot_id:
            errors.append("Timeslot ID is required")
        
        if not self.start_date:
            errors.append("Start date is required")
        
        if not self.end_date:
            errors.append("End date is required")
        
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            errors.append("End date must be after start date")
        
        if not self.amount_paid or self.amount_paid <= 0:
            errors.append("Amount paid must be greater than 0")
        
        # Check for overlaps
        if self.check_overlap_with_student_subscriptions():
            errors.append("This subscription conflicts with existing bookings")
        
        return errors
    
    def __str__(self):
        return f"Subscription {self.receipt_number} ({self.start_date} to {self.end_date})"
    
    def __repr__(self):
        return f"Subscription(id={self.id}, student_id={self.student_id}, seat_id={self.seat_id})"
