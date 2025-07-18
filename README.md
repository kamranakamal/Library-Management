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

> **🪟 Windows Users**: Need Chrome? Quick install: `winget install Google.Chrome`  
> **🐧 Fedora Users**: Need Chrome? Quick install: `sudo dnf install google-chrome-stable`  
> **📖 Full Chrome Setup Guide**: See detailed instructions [below](#-chrome--chromedriver-setup-for-windows)

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

## 🌐 Chrome & ChromeDriver Setup for Windows

### 📋 **Prerequisites for WhatsApp Automation**

The WhatsApp automation feature requires Google Chrome and ChromeDriver to function properly. Follow these step-by-step instructions for Windows installation:

### 🔧 **Method 1: Using Windows Package Manager (Recommended)**

#### **Step 1: Install Google Chrome**
1. **Open Command Prompt or PowerShell as Administrator**
   - Press `Win + X` and select "Windows PowerShell (Admin)" or "Command Prompt (Admin)"

2. **Install Chrome using winget**
   ```cmd
   winget install Google.Chrome
   ```
   
   **Alternative using Chocolatey** (if you have Chocolatey installed):
   ```cmd
   choco install googlechrome
   ```

#### **Step 2: Verify Chrome Installation**
```cmd
# Check if Chrome is installed and get version
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version
```

Expected output: `Google Chrome 119.x.x.xxxx` (or similar)

### 🔧 **Method 2: Manual Installation**

#### **Step 1: Download and Install Chrome**
1. **Download Chrome**
   - Go to [https://www.google.com/chrome/](https://www.google.com/chrome/)
   - Click "Download Chrome"
   - Run the downloaded installer (`ChromeSetup.exe`)

2. **Follow Installation Wizard**
   - Accept the license agreement
   - Choose installation options
   - Wait for installation to complete

#### **Step 2: Verify Installation Paths**
Chrome will be installed in one of these locations:
```
# System-wide installation:
C:\Program Files\Google\Chrome\Application\chrome.exe

# User-specific installation:
C:\Users\[USERNAME]\AppData\Local\Google\Chrome\Application\chrome.exe
```

### 🔧 **ChromeDriver Setup (Automatic)**

**Good News!** 🎉 Our application automatically handles ChromeDriver installation:

1. **Automatic Download**: The app downloads the correct ChromeDriver version
2. **Version Matching**: Automatically matches your Chrome version
3. **Path Management**: Handles all path configurations
4. **Updates**: Automatically updates when Chrome updates

### 🧪 **Testing Your Installation**

#### **Step 1: Test Chrome Detection**
1. **Launch the Library Management Application**
   ```cmd
   python start_application.py
   ```

2. **Navigate to WhatsApp Automation**
   - Click on the "WhatsApp Automation" tab

3. **Test Chrome Installation**
   - Click the "Test Chrome Installation" button
   - The app will show a diagnostic window with:
     - ✅ Chrome detection status
     - 📍 Chrome executable path
     - 🔢 Chrome version information
     - 🚗 ChromeDriver compatibility

#### **Step 2: Test WhatsApp Web Connection**
1. **Initialize WhatsApp**
   - Click "Initialize WhatsApp" button
   - Chrome should open automatically
   - WhatsApp Web should load

2. **QR Code Login**
   - Scan the QR code with your phone's WhatsApp
   - Verify successful connection

### 🛠️ **Troubleshooting Common Issues**

#### **❌ "Chrome not found" Error**

**Solution 1: Check Installation Path**
```cmd
# Verify Chrome is installed
dir "C:\Program Files\Google\Chrome\Application\"
dir "C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\"
```

**Solution 2: Add Chrome to PATH**
1. Open System Properties (`Win + R` → `sysdm.cpl`)
2. Click "Environment Variables"
3. Edit "Path" variable
4. Add Chrome installation directory:
   ```
   C:\Program Files\Google\Chrome\Application
   ```

**Solution 3: Reinstall Chrome**
```cmd
# Uninstall and reinstall
winget uninstall Google.Chrome
winget install Google.Chrome
```

#### **❌ ChromeDriver Compatibility Issues**

**Solution 1: Clear ChromeDriver Cache**
1. Delete ChromeDriver cache:
   ```cmd
   rmdir /s "%USERPROFILE%\.wdm"
   ```
2. Restart the application

**Solution 2: Manual ChromeDriver Update**
1. Check Chrome version:
   ```cmd
   chrome --version
   ```
2. Download matching ChromeDriver from [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
3. Place in application directory

#### **❌ WhatsApp Web Not Loading**

**Solution 1: Check Internet Connection**
- Ensure stable internet connection
- Try accessing [web.whatsapp.com](https://web.whatsapp.com) manually

**Solution 2: Clear Chrome Data**
- Click "Clear Session Data" in the app
- Or manually clear Chrome data:
  ```cmd
  rmdir /s "%USERPROFILE%\AppData\Local\Google\Chrome\User Data\WhatsApp_Session"
  ```

**Solution 3: Disable Antivirus/Firewall Temporarily**
- Some security software blocks automated browsers
- Add Chrome and Python to antivirus exceptions

### 📱 **Alternative Browser Support**

If Chrome doesn't work, the app also supports:

#### **Microsoft Edge**
```cmd
winget install Microsoft.Edge
```

#### **Chromium**
```cmd
winget install Chromium.Chromium
```

#### **Firefox** (Limited Support)
```cmd
winget install Mozilla.Firefox
```

### 🔍 **Advanced Configuration**

#### **Custom Chrome Path**
If Chrome is installed in a non-standard location:

1. **Edit Application Settings**
   - Modify `config/settings.py`
   - Add custom Chrome path:
   ```python
   CHROME_EXECUTABLE_PATH = r"C:\Custom\Path\To\chrome.exe"
   ```

#### **Proxy Configuration**
For networks with proxy:
```python
# In config/settings.py
CHROME_OPTIONS = [
    "--proxy-server=proxy.company.com:8080",
    "--proxy-auth=username:password"
]
```

### 📚 **Additional Resources**

- **Chrome Downloads**: [https://www.google.com/chrome/](https://www.google.com/chrome/)
- **ChromeDriver**: [https://chromedriver.chromium.org/](https://chromedriver.chromium.org/)
- **Selenium Documentation**: [https://selenium-python.readthedocs.io/](https://selenium-python.readthedocs.io/)
- **WhatsApp Web**: [https://web.whatsapp.com/](https://web.whatsapp.com/)

### 🎯 **Quick Verification Checklist**

Before using WhatsApp automation, ensure:

- ✅ Google Chrome is installed and updated
- ✅ Chrome opens from command line
- ✅ Internet connection is stable
- ✅ WhatsApp Web loads in Chrome manually
- ✅ Python application can detect Chrome
- ✅ No antivirus blocking automated browsing
- ✅ ChromeDriver auto-download works

**🎉 Once everything is working, you'll be able to:**
- 📱 Send automated WhatsApp reminders
- 📚 Notify students about overdue books
- 💳 Send subscription expiry alerts
- 📊 Bulk message student groups

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
A: Follow these steps:
1. **Check Chrome Installation**: Use the "Test Chrome Installation" button in the app
2. **Verify Chrome Path**: Ensure Chrome is installed in standard locations:
   - `C:\Program Files\Google\Chrome\Application\chrome.exe` (Windows)
   - `/usr/bin/google-chrome` (Linux)
3. **Update Chrome**: Ensure you have the latest Chrome version
4. **Clear Session Data**: Use the "Clear Session Data" button
5. **Check Internet**: Verify WhatsApp Web loads manually at [web.whatsapp.com](https://web.whatsapp.com)

**Q: "Chrome not found" error on Windows?**
A: Try these solutions:
1. **Install Chrome using winget**: `winget install Google.Chrome`
2. **Add Chrome to PATH**: Add `C:\Program Files\Google\Chrome\Application` to system PATH
3. **Check User Installation**: Look for Chrome in `%LOCALAPPDATA%\Google\Chrome\Application\`
4. **Restart Application**: Close and reopen the application after installing Chrome

**Q: "Chrome not found" error on Fedora/Linux?**
A: Install Chrome using these commands:
```bash
# Fedora
sudo dnf install google-chrome-stable
# OR install Chromium
sudo dnf install chromium

# Ubuntu/Debian
sudo apt update && sudo apt install google-chrome-stable

# Verify installation
which google-chrome
```

**Q: ChromeDriver compatibility issues?**
A: The app auto-downloads ChromeDriver, but if issues persist:
1. **Clear ChromeDriver cache**: Delete `~/.wdm` folder (Linux) or `%USERPROFILE%\.wdm` (Windows)
2. **Update Chrome**: Ensure Chrome is up-to-date
3. **Manual ChromeDriver**: Download from [chromedriver.chromium.org](https://chromedriver.chromium.org/)

**Q: Database errors on startup?**
A: Run `python setup.py` to reinitialize the database with sample data.

**Q: PDF receipts not generating?**
A: Check that the `data/receipts/` directory exists and has write permissions.

**Q: Seat assignment conflicts?**
A: The system automatically prevents overlapping subscriptions and validates seat availability.

**Q: Seats showing as occupied when they shouldn't be?**
A: Use the new diagnostic tools:
1. **Click "Fix Occupancy Issues"** in the seat management area
2. **Use "Diagnose Seat"** to see detailed subscription status
3. **Clear expired subscriptions** that are still marked as active

**Q: Currency symbol (₹) not displaying correctly?**
A: Ensure your system supports UTF-8 encoding:
1. **Windows**: Set system locale to support Unicode
2. **Linux**: Ensure `LANG` environment variable includes UTF-8 (e.g., `en_US.UTF-8`)
3. **Python**: The app handles encoding automatically, but system fonts may need Unicode support

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
