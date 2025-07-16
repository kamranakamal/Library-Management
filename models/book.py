"""
Book model for database operations
"""

from config.database import DatabaseManager


class Book:
    """Book model class"""
    
    def __init__(self, title=None, author=None, isbn=None, category=None,
                 total_copies=1, available_copies=1, book_id=None):
        self.id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self.total_copies = total_copies
        self.available_copies = available_copies
        self.is_active = True
        self.db_manager = DatabaseManager()
    
    def save(self):
        """Save book to database"""
        if self.id:
            return self._update()
        else:
            return self._create()
    
    def _create(self):
        """Create new book record"""
        query = '''
            INSERT INTO books (
                title, author, isbn, category, total_copies, available_copies
            ) VALUES (?, ?, ?, ?, ?, ?)
        '''
        params = (
            self.title, self.author, self.isbn, self.category,
            self.total_copies, self.available_copies
        )
        
        self.id = self.db_manager.execute_query(query, params)
        return self.id
    
    def _update(self):
        """Update existing book record"""
        query = '''
            UPDATE books SET
                title = ?, author = ?, isbn = ?, category = ?,
                total_copies = ?, available_copies = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        params = (
            self.title, self.author, self.isbn, self.category,
            self.total_copies, self.available_copies, self.id
        )
        
        self.db_manager.execute_query(query, params)
        return self.id
    
    def delete(self):
        """Soft delete book (mark as inactive)"""
        if not self.id:
            raise ValueError("Cannot delete book without ID")
        
        query = "UPDATE books SET is_active = 0 WHERE id = ?"
        self.db_manager.execute_query(query, (self.id,))
        self.is_active = False
    
    @classmethod
    def get_by_id(cls, book_id):
        """Get book by ID"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM books WHERE id = ? AND is_active = 1"
        result = db_manager.execute_query(query, (book_id,))
        
        if result:
            row = result[0]
            return cls._from_row(row)
        return None
    
    @classmethod
    def get_all(cls, active_only=True):
        """Get all books"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM books"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY title"
        
        results = db_manager.execute_query(query)
        return [cls._from_row(row) for row in results]
    
    @classmethod
    def search(cls, search_term):
        """Search books by title, author, or ISBN"""
        db_manager = DatabaseManager()
        query = '''
            SELECT * FROM books 
            WHERE (title LIKE ? OR author LIKE ? OR isbn LIKE ?)
            AND is_active = 1
            ORDER BY title
        '''
        search_pattern = f"%{search_term}%"
        results = db_manager.execute_query(query, (search_pattern, search_pattern, search_pattern))
        return [cls._from_row(row) for row in results]
    
    @classmethod
    def get_by_category(cls, category):
        """Get books by category"""
        db_manager = DatabaseManager()
        query = "SELECT * FROM books WHERE category = ? AND is_active = 1 ORDER BY title"
        results = db_manager.execute_query(query, (category,))
        return [cls._from_row(row) for row in results]
    
    @classmethod
    def _from_row(cls, row):
        """Create Book object from database row"""
        book = cls()
        book.id = row['id']
        book.title = row['title']
        book.author = row['author']
        book.isbn = row['isbn']
        book.category = row['category']
        book.total_copies = row['total_copies']
        book.available_copies = row['available_copies']
        book.is_active = bool(row['is_active'])
        return book
    
    def is_available(self):
        """Check if book is available for borrowing"""
        return self.available_copies > 0
    
    def borrow(self):
        """Decrease available copies when book is borrowed"""
        if self.available_copies <= 0:
            raise ValueError("No copies available for borrowing")
        
        self.available_copies -= 1
        query = "UPDATE books SET available_copies = ? WHERE id = ?"
        self.db_manager.execute_query(query, (self.available_copies, self.id))
    
    def return_book(self):
        """Increase available copies when book is returned"""
        if self.available_copies >= self.total_copies:
            raise ValueError("Cannot return more copies than total")
        
        self.available_copies += 1
        query = "UPDATE books SET available_copies = ? WHERE id = ?"
        self.db_manager.execute_query(query, (self.available_copies, self.id))
    
    def get_borrowing_history(self):
        """Get borrowing history for this book"""
        query = '''
            SELECT bb.*, s.name as student_name, s.mobile_number
            FROM book_borrowings bb
            JOIN students s ON bb.student_id = s.id
            WHERE bb.book_id = ?
            ORDER BY bb.borrow_date DESC
        '''
        return self.db_manager.execute_query(query, (self.id,))
    
    def get_current_borrowers(self):
        """Get current borrowers of this book"""
        query = '''
            SELECT bb.*, s.name as student_name, s.mobile_number
            FROM book_borrowings bb
            JOIN students s ON bb.student_id = s.id
            WHERE bb.book_id = ? AND bb.is_returned = 0
            ORDER BY bb.borrow_date
        '''
        return self.db_manager.execute_query(query, (self.id,))
    
    def validate(self):
        """Validate book data"""
        errors = []
        
        if not self.title or not self.title.strip():
            errors.append("Title is required")
        
        if self.total_copies < 1:
            errors.append("Total copies must be at least 1")
        
        if self.available_copies < 0:
            errors.append("Available copies cannot be negative")
        
        if self.available_copies > self.total_copies:
            errors.append("Available copies cannot exceed total copies")
        
        return errors
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def __repr__(self):
        return f"Book(id={self.id}, title='{self.title}', available={self.available_copies}/{self.total_copies})"
