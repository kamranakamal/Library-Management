"""
Application settings and configuration
"""

import os

# Application Information
APP_NAME = "Sangharsh Library"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Library Management Team"

# Library Information
LIBRARY_NAME = "Sangharsh Library"
LIBRARY_PHONE = "+91 85219 10999"
LIBRARY_EMAIL = "sangharshlibrary7@gmail.com"
LIBRARY_WEBSITE = "https://sangharshlibrary.com"  # QR code will point to this URL
LIBRARY_ADDRESS = "Rajgir Road, Opp. of Kohinoor Furniture, Malahbigha, Islampur, Nalanda, Bihar 801303"

# Database Configuration
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "library.db")

# Seat Configuration
TOTAL_SEATS = 82
GIRLS_SEATS = {
    "row_1": list(range(1, 10)),      # Seats 1-9
    "row_10": list(range(72, 83))     # Seats 72-82
}
BOYS_SEATS = list(range(10, 72))      # Seats 10-71

# File Paths
RECEIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "receipts")
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "exports")

# Timeslot Configuration
MIN_DURATION_MONTHS = 1
DEFAULT_CURRENCY = "Rs."

# Currency Configuration
CURRENCY_SYMBOL = "Rs."  # Using Rs. instead of ₹ for better font compatibility
CURRENCY_FORMAT = "{symbol} {amount:,.2f}"  # Format: Rs. 1,234.56

# WhatsApp Configuration
WHATSAPP_WEB_URL = "https://web.whatsapp.com"
WHATSAPP_DELAY = 3  # seconds

# PDF Configuration
PDF_FONT_SIZE = 12
PDF_MARGIN = 20

# GUI Configuration
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
THEME_COLOR = "#2E86AB"
ACCENT_COLOR = "#A23B72"
BACKGROUND_COLOR = "#F18F01"
TEXT_COLOR = "#C73E1D"
