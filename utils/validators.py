"""
Input validation utilities
"""

import re
from datetime import datetime, date


class ValidationError(Exception):
    """Custom validation error"""
    pass


class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_name(name, field_name="Name"):
        """Validate name fields"""
        if not name or not name.strip():
            raise ValidationError(f"{field_name} is required")
        
        if len(name.strip()) < 2:
            raise ValidationError(f"{field_name} must be at least 2 characters long")
        
        if len(name.strip()) > 100:
            raise ValidationError(f"{field_name} must not exceed 100 characters")
        
        # Allow only letters, spaces, and common name characters
        if not re.match(r'^[a-zA-Z\s\.\'-]+$', name.strip()):
            raise ValidationError(f"{field_name} can only contain letters, spaces, dots, apostrophes, and hyphens")
        
        return name.strip()
    
    @staticmethod
    def validate_mobile_number(mobile):
        """Validate mobile number"""
        if not mobile:
            raise ValidationError("Mobile number is required")
        
        # Remove any spaces, dashes, or other characters
        clean_mobile = re.sub(r'[^\d]', '', mobile)
        
        if len(clean_mobile) != 10:
            raise ValidationError("Mobile number must be exactly 10 digits")
        
        if not clean_mobile.startswith(('6', '7', '8', '9')):
            raise ValidationError("Mobile number must start with 6, 7, 8, or 9")
        
        return clean_mobile
    
    @staticmethod
    def validate_aadhaar_number(aadhaar):
        """Validate Aadhaar number"""
        # Handle None explicitly
        if aadhaar is None:
            return None
        
        # Convert to string and strip whitespace
        aadhaar_str = str(aadhaar).strip()
        
        # If empty after stripping, return None (optional field)
        if aadhaar_str == "":
            return None
        
        # Remove any spaces or dashes
        clean_aadhaar = re.sub(r'[^\d]', '', aadhaar_str)
        
        if len(clean_aadhaar) != 12:
            raise ValidationError("Aadhaar number must be exactly 12 digits")
        
        # Basic Aadhaar validation (simplified)
        if clean_aadhaar.startswith(('0', '1')):
            raise ValidationError("Invalid Aadhaar number format")
        
        return clean_aadhaar
    
    @staticmethod
    def validate_email(email):
        """Validate email address"""
        if not email:
            return None  # Email is optional
        
        email = email.strip().lower()
        
        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        if len(email) > 254:
            raise ValidationError("Email address is too long")
        
        return email
    
    @staticmethod
    def validate_gender(gender):
        """Validate gender"""
        if not gender:
            raise ValidationError("Gender is required")
        
        valid_genders = ['Male', 'Female']
        if gender not in valid_genders:
            raise ValidationError("Gender must be either 'Male' or 'Female'")
        
        return gender
    
    @staticmethod
    def validate_amount(amount):
        """Validate monetary amount"""
        if amount is None:
            raise ValidationError("Amount is required")
        
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            raise ValidationError("Amount must be a valid number")
        
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0")
        
        if amount > 999999.99:
            raise ValidationError("Amount is too large")
        
        # Round to 2 decimal places
        return round(amount, 2)
    
    @staticmethod
    def validate_date(date_value, field_name="Date"):
        """Validate date"""
        if not date_value:
            raise ValidationError(f"{field_name} is required")
        
        if isinstance(date_value, str):
            try:
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                    try:
                        date_value = datetime.strptime(date_value, fmt).date()
                        break
                    except ValueError:
                        continue
                else:
                    raise ValidationError(f"Invalid {field_name.lower()} format. Use YYYY-MM-DD")
            except ValueError:
                raise ValidationError(f"Invalid {field_name.lower()} format")
        
        if not isinstance(date_value, date):
            raise ValidationError(f"Invalid {field_name.lower()}")
        
        return date_value
    
    @staticmethod
    def validate_time(time_value, field_name="Time"):
        """Validate time"""
        if not time_value:
            raise ValidationError(f"{field_name} is required")
        
        if isinstance(time_value, str):
            # Try to parse time in HH:MM format
            time_pattern = r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$'
            if not re.match(time_pattern, time_value):
                raise ValidationError(f"Invalid {field_name.lower()} format. Use HH:MM (24-hour format)")
        
        return time_value
    
    @staticmethod
    def validate_seat_number(seat_number):
        """Validate seat number"""
        if seat_number is None:
            raise ValidationError("Seat number is required")
        
        try:
            seat_number = int(seat_number)
        except (ValueError, TypeError):
            raise ValidationError("Seat number must be a valid number")
        
        if seat_number < 1 or seat_number > 82:
            raise ValidationError("Seat number must be between 1 and 82")
        
        return seat_number
    
    @staticmethod
    def validate_locker_number(locker_number):
        """Validate locker number"""
        # Handle empty or None values - locker is optional
        if locker_number is None:
            return None
        
        # Convert to string and strip whitespace
        locker_str = str(locker_number).strip()
        
        # If empty after stripping, return None (optional field)
        if locker_str == "":
            return None
        
        try:
            locker_number = int(locker_str)
        except (ValueError, TypeError):
            raise ValidationError("Locker number must be a valid number")
        
        if locker_number < 1:
            raise ValidationError("Locker number must be positive")
        
        return locker_number
    
    @staticmethod
    def validate_isbn(isbn):
        """Validate ISBN"""
        if not isbn:
            return None  # ISBN is optional
        
        # Remove hyphens and spaces
        clean_isbn = re.sub(r'[^\dX]', '', isbn.upper())
        
        # Check ISBN-10 or ISBN-13
        if len(clean_isbn) == 10:
            # ISBN-10 validation
            if not re.match(r'^\d{9}[\dX]$', clean_isbn):
                raise ValidationError("Invalid ISBN-10 format")
        elif len(clean_isbn) == 13:
            # ISBN-13 validation
            if not re.match(r'^\d{13}$', clean_isbn):
                raise ValidationError("Invalid ISBN-13 format")
        else:
            raise ValidationError("ISBN must be either 10 or 13 characters")
        
        return clean_isbn
    
    @staticmethod
    def validate_book_copies(copies):
        """Validate book copies count"""
        if copies is None:
            raise ValidationError("Number of copies is required")
        
        try:
            copies = int(copies)
        except (ValueError, TypeError):
            raise ValidationError("Number of copies must be a valid number")
        
        if copies < 1:
            raise ValidationError("Number of copies must be at least 1")
        
        if copies > 1000:
            raise ValidationError("Number of copies cannot exceed 1000")
        
        return copies
    
    @staticmethod
    def validate_duration_months(months):
        """Validate subscription duration in months"""
        if months is None:
            raise ValidationError("Duration is required")
        
        try:
            months = int(months)
        except (ValueError, TypeError):
            raise ValidationError("Duration must be a valid number")
        
        if months < 1:
            raise ValidationError("Duration must be at least 1 month")
        
        if months > 60:
            raise ValidationError("Duration cannot exceed 60 months")
        
        return months
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        """Validate date range"""
        start_date = Validators.validate_date(start_date, "Start date")
        end_date = Validators.validate_date(end_date, "End date")
        
        if start_date >= end_date:
            raise ValidationError("End date must be after start date")
        
        # Check if start date is not too far in the past
        if start_date < date.today().replace(year=date.today().year - 1):
            raise ValidationError("Start date cannot be more than 1 year in the past")
        
        # Check if end date is not too far in the future
        if end_date > date.today().replace(year=date.today().year + 5):
            raise ValidationError("End date cannot be more than 5 years in the future")
        
        return start_date, end_date
    
    @staticmethod
    def validate_student_data(student_data):
        """Validate complete student data"""
        validated_data = {}
        
        validated_data['name'] = Validators.validate_name(student_data.get('name'), "Student name")
        validated_data['father_name'] = Validators.validate_name(student_data.get('father_name'), "Father's name")
        validated_data['gender'] = Validators.validate_gender(student_data.get('gender'))
        validated_data['mobile_number'] = Validators.validate_mobile_number(student_data.get('mobile_number'))
        validated_data['aadhaar_number'] = Validators.validate_aadhaar_number(student_data.get('aadhaar_number'))
        validated_data['email'] = Validators.validate_email(student_data.get('email'))
        validated_data['locker_number'] = Validators.validate_locker_number(student_data.get('locker_number'))
        
        return validated_data
