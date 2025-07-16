# Library Management System - Changelog

## Version 1.0.6 (2025-07-16)

### Major Changes
- **Timeslot Locker Field Redesign**
  - Changed `lockers_available` from INTEGER count to BOOLEAN availability flag
  - Updated database schema: `lockers_available BOOLEAN DEFAULT 0`
  - Replaced text input with checkbox in timeslot management GUI
  - Updated display to show "Yes/No" instead of numeric values
  - Added database migration script for existing installations

### Bug Fixes
- **Code Quality Improvements**
  - Fixed duplicate assignment in timeslot management (`timeslot.lockers_available = lockers`)
  - Removed unused import warnings across multiple files
  - Fixed f-string formatting issues in setup.py
  - Updated bare except statements to use proper exception handling

### Technical Improvements
- Enhanced boolean handling in Timeslot model with explicit `bool()` conversion
- Improved data validation in timeslot form to use boolean values
- Added comprehensive migration script (`migrate_lockers.py`) for database updates
- Better error handling and type consistency across the application

### Files Modified
1. `config/database.py` - Updated schema for boolean locker field
2. `models/timeslot.py` - Enhanced boolean handling and data conversion
3. `gui/timeslot_management.py` - Replaced text input with checkbox interface
4. `migrate_lockers.py` - New migration script for database updates
5. Various files - Code quality improvements and lint fixes

## Version 1.0.5 (2025-07-16)

### Bug Fixes
- **Validation System**
  - Fixed locker number validation to properly handle optional empty fields
  - Fixed Aadhaar number validation to handle None values and empty strings correctly
  - Improved validation error handling for optional fields

- **Date Handling**
  - Fixed date comparison errors in subscription model by properly converting string dates to date objects
  - Added robust date parsing in `_from_row` method for subscription loading

- **WhatsApp Automation**
  - Added Chrome browser detection and fallback handling
  - Improved error messages when Chrome binary is not found
  - Added support for multiple Chrome installation paths (Google Chrome, Chromium, Snap packages)
  - Fixed bare except statements for better error handling
  - Removed unused variables to clean up code

### Technical Improvements
- Enhanced error reporting with more descriptive messages
- Added proper exception handling throughout WhatsApp automation
- Improved validation logic for optional fields
- Better handling of edge cases in form validation

## Version 1.0.4 (2024-01-XX)

### Bug Fixes
- Fixed geometry manager conflicts in all GUI components
- Corrected FPDF import issues
- Resolved GUI layout problems in student, timeslot, and book management

## Version 1.0.3 (2024-01-XX)

### Features
- Complete GUI implementation with tabbed interface
- Student management with gender-based seat assignment
- Timeslot management with overlap detection
- Book borrowing system
- Analytics dashboard with data visualization
- PDF receipt generation
- Excel export functionality

## Version 1.0.2 (2024-01-XX)

### Database
- Implemented complete database schema
- Added 82-seat configuration (rows 1&10 for girls, rows 2-9 for boys)
- Created all necessary tables with relationships

## Version 1.0.1 (2024-01-XX)

### Initial Release
- Project structure setup
- Basic models implementation
- Configuration system
