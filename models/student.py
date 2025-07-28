"""
Student model for database operations
"""

from datetime import date
from config.database import DatabaseManager


class Student:
    """Student model class"""
    
    def __init__(self, name=None, father_name=None, gender=None, mobile_number=None,
                 aadhaar_number=None, email=None, photo_path=None, locker_number=None,
                 registration_date=None, student_id=None):
        self.id = student_id
        self.name = name
        self.father_name = father_name
        self.gender = gender
        self.mobile_number = mobile_number
        self.aadhaar_number = aadhaar_number
        self.email = email
        self.photo_path = photo_path
        self.locker_number = locker_number
        self.registration_date = registration_date or date.today()
        self.is_active = True
        self.db_manager = DatabaseManager()
    
    def save(self):
        """Save student to database"""
        if self.id:
            return self._update()
        else:
            return self._create()
    
    def _create(self):
        """Create new student record"""
        query = '''
            INSERT INTO students (
                name, father_name, gender, mobile_number, aadhaar_number,
                email, photo_path, locker_number, registration_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            self.name, self.father_name, self.gender, self.mobile_number,
            self.aadhaar_number, self.email, self.photo_path,
            self.locker_number, self.registration_date
        )
        
        self.id = self.db_manager.execute_query(query, params)
        return self.id
    
    def _update(self):
        """Update existing student record"""
        query = '''
            UPDATE students SET
                name = ?, father_name = ?, gender = ?, mobile_number = ?,
                aadhaar_number = ?, email = ?, photo_path = ?, locker_number = ?,
                registration_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        params = (
            self.name, self.father_name, self.gender, self.mobile_number,
            self.aadhaar_number, self.email, self.photo_path,
            self.locker_number, self.registration_date, self.id
        )
        
        self.db_manager.execute_query(query, params)
        return self.id
    
    def delete(self):
        """Soft delete student (mark as inactive) and deactivate all subscriptions"""
        if not self.id:
            raise ValueError("Cannot delete student without ID")
        
        # First deactivate all student's subscriptions
        subscription_query = "UPDATE student_subscriptions SET is_active = 0 WHERE student_id = ?"
        self.db_manager.execute_query(subscription_query, (self.id,))
        
        # Then mark student as inactive
        query = "UPDATE students SET is_active = 0 WHERE id = ?"
        self.db_manager.execute_query(query, (self.id,))
        self.is_active = False
    
    @classmethod
    def get_by_id(cls, student_id):
        """Get student by ID"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM students WHERE id = ? AND is_active = 1"
        result = db_manager.execute_query(query, (student_id,))
        
        if result:
            row = result[0]
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all(cls, active_only=True):
        """Get all students"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM students"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        
        results = db_manager.execute_query(query)
        return [cls._from_row(row) for row in results]
    
    @classmethod
    def search(cls, search_term):
        """Search students by ID, name, mobile, or aadhaar"""
        db_manager = DatabaseManager()
        query = '''
            SELECT * FROM students 
            WHERE (id = ? OR name LIKE ? OR mobile_number LIKE ? OR aadhaar_number LIKE ?)
            AND is_active = 1
            ORDER BY name
        '''
        search_pattern = f"%{search_term}%"
        # Try to convert search term to integer for ID search
        try:
            student_id = int(search_term)
            results = db_manager.execute_query(query, (student_id, search_pattern, search_pattern, search_pattern))
        except ValueError:
            # If not a number, search only by name, mobile, or aadhaar
            query = '''
                SELECT * FROM students 
                WHERE (name LIKE ? OR mobile_number LIKE ? OR aadhaar_number LIKE ?)
                AND is_active = 1
                ORDER BY name
            '''
            results = db_manager.execute_query(query, (search_pattern, search_pattern, search_pattern))
        return [cls._from_row(row) for row in results]
    
    @classmethod
    def _from_row(cls, row):
        """Create Student object from database row"""
        student = cls()
        student.id = row['id']
        student.name = row['name']
        student.father_name = row['father_name']
        student.gender = row['gender']
        student.mobile_number = row['mobile_number']
        student.aadhaar_number = row['aadhaar_number']
        student.email = row['email']
        student.photo_path = row['photo_path']
        student.locker_number = row['locker_number']
        student.registration_date = row['registration_date']
        student.is_active = bool(row['is_active'])
        return student
    
    def get_active_subscriptions(self):
        """Get active subscriptions for this student"""
        from models.subscription import Subscription
        return Subscription.get_by_student_id(self.id, active_only=True)
    
    def get_borrowing_history(self):
        """Get book borrowing history for this student"""
        query = '''
            SELECT bb.*, b.title, b.author
            FROM book_borrowings bb
            JOIN books b ON bb.book_id = b.id
            WHERE bb.student_id = ?
            ORDER BY bb.borrow_date DESC
        '''
        return self.db_manager.execute_query(query, (self.id,))
    
    def validate(self):
        """Validate student data"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Name is required")
        
        if not self.father_name or not self.father_name.strip():
            errors.append("Father's name is required")
        
        if self.gender not in ['Male', 'Female']:
            errors.append("Gender must be Male or Female")
        
        if not self.mobile_number or len(self.mobile_number) != 10:
            errors.append("Valid 10-digit mobile number is required")
        
        if self.aadhaar_number and len(self.aadhaar_number) != 12:
            errors.append("Aadhaar number must be 12 digits")
        
        return errors
    
    def __str__(self):
        return f"{self.name} ({self.mobile_number})"
    
    def __repr__(self):
        return f"Student(id={self.id}, name='{self.name}', gender='{self.gender}')"
