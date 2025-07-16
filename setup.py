#!/usr/bin/env python3
"""
Library Management System Setup and Demo
"""

import os
import sys
import sqlite3
from datetime import date

# Ensure the project directory is in Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def create_minimal_database():
    """Create a minimal database with sample data"""
    db_path = os.path.join(project_dir, "data", "library.db")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create tables
        print("Creating database tables...")
        
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
                lockers_available INTEGER DEFAULT 0,
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
        
        # Initialize seats
        print("Initializing seats...")
        cursor.execute('SELECT COUNT(*) FROM seats')
        if cursor.fetchone()[0] == 0:
            # Girls seats - Row 1 (1-9) and Row 10 (72-82)
            for seat_id in range(1, 10):
                cursor.execute('INSERT INTO seats (id, row_number, gender_restriction) VALUES (?, 1, "Female")', (seat_id,))
            
            for seat_id in range(72, 83):
                cursor.execute('INSERT INTO seats (id, row_number, gender_restriction) VALUES (?, 10, "Female")', (seat_id,))
            
            # Boys seats - Rows 2-9 (10-71)
            for seat_id in range(10, 72):
                row_number = ((seat_id - 10) // 8) + 2
                cursor.execute('INSERT INTO seats (id, row_number, gender_restriction) VALUES (?, ?, "Male")', (seat_id, row_number))
        
        # Add sample data
        print("Adding sample data...")
        
        # Sample timeslots
        cursor.execute('SELECT COUNT(*) FROM timeslots')
        if cursor.fetchone()[0] == 0:
            sample_timeslots = [
                ("Morning Shift", "06:00", "12:00", 1500.00, 1, 10),
                ("Afternoon Shift", "12:00", "18:00", 1500.00, 1, 10),
                ("Evening Shift", "18:00", "23:00", 1200.00, 1, 5),
                ("Night Shift", "23:00", "06:00", 1000.00, 1, 5)
            ]
            
            for name, start_time, end_time, price, duration, lockers in sample_timeslots:
                cursor.execute('''
                    INSERT INTO timeslots (name, start_time, end_time, price, duration_months, lockers_available)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, start_time, end_time, price, duration, lockers))
        
        # Sample books
        cursor.execute('SELECT COUNT(*) FROM books')
        if cursor.fetchone()[0] == 0:
            sample_books = [
                ("Introduction to Computer Science", "John Smith", "9781234567890", "Computer Science", 5, 5),
                ("Advanced Mathematics", "Jane Doe", "9781234567891", "Mathematics", 3, 3),
                ("Physics Fundamentals", "Robert Johnson", "9781234567892", "Physics", 4, 4),
                ("History of India", "Priya Sharma", "9781234567893", "History", 2, 2),
                ("English Literature", "Michael Brown", "9781234567894", "Literature", 6, 6)
            ]
            
            for title, author, isbn, category, total, available in sample_books:
                cursor.execute('''
                    INSERT INTO books (title, author, isbn, category, total_copies, available_copies)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (title, author, isbn, category, total, available))
        
        # Sample students
        cursor.execute('SELECT COUNT(*) FROM students')
        if cursor.fetchone()[0] == 0:
            sample_students = [
                ("Rahul Kumar", "Suresh Kumar", "Male", "9876543210", "123456789012", "rahul@email.com", None, None, str(date.today())),
                ("Priya Singh", "Rajesh Singh", "Female", "9876543211", "123456789013", "priya@email.com", None, None, str(date.today())),
                ("Amit Patel", "Kishore Patel", "Male", "9876543212", "123456789014", "amit@email.com", None, None, str(date.today())),
                ("Sneha Reddy", "Venkat Reddy", "Female", "9876543213", "123456789015", "sneha@email.com", None, None, str(date.today()))
            ]
            
            for name, father_name, gender, mobile, aadhaar, email, photo, locker, reg_date in sample_students:
                cursor.execute('''
                    INSERT INTO students (name, father_name, gender, mobile_number, aadhaar_number, email, photo_path, locker_number, registration_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, father_name, gender, mobile, aadhaar, email, photo, locker, reg_date))
        
        conn.commit()
        print("✅ Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_startup_script():
    """Create a startup script for easy application launch"""
    startup_script = f'''#!/usr/bin/env python3
"""
Library Management System Launcher
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project directory to path
project_dir = "{project_dir}"
sys.path.insert(0, project_dir)

def main():
    try:
        # Check if database exists
        db_path = os.path.join(project_dir, "data", "library.db")
        if not os.path.exists(db_path):
            print("Database not found. Please run setup.py first.")
            return
        
        # Import and start application
        from config.database import DatabaseManager
        from gui.main_window import MainWindow
        
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        
        # Create and start GUI
        root = tk.Tk()
        MainWindow(root)
        root.mainloop()
        
    except ImportError as e:
        error_msg = f"Missing dependency: {{e}}\\n\\nPlease install required packages:\\npip install -r requirements.txt"
        try:
            messagebox.showerror("Import Error", error_msg)
        except:
            print(error_msg)
    except Exception as e:
        error_msg = f"Application error: {{e}}"
        try:
            messagebox.showerror("Error", error_msg)
        except:
            print(error_msg)

if __name__ == "__main__":
    main()
'''
    
    with open(os.path.join(project_dir, "start_application.py"), "w") as f:
        f.write(startup_script)
    
    print("✅ Startup script created: start_application.py")

def create_readme_file():
    """Create detailed README with setup instructions"""
    readme_content = '''# Library Management System

A comprehensive library management system built with Python, SQLite, and Tkinter.

## Quick Start

1. **Run Setup**:
   ```bash
   python setup.py
   ```

2. **Start Application**:
   ```bash
   python start_application.py
   ```

## Features

### 🎓 Student Management
- Complete student profile management
- Gender-based automatic seat assignment
- Multiple timeslot bookings per student
- PDF receipt generation
- Student search and subscription renewal

### ⏰ Timeslot Management
- CRUD operations for time duration slots
- Overlap detection and prevention
- Multiple students per seat with non-overlapping timeslots
- Configurable pricing and duration

### 📚 Book Management
- Book inventory management
- Borrow/return tracking
- Student borrowing history
- Category-based organization

### 📊 Analytics & Reports
- Comprehensive statistics dashboard
- Excel export functionality
- Monthly reports
- Seat occupancy visualization

### 📱 WhatsApp Integration
- Automated subscription reminders
- Custom message broadcasting
- Overdue book notifications

## Database Schema

### Seats Configuration
- **Row 1 (Seats 1-9)**: Girls only
- **Rows 2-9 (Seats 10-71)**: Boys only  
- **Row 10 (Seats 72-82)**: Girls only

### Sample Data Included
- 82 seats with proper gender restrictions
- 4 sample timeslots (Morning, Afternoon, Evening, Night)
- 5 sample books across different categories
- 4 sample students (2 male, 2 female)

## File Structure

```
library_management/
├── main.py                 # Main application entry point
├── setup.py                # Database setup script
├── start_application.py    # Easy launcher
├── requirements.txt        # Python dependencies
├── config/
│   ├── database.py         # Database management
│   └── settings.py         # Application settings
├── models/
│   ├── student.py          # Student model
│   ├── timeslot.py         # Timeslot model
│   ├── seat.py             # Seat model
│   ├── book.py             # Book model
│   └── subscription.py     # Subscription model
├── gui/
│   ├── main_window.py      # Main application window
│   ├── student_management.py
│   ├── timeslot_management.py
│   ├── book_management.py
│   ├── analytics.py
│   └── whatsapp_window.py
├── utils/
│   ├── database_manager.py # Database operations
│   ├── pdf_generator.py    # PDF receipt generation
│   ├── excel_exporter.py   # Excel export functionality
│   ├── whatsapp_automation.py
│   └── validators.py       # Input validation
├── data/
│   ├── library.db          # SQLite database
│   ├── receipts/           # PDF receipts storage
│   └── exports/            # Excel exports storage
└── README.md
```

## Installation

### Prerequisites
- Python 3.7+
- tkinter (usually included with Python)

### Optional Dependencies
For full functionality, install:
```bash
pip install pandas openpyxl selenium fpdf2 pillow webdriver-manager matplotlib
```

### Manual Installation
```bash
# Clone or download the project
cd library_management

# Install dependencies (optional for basic functionality)
pip install -r requirements.txt

# Setup database
python setup.py

# Run application
python start_application.py
```

## Usage

### Adding Students
1. Go to **Student Management** tab
2. Fill in student details (name, father's name, gender, mobile are required)
3. Click **Save Student**

### Creating Subscriptions
1. Select or create a student
2. Choose a timeslot from dropdown
3. Select an available seat (filtered by gender)
4. Set duration and amount
5. Click **Add Subscription**

### Managing Books
1. Go to **Book Management** tab
2. Add books in the **Books** sub-tab
3. Handle borrowing/returning in the **Borrowings** sub-tab

### Analytics
1. Go to **Analytics** tab
2. View current statistics in **Overview**
3. Generate charts in **Charts** tab
4. Export data and generate reports in **Reports** tab

### WhatsApp Automation
1. Go to **Tools** > **WhatsApp Automation**
2. Initialize WhatsApp Web connection
3. Send subscription reminders or custom messages

## Troubleshooting

### Common Issues

1. **Database not found**
   - Run `python setup.py` to create the database

2. **Import errors**
   - Install required packages: `pip install -r requirements.txt`

3. **GUI not starting**
   - Ensure tkinter is installed: `python -c "import tkinter"`

4. **WhatsApp automation not working**
   - Install selenium and webdriver-manager
   - Ensure Chrome browser is installed

### Support
For issues or questions, check:
- Database file exists in `data/library.db`
- All required modules are importable
- Python version is 3.7 or higher

## License
This project is open source and available under the MIT License.
'''
    
    with open(os.path.join(project_dir, "README.md"), "w") as f:
        f.write(readme_content)
    
    print("✅ README.md updated with detailed instructions")

def main():
    print("🚀 Library Management System Setup")
    print("=" * 50)
    
    success = True
    
    # Create database
    if create_minimal_database():
        print("✅ Database setup completed")
    else:
        print("❌ Database setup failed")
        success = False
    
    # Create startup script
    create_startup_script()
    
    # Update README
    create_readme_file()
    
    print("\n" + "=" * 50)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\nTo start the application:")
        print("  python start_application.py")
        print("\nOr use the traditional method:")
        print("  python main.py")
        print("\nFeatures available:")
        print("  • Student Management with 82 seats")
        print("  • Timeslot Management with overlap detection")
        print("  • Book Management with borrowing system")
        print("  • Analytics with charts and reports")
        print("  • WhatsApp automation (requires additional setup)")
        print("\nSample data has been added for testing.")
    else:
        print("❌ Setup had some issues. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
