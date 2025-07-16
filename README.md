# 📚 Library Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-green.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg)
![License](https://img.shields.io/badge/License-MIT-red.svg)
![Version](https://img.shields.io/badge/Version-1.0.7-brightgreen.svg)

**A comprehensive library management system built with Python, SQLite, and Tkinter**

*✨ Developed with the assistance of GitHub Copilot*

</div>

---

## 🌟 Features

### 📋 **Student Management**
- ✅ Complete student profile management with photo support
- 👥 Gender-based automatic seat assignment (82 seats total)
- 📱 Contact information and Aadhaar validation
- 🔒 Mandatory subscription requirement for new students
- 📊 Active subscription tracking

### ⏰ **Timeslot Management**
- 🕐 Create and manage library time slots
- ⚡ Automatic overlap detection and prevention
- 💰 Flexible pricing and duration settings
- 🔒 Boolean locker availability flag
- 📈 Real-time occupancy rate calculation

### 💳 **Subscription System**
- 📝 Multiple subscription plans per student
- 🪑 Smart seat allocation based on gender and availability
- 📅 Automatic start/end date calculation
- 🧾 PDF receipt generation with unique numbering
- ⚠️ Conflict detection for overlapping bookings

### 📚 **Book Management**
- 📖 Complete book inventory system
- 📊 Borrowing and return tracking
- ⏰ Due date management with fine calculation
- 🔍 Advanced search and filtering options
- 📋 Borrowing history for each student

### 📊 **Analytics Dashboard**
- 📈 Real-time occupancy statistics
- 💹 Revenue tracking and reports
- 📉 Student engagement metrics
- 📊 Visual charts and graphs
- 📁 Excel export functionality

### 📱 **WhatsApp Automation**
- 📲 Automated subscription expiry reminders
- 📚 Overdue book return notifications
- 🔄 Bulk messaging with anti-spam delays
- 🔐 QR code login for WhatsApp Web
- ⚙️ Chrome browser auto-detection

---

## 🚀 Quick Start

### 📋 Prerequisites

- Python 3.8 or higher
- SQLite3 (included with Python)
- Chrome/Chromium browser (for WhatsApp automation)

### ⚡ Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd "Library Management"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/Mac
   # OR
   .venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database and sample data**
   ```bash
   python setup.py
   ```

5. **Launch the application**
   ```bash
   python start_application.py
   ```

---

## 🗂️ Project Structure

```
Library Management/
├── 📁 config/
│   ├── database.py          # Database configuration & initialization
│   └── settings.py          # Application settings
├── 📁 models/
│   ├── student.py          # Student data model
│   ├── timeslot.py         # Timeslot management model
│   ├── seat.py             # Seat assignment model
│   ├── book.py             # Book inventory model
│   └── subscription.py     # Subscription tracking model
├── 📁 gui/
│   ├── main_window.py      # Main application interface
│   ├── student_management.py    # Student CRUD interface
│   ├── timeslot_management.py   # Timeslot management interface
│   ├── book_management.py      # Book management interface
│   ├── analytics.py             # Analytics dashboard
│   └── whatsapp_window.py      # WhatsApp automation interface
├── 📁 utils/
│   ├── database_manager.py     # High-level DB operations
│   ├── pdf_generator.py        # Receipt & report generation
│   ├── excel_exporter.py       # Data export functionality
│   ├── whatsapp_automation.py  # WhatsApp Web automation
│   └── validators.py           # Input validation utilities
├── 📁 data/
│   ├── library.db              # SQLite database (auto-created)
│   ├── receipts/               # PDF storage directory
│   └── exports/                # Excel export directory
├── main.py                     # Application entry point
├── start_application.py        # Quick start script
├── setup.py                   # Automated setup script
├── requirements.txt           # Dependencies list
├── README.md                  # This comprehensive guide
└── CHANGELOG.md              # Version history
```

---

## 💡 Usage Guide

### 👥 **Student Management**

1. **Adding New Students**
   - Fill in student details (name, father's name, gender, mobile)
   - Optional: Add Aadhaar number, email, and locker number
   - **Important**: A subscription plan is mandatory for new students
   - System automatically opens subscription dialog after student creation

2. **Managing Subscriptions**
   - Select timeslot and duration
   - System automatically assigns appropriate seats based on gender
   - Generate PDF receipts for payment confirmation
   - Track active and expired subscriptions

### ⏰ **Timeslot Management**

1. **Creating Timeslots**
   - Set name, start/end times, and pricing
   - Configure duration in months
   - Set locker availability (Yes/No checkbox)
   - System prevents overlapping time slots

2. **Monitoring Occupancy**
   - View real-time occupancy rates
   - Track available vs occupied seats
   - Analyze popular time slots

### 📚 **Book Management**

1. **Adding Books**
   - Register books with title, author, and category
   - Set availability status and condition
   - Track total book inventory

2. **Managing Borrowing**
   - Issue books to registered students
   - Set due dates and calculate fines
   - Track return status and borrowing history

### 📊 **Analytics Dashboard**

1. **Revenue Tracking**
   - View total revenue by time period
   - Track subscription payments
   - Generate financial reports

2. **Occupancy Analytics**
   - Monitor seat utilization rates
   - Identify peak usage times
   - Export data to Excel for further analysis

### 📱 **WhatsApp Automation**

1. **Setup**
   - Ensure Chrome browser is installed
   - Click "Start WhatsApp" to open WhatsApp Web
   - Scan QR code with your phone to login

2. **Automated Messaging**
   - Send subscription expiry reminders
   - Notify about overdue book returns
   - Bulk messaging with smart delays

---

## ⚙️ Configuration

### 📊 **Seat Configuration**
- **Total Seats**: 82 (configurable in `config/settings.py`)
- **Male Section**: Seats 1-41
- **Female Section**: Seats 42-82
- **Gender-based Assignment**: Automatic seat allocation

### 🗄️ **Database Settings**
- **Database**: SQLite (`data/library.db`)
- **Auto-backup**: Enabled
- **Migration**: Automatic on startup

### 📁 **File Locations**
- **Receipts**: `data/receipts/`
- **Exports**: `data/exports/`
- **Database**: `data/library.db`

---

## 🔧 Troubleshooting

### 🐛 **Common Issues**

**Q: WhatsApp automation not working?**
A: Ensure Chrome browser is installed and WhatsApp Web is accessible. The system auto-detects Chrome installation.

**Q: Database errors on startup?**
A: Run `python setup.py` to reinitialize the database with sample data.

**Q: PDF receipts not generating?**
A: Check that the `data/receipts/` directory exists and has write permissions.

**Q: Seat assignment conflicts?**
A: The system automatically prevents overlapping subscriptions and validates seat availability.

### 📞 **Support**

If you encounter issues:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure proper file permissions in the data directory
4. Review the CHANGELOG.md for recent updates

---

## 🚀 Deployment

### 🏭 **Production Setup**

1. **Environment Preparation**
   ```bash
   python -m venv production_env
   source production_env/bin/activate
   pip install -r requirements.txt
   ```

2. **Database Initialization**
   ```bash
   python setup.py
   ```

3. **Launch Application**
   ```bash
   python start_application.py
   ```

### 🔒 **Security Considerations**

- Keep your database files secure
- Regular backups of `data/library.db`
- Monitor access to WhatsApp automation features
- Validate all user inputs through built-in validators

---

## 📋 System Requirements

### 🖥️ **Minimum Requirements**
- **OS**: Windows 10/11, macOS 10.14+, Linux Ubuntu 18.04+
- **Python**: 3.8 or higher
- **RAM**: 512 MB available
- **Storage**: 100 MB free space
- **Browser**: Chrome/Chromium (for WhatsApp features)

### 🚀 **Recommended Requirements**
- **Python**: 3.11 or higher
- **RAM**: 2 GB available
- **Storage**: 1 GB free space
- **Screen**: 1366x768 or higher resolution

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### 📝 **Contribution Guidelines**
- Follow PEP 8 coding standards
- Add appropriate comments and docstrings
- Test your changes thoroughly
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **🤖 GitHub Copilot**: This project was developed with significant assistance from GitHub Copilot, which helped in code generation, debugging, and optimization throughout the development process.
- **🐍 Python Community**: For excellent libraries and documentation
- **🎨 Tkinter**: For providing a robust GUI framework
- **📚 SQLite**: For lightweight and efficient database management

---

## 📞 Contact

For questions, suggestions, or support, please create an issue in this repository.

---

<div align="center">

**📚 Happy Library Management! 📚**

*Made with ❤️ using Python, SQLite, and Tkinter*

*Powered by GitHub Copilot 🤖*

</div>
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
