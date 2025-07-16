"""
Database configuration and management
"""

import sqlite3
import os
from config.settings import DATABASE_PATH


class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = os.path.dirname(self.db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def initialize_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Students table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    father_name TEXT NOT NULL,
                    gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female')),
                    mobile_number TEXT NOT NULL,
                    aadhaar_number TEXT,
                    email TEXT,
                    photo_path TEXT,
                    locker_number INTEGER,
                    registration_date DATE NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Seats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS seats (
                    id INTEGER PRIMARY KEY,
                    row_number INTEGER NOT NULL,
                    gender_restriction TEXT CHECK (gender_restriction IN ('Male', 'Female', 'Any')),
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Timeslots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS timeslots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    duration_months INTEGER NOT NULL DEFAULT 1,
                    lockers_available BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Student subscriptions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    seat_id INTEGER NOT NULL,
                    timeslot_id INTEGER NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    amount_paid DECIMAL(10,2) NOT NULL,
                    receipt_number TEXT UNIQUE,
                    receipt_path TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    FOREIGN KEY (seat_id) REFERENCES seats (id),
                    FOREIGN KEY (timeslot_id) REFERENCES timeslots (id)
                )
            ''')
            
            # Books table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT,
                    isbn TEXT,
                    category TEXT,
                    total_copies INTEGER DEFAULT 1,
                    available_copies INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Book borrowings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS book_borrowings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    borrow_date DATE NOT NULL,
                    return_date DATE,
                    due_date DATE NOT NULL,
                    fine_amount DECIMAL(10,2) DEFAULT 0,
                    is_returned BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    FOREIGN KEY (book_id) REFERENCES books (id)
                )
            ''')
            
            # Initialize seats if empty
            cursor.execute('SELECT COUNT(*) FROM seats')
            if cursor.fetchone()[0] == 0:
                self._initialize_seats(cursor)
            
            conn.commit()
            print("Database initialized successfully!")
            
        except Exception as e:
            conn.rollback()
            print(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
    
    def _initialize_seats(self, cursor):
        """Initialize seats with gender restrictions"""
        from config.settings import GIRLS_SEATS, BOYS_SEATS
        
        # Girls seats - Row 1 (1-9) and Row 10 (72-82)
        for seat_id in GIRLS_SEATS["row_1"]:
            cursor.execute('''
                INSERT INTO seats (id, row_number, gender_restriction)
                VALUES (?, 1, 'Female')
            ''', (seat_id,))
        
        for seat_id in GIRLS_SEATS["row_10"]:
            cursor.execute('''
                INSERT INTO seats (id, row_number, gender_restriction)
                VALUES (?, 10, 'Female')
            ''', (seat_id,))
        
        # Boys seats - Rows 2-9 (10-71)
        for seat_id in BOYS_SEATS:
            row_number = ((seat_id - 10) // 8) + 2  # Calculate row number
            cursor.execute('''
                INSERT INTO seats (id, row_number, gender_restriction)
                VALUES (?, ?, 'Male')
            ''', (seat_id, row_number))
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_many(self, query, params_list):
        """Execute a query with multiple parameter sets"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
