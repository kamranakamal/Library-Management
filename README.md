# Library Management System

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
