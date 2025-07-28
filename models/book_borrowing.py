from config.database import DatabaseManager
from datetime import date

class BookBorrowing:
    """Model for book borrowings"""

    def __init__(self, student_id, book_id, borrow_date, due_date, return_date=None, fine_amount=0, is_returned=0, id=None):
        self.id = id
        self.student_id = student_id
        self.book_id = book_id
        self.borrow_date = borrow_date
        self.due_date = due_date
        self.return_date = return_date
        self.fine_amount = fine_amount
        self.is_returned = is_returned

    def save(self):
        """Save the borrowing record to the database"""
        db = DatabaseManager()
        query = '''
            INSERT INTO book_borrowings (student_id, book_id, borrow_date, due_date, is_returned, fine_amount)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        db.execute_query(query, (self.student_id, self.book_id, self.borrow_date, self.due_date, self.is_returned, self.fine_amount))
        return self

    def return_book(self):
        """Mark a book as returned and update book availability"""
        db = DatabaseManager()
        query = "UPDATE book_borrowings SET is_returned = 1, return_date = ? WHERE id = ?"
        db.execute_query(query, (date.today().strftime('%Y-%m-%d'), self.id))
        
        # Update the book's available copies
        from models.book import Book
        book = Book.get_by_id(self.book_id)
        if book:
            book.return_book()

    @staticmethod
    def get_by_id(borrowing_id):
        """Get a borrowing record by its ID"""
        db = DatabaseManager()
        query = "SELECT * FROM book_borrowings WHERE id = ?"
        result = db.execute_query(query, (borrowing_id,))
        if result:
            b = result[0]
            return BookBorrowing(id=b['id'], student_id=b['student_id'], book_id=b['book_id'], borrow_date=b['borrow_date'], due_date=b['due_date'], return_date=b['return_date'], fine_amount=b['fine_amount'], is_returned=b['is_returned'])
        return None

    @staticmethod
    def get_all_details(filter_by='All'):
        """Get all borrowing records with student and book details"""
        db = DatabaseManager()
        query = '''
            SELECT bb.id, s.name as student_name, s.father_name, s.mobile_number as student_phone, b.title as book_title,
                   bb.borrow_date, bb.due_date, CAST(julianday(bb.due_date) - julianday(bb.borrow_date) AS INTEGER) as days_borrowed,
                   bb.return_date, bb.fine_amount, bb.is_returned
            FROM book_borrowings bb
            JOIN students s ON bb.student_id = s.id
            JOIN books b ON bb.book_id = b.id
        '''
        if filter_by == "Active":
            query += " WHERE bb.is_returned = 0"
        elif filter_by == "Returned":
            query += " WHERE bb.is_returned = 1"
        elif filter_by == "Overdue":
            query += " WHERE bb.is_returned = 0 AND bb.due_date < date('now')"
        
        query += " ORDER BY bb.borrow_date DESC"
        return db.execute_query(query)

    @staticmethod
    def delete_by_id(borrowing_id):
        """Delete a borrowing record by its ID"""
        db = DatabaseManager()
        query = "DELETE FROM book_borrowings WHERE id = ?"
        db.execute_query(query, (borrowing_id,))

