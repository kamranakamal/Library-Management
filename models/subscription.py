"""
Student subscription model for database operations
"""

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from config.database import DatabaseManager


class Subscription:
    """Student subscription model class"""
    
    def __init__(self, student_id=None, seat_id=None, timeslot_id=None,
                 start_date=None, end_date=None, amount_paid=None,
                 receipt_number=None, receipt_path=None, subscription_id=None,
                 created_at=None):
        self.id = subscription_id
        self.student_id = student_id
        self.seat_id = seat_id
        self.timeslot_id = timeslot_id
        self.start_date = start_date
        self.end_date = end_date
        self.amount_paid = amount_paid
        self.receipt_number = receipt_number
        self.receipt_path = receipt_path
        self.created_at = created_at
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
    
    def hard_delete(self):
        """Permanently delete subscription from database"""
        if not self.id:
            raise ValueError("Cannot delete subscription without ID")
        
        query = "DELETE FROM student_subscriptions WHERE id = ?"
        self.db_manager.execute_query(query, (self.id,))
        self.id = None
    
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
                   seat.id as seat_number, t.name as timeslot_name,
                   t.start_time as timeslot_start, t.end_time as timeslot_end
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            JOIN seats seat ON ss.seat_id = seat.id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.is_active = 1 AND s.is_active = 1 AND ss.end_date BETWEEN date('now') AND ?
            ORDER BY ss.end_date
        '''
        
        results = db_manager.execute_query(query, (expiry_date,))
        return results
    
    @classmethod
    def get_expired_subscriptions(cls, days_expired=7):
        """Get subscriptions that have expired within specified days"""
        db_manager = DatabaseManager()
        cutoff_date = date.today() - timedelta(days=days_expired)
        
        query = '''
            SELECT ss.*, s.name as student_name, s.mobile_number,
                   seat.id as seat_number, t.name as timeslot_name,
                   t.start_time as timeslot_start, t.end_time as timeslot_end
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            JOIN seats seat ON ss.seat_id = seat.id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.is_active = 1 AND s.is_active = 1 
                  AND ss.end_date < date('now') 
                  AND ss.end_date >= ?
            ORDER BY ss.end_date DESC
        '''
        
        results = db_manager.execute_query(query, (cutoff_date,))
        return results
    
    @classmethod
    def get_all_expired_subscriptions(cls):
        """Get all expired subscriptions regardless of expiry date"""
        db_manager = DatabaseManager()
        
        query = '''
            SELECT ss.*, s.name as student_name, s.mobile_number,
                   seat.id as seat_number, t.name as timeslot_name,
                   t.start_time as timeslot_start, t.end_time as timeslot_end
            FROM student_subscriptions ss
            JOIN students s ON ss.student_id = s.id
            JOIN seats seat ON ss.seat_id = seat.id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.is_active = 1 AND s.is_active = 1 
                  AND ss.end_date < date('now')
            ORDER BY ss.end_date DESC
        '''
        
        results = db_manager.execute_query(query)
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
        subscription.created_at = row['created_at'] if 'created_at' in row else None
        subscription.is_active = bool(row['is_active'])
        return subscription
    
    def check_overlap_with_student_subscriptions(self):
        """Check if this subscription overlaps with student's other subscriptions"""
        # Check for two types of conflicts:
        # 1. Exact duplicate (same seat + same timeslot combination)
        # 2. Same timeslot conflicts (student can't be in two different seats at same time)
        
        # Check for exact duplicate subscriptions (same seat + same timeslot)
        duplicate_query = '''
            SELECT ss.id, ss.start_date, ss.end_date, s.id as seat_number, t.name as timeslot_name
            FROM student_subscriptions ss
            JOIN seats s ON ss.seat_id = s.id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.student_id = ? AND ss.seat_id = ? AND ss.timeslot_id = ? AND ss.is_active = 1
            AND NOT (ss.end_date < ? OR ss.start_date > ?)
            AND ss.id != ?
        '''
        duplicate_params = (
            self.student_id, self.seat_id, self.timeslot_id, self.start_date, 
            self.end_date, self.id or 0
        )
        
        duplicate_result = self.db_manager.execute_query(duplicate_query, duplicate_params)
        
        if duplicate_result and len(duplicate_result) > 0:
            conflict = duplicate_result[0]
            self._conflict_details = {
                'type': 'duplicate_subscription',
                'seat_number': conflict['seat_number'],
                'timeslot_name': conflict['timeslot_name'],
                'start_date': conflict['start_date'],
                'end_date': conflict['end_date']
            }
            return True
        
        # Check for same timeslot conflicts (student can't be in two different seats at same time)
        same_timeslot_query = '''
            SELECT ss.id, ss.start_date, ss.end_date, s.id as seat_number, t.name as timeslot_name
            FROM student_subscriptions ss
            JOIN seats s ON ss.seat_id = s.id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.student_id = ? AND ss.timeslot_id = ? AND ss.seat_id != ? AND ss.is_active = 1
            AND NOT (ss.end_date < ? OR ss.start_date > ?)
            AND ss.id != ?
        '''
        same_timeslot_params = (
            self.student_id, self.timeslot_id, self.seat_id, self.start_date, 
            self.end_date, self.id or 0
        )
        
        same_timeslot_result = self.db_manager.execute_query(same_timeslot_query, same_timeslot_params)
        
        if same_timeslot_result and len(same_timeslot_result) > 0:
            conflict = same_timeslot_result[0]
            self._conflict_details = {
                'type': 'same_timeslot',
                'seat_number': conflict['seat_number'],
                'timeslot_name': conflict['timeslot_name'],
                'start_date': conflict['start_date'],
                'end_date': conflict['end_date']
            }
            return True
        
        return False
    
    def check_seat_time_overlaps(self):
        """Check if this subscription has time overlaps with other subscriptions on the same seat"""
        from models.timeslot import Timeslot
        
        # Get this subscription's timeslot
        this_timeslot = Timeslot.get_by_id(self.timeslot_id)
        if not this_timeslot:
            return False
        
        # Check for overlaps with other subscriptions on the same seat
        overlap_query = '''
            SELECT ss.id, ss.start_date, ss.end_date, s.id as seat_number, 
                   t.name as timeslot_name, t.start_time, t.end_time
            FROM student_subscriptions ss
            JOIN seats s ON ss.seat_id = s.id
            JOIN timeslots t ON ss.timeslot_id = t.id
            WHERE ss.seat_id = ? AND ss.is_active = 1
            AND NOT (ss.end_date < ? OR ss.start_date > ?)
            AND ss.id != ?
        '''
        overlap_params = (
            self.seat_id, self.start_date, self.end_date, self.id or 0
        )
        
        overlap_result = self.db_manager.execute_query(overlap_query, overlap_params)
        
        for conflict in overlap_result:
            # Check if the timeslots have time overlap
            if this_timeslot.check_overlap(conflict['start_time'], conflict['end_time']):
                self._conflict_details = {
                    'type': 'time_overlap',
                    'seat_number': conflict['seat_number'],
                    'timeslot_name': conflict['timeslot_name'],
                    'start_date': conflict['start_date'],
                    'end_date': conflict['end_date']
                }
                return True
        
        return False
    
    def get_conflict_details(self):
        """Get details about the conflicting subscription"""
        if hasattr(self, '_conflict_details'):
            conflict = self._conflict_details
            return (f"Conflicts with existing subscription on Seat {conflict['seat_number']} "
                   f"({conflict['timeslot_name']}) from {conflict['start_date']} to {conflict['end_date']}")
        return "Conflicts with existing subscription"
    
    def renew(self, months=None, amount=None):
        """Renew subscription for specified months"""
        if not months:
            # Get timeslot duration
            from models.timeslot import Timeslot
            timeslot = Timeslot.get_by_id(self.timeslot_id)
            months = timeslot.duration_months if timeslot else 1
        
        # Get the renewal amount (either provided or from timeslot price)
        if amount is None:
            from models.timeslot import Timeslot
            timeslot = Timeslot.get_by_id(self.timeslot_id)
            amount = timeslot.price if timeslot else 0
        
        # Create new subscription starting from current end date
        from dateutil.relativedelta import relativedelta
        new_end_date = self.end_date + relativedelta(months=months)
        
        new_subscription = Subscription(
            student_id=self.student_id,
            seat_id=self.seat_id,
            timeslot_id=self.timeslot_id,
            start_date=self.end_date,
            end_date=new_end_date,
            amount_paid=amount  # Use new amount, not previous amount
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
            errors.append(self.get_conflict_details())
        
        # Check for time overlaps on the same seat with different timeslots
        if self.check_seat_time_overlaps():
            errors.append(self.get_conflict_details())
        
        return errors
    
    def get_conflict_details(self):
        """Get detailed conflict information for better error messages"""
        if not hasattr(self, '_conflict_details'):
            return "This subscription conflicts with existing bookings"
        
        conflict = self._conflict_details
        
        if conflict['type'] == 'duplicate_subscription':
            return (f"Duplicate subscription: You already have a subscription for Seat {conflict['seat_number']} "
                   f"in {conflict['timeslot_name']} from {conflict['start_date']} to {conflict['end_date']}. "
                   f"You cannot purchase the same subscription plan twice. Please choose a different timeslot or wait for the current subscription to expire.")
        
        elif conflict['type'] == 'same_timeslot':
            return (f"Time conflict: You already have a subscription for {conflict['timeslot_name']} "
                   f"(Seat {conflict['seat_number']}) from {conflict['start_date']} to {conflict['end_date']}. "
                   f"A student cannot have multiple seats in the same timeslot during overlapping periods.")
        
        return "This subscription conflicts with existing bookings"
    
    def get_seat(self):
        """Get the seat object for this subscription"""
        from models.seat import Seat
        return Seat.get_by_id(self.seat_id)
    
    def get_timeslot(self):
        """Get the timeslot object for this subscription"""
        from models.timeslot import Timeslot
        return Timeslot.get_by_id(self.timeslot_id)
    
    def __str__(self):
        return f"Subscription {self.receipt_number} ({self.start_date} to {self.end_date})"
    
    def __repr__(self):
        return f"Subscription(id={self.id}, student_id={self.student_id}, seat_id={self.seat_id})"
