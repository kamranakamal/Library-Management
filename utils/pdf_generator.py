"""
PDF receipt generation utilities
"""

import os
from datetime import datetime
from fpdf import FPDF

class CustomFPDF(FPDF):
    """Custom FPDF class to include a footer"""
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        self.set_x(10) # Reset x position
        self.cell(0, 10, f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 0, 'L')
import qrcode
from io import BytesIO
from config.settings import (RECEIPTS_DIR, DEFAULT_CURRENCY, APP_NAME, 
                           LIBRARY_NAME, LIBRARY_PHONE, LIBRARY_EMAIL, LIBRARY_ADDRESS, LIBRARY_WEBSITE)


class PDFGenerator:
    """PDF generator for receipts and reports"""
    
    def __init__(self):
        self.pdf = None
    
    def ensure_receipts_directory(self):
        """Ensure receipts directory exists"""
        if not os.path.exists(RECEIPTS_DIR):
            os.makedirs(RECEIPTS_DIR)
    
    def generate_qr_code(self, data, filename=None):
        """Generate QR code for given data and save as temporary file"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to temporary file if filename not provided
            if not filename:
                temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                filename = os.path.join(temp_dir, f"qr_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            img.save(filename)
            return filename
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None
    
    def generate_subscription_receipt(self, subscription, student, seat, timeslot, filename=None):
        """Generate PDF receipt for subscription - Compatible interface"""
        try:
            # Convert objects to data dictionary format
            subscription_data = {
                'receipt_number': subscription.receipt_number,
                'student_name': student.name,
                'father_name': student.father_name,
                'mobile_number': student.mobile_number,
                'aadhaar_number': student.aadhaar_number,
                'seat_id': seat.id,  # Changed from seat.seat_number to seat.id
                'timeslot_name': timeslot.name,
                'timeslot_time': f"{timeslot.start_time} - {timeslot.end_time}",  # Added timeslot time
                'start_date': subscription.start_date,
                'end_date': subscription.end_date,
                'locker_number': student.locker_number,
                'amount_paid': subscription.amount_paid,
                'payment_date': subscription.created_at.split()[0] if hasattr(subscription, 'created_at') else datetime.now().strftime('%Y-%m-%d')
            }
            
            return self._generate_subscription_receipt_from_data(subscription_data, filename)
            
        except Exception as e:
            return False, f"Error generating receipt: {str(e)}"
    
    def _generate_subscription_receipt_from_data(self, subscription_data, custom_filename=None):
        """Generate PDF receipt for subscription from data dictionary"""
        try:
            # Create PDF
            pdf = CustomFPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            
            # Header
            pdf.set_font('Arial', 'B', 18)
            pdf.cell(0, 10, LIBRARY_NAME, 0, 1, 'C')
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, LIBRARY_ADDRESS, 0, 1, 'C')
            pdf.cell(0, 6, f"Phone: {LIBRARY_PHONE} | Email: {LIBRARY_EMAIL}", 0, 1, 'C')
            
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Subscription Receipt', 0, 1, 'C')
            pdf.ln(10)
            
            # Receipt details
            pdf.set_font('Arial', '', 12)
            
            # Receipt number and date
            pdf.cell(0, 8, f"Receipt No: {subscription_data['receipt_number']}", 0, 1)
            pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
            pdf.ln(5)
            
            # Student details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Student Details:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            # Save Y position before student details
            student_details_y = pdf.get_y()
            
            pdf.cell(0, 6, f"Name: {subscription_data['student_name']}", 0, 1)
            pdf.cell(0, 6, f"Father's Name: {subscription_data['father_name']}", 0, 1)
            pdf.cell(0, 6, f"Mobile: {subscription_data['mobile_number']}", 0, 1)
            
            if subscription_data.get('aadhaar_number'):
                pdf.cell(0, 6, f"Aadhaar: {subscription_data['aadhaar_number']}", 0, 1)
            
            pdf.ln(3)  # Small gap after student details
            
            # Subscription details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 6, 'Subscription Details:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(0, 6, f"Seat Number: {subscription_data['seat_id']}", 0, 1)
            pdf.cell(0, 6, f"Timeslot: {subscription_data['timeslot_name']}", 0, 1)
            pdf.cell(0, 6, f"Time: {subscription_data['timeslot_time']}", 0, 1)
            pdf.cell(0, 6, f"Duration: {subscription_data['start_date']} to {subscription_data['end_date']}", 0, 1)
            
            if subscription_data.get('locker_number'):
                pdf.cell(0, 6, f"Locker Number: {subscription_data['locker_number']}", 0, 1)
            
            pdf.ln(8)
            
            # Payment details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Payment Details:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(0, 8, f"Amount Paid: {DEFAULT_CURRENCY} {subscription_data['amount_paid']}", 0, 1)
            pdf.cell(0, 8, f"Payment Date: {subscription_data['payment_date']}", 0, 1)
            pdf.ln(10)
            
            # Terms and conditions
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, 'Terms and Conditions:', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            terms = [
                "1. This receipt is valid for the subscription period mentioned above.",
                "2. No refund will be provided for early termination.",
                "3. Library rules and regulations apply.",
                "4. Lost receipt should be reported immediately.",
                "5. Seat transfer is not allowed without prior approval."
            ]
            
            for term in terms:
                pdf.cell(0, 5, term, 0, 1)
            
            pdf.ln(10)
            
            # Add QR codes at the bottom
            qr_y = pdf.get_y()
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, 'Quick Access:', 0, 1)
            pdf.ln(2)
            
            # Website QR code
            qr_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sangharsh_library_qr.png')
            if os.path.exists(qr_path):
                try:
                    # Position website QR code on the left
                    pdf.image(qr_path, x=30, y=pdf.get_y(), w=25, h=25)
                    
                    # Add text below website QR code
                    pdf.set_xy(20, pdf.get_y() + 26)
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(45, 3, 'Visit our website', 0, 0, 'C')
                    
                    # Generate and add library rules QR code on the right
                    library_rules_url = "https://www.notion.so/Sangharsh-Library-rules-235ed2a2852c80fa980cf28ceeb9f5f1"
                    rules_qr_path = self.generate_qr_code(library_rules_url)
                    if rules_qr_path:
                        # Position library rules QR code on the right
                        pdf.image(rules_qr_path, x=140, y=qr_y + 8, w=25, h=25)
                        
                        # Add text below library rules QR code
                        pdf.set_xy(130, qr_y + 34)
                        pdf.set_font('Arial', '', 8)
                        pdf.cell(45, 3, 'Library rules & policies', 0, 0, 'C')
                        
                        # Clean up temporary QR code file
                        try:
                            os.remove(rules_qr_path)
                        except:
                            pass
                            
                except Exception as e:
                    print(f"Error adding QR codes: {e}")
            
            # Move cursor below QR codes
            pdf.set_y(qr_y + 45)
            
            # Save PDF
            filename = custom_filename or f"receipt_{subscription_data['receipt_number']}.pdf"
            filepath = os.path.join(RECEIPTS_DIR, filename)
            pdf.output(filepath)
            
            return True, filepath
            
        except Exception as e:
            return False, f"Error generating comprehensive receipt: {str(e)}"


    def generate_student_comprehensive_receipt(self, student_data, subscriptions_data):
        """Generate a comprehensive PDF receipt for a student, including all their subscriptions."""
        try:
            pdf = CustomFPDF()
            pdf.add_page()

            # Header
            pdf.set_font('Arial', 'B', 18)
            pdf.cell(0, 10, LIBRARY_NAME, border=0, ln=1, align='C')
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, LIBRARY_ADDRESS, border=0, ln=1, align='C')
            pdf.cell(0, 6, f"Phone: {LIBRARY_PHONE} | Email: {LIBRARY_EMAIL}", border=0, ln=1, align='C')
            pdf.ln(5)

            # Title
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Comprehensive Student Receipt', border=0, ln=1, align='C')
            pdf.ln(10)

            # Student Details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Student Details:', border=0, ln=1, align='L')
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 6, f"Name: {student_data.get('name', 'N/A')}", border=0, ln=1, align='L')
            pdf.cell(0, 6, f"Father's Name: {student_data.get('father_name', 'N/A')}", border=0, ln=1, align='L')
            pdf.cell(0, 6, f"Mobile: {student_data.get('phone', 'N/A')}", border=0, ln=1, align='L')
            reg_date = student_data.get('registration_date', 'N/A')
            if hasattr(reg_date, 'strftime'):
                reg_date = reg_date.strftime('%d/%m/%Y')
            pdf.cell(0, 6, f"Registration Date: {reg_date}", border=0, ln=1, align='L')
            pdf.ln(8)

            # Subscriptions Table Header
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(15, 10, 'Stu ID', border=1, ln=0, align='C')
            pdf.cell(25, 10, 'Start Date', border=1, ln=0, align='C')
            pdf.cell(25, 10, 'End Date', border=1, ln=0, align='C')
            pdf.cell(20, 10, 'Amount', border=1, ln=0, align='C')
            pdf.cell(20, 10, 'Duration', border=1, ln=0, align='C')
            pdf.cell(20, 10, 'Seat No', border=1, ln=0, align='C')
            pdf.cell(35, 10, 'Timeslot', border=1, ln=0, align='C')
            pdf.cell(25, 10, 'Status', border=1, ln=1, align='C')

            # Subscriptions Table Rows
            pdf.set_font('Arial', '', 9)
            for sub in subscriptions_data:
                start_date = sub.get('start_date', 'N/A')
                if isinstance(start_date, datetime):
                    start_date = start_date.strftime('%d/%m/%Y')
                end_date = sub.get('end_date', 'N/A')
                if isinstance(end_date, datetime):
                    end_date = end_date.strftime('%d/%m/%Y')
                
                # Use duration_months from subscription data
                duration_months = sub.get('duration_months', 'N/A')
                if duration_months == 'N/A' or duration_months is None:
                    # Fallback to calculating from dates if duration_months is not available
                    try:
                        # Parse dates if they are strings, otherwise use as-is
                        if isinstance(start_date, str) and start_date != 'N/A':
                            start_dt = datetime.strptime(start_date, '%d/%m/%Y')
                        elif hasattr(start_date, 'strftime'):
                            # Already a datetime object
                            start_dt = start_date
                        else:
                            # Fallback to today if we can't parse
                            start_dt = datetime.now()
                            
                        if isinstance(end_date, str) and end_date != 'N/A':
                            end_dt = datetime.strptime(end_date, '%d/%m/%Y')
                        elif hasattr(end_date, 'strftime'):
                            # Already a datetime object
                            end_dt = end_date
                        else:
                            # Fallback to today if we can't parse
                            end_dt = datetime.now()
                            
                        duration_days = (end_dt - start_dt).days + 1
                        duration_months = round(duration_days / 30.0, 1)
                    except Exception as e:
                        print(f"Duration calculation error: {e}")
                        duration_months = 'N/A'
                
                # Use student ID instead of subscription ID
                student_id = student_data.get('id', 'N/A')
                pdf.cell(15, 10, str(student_id), border=1, ln=0, align='C')
                pdf.cell(25, 10, str(start_date), border=1, ln=0, align='C')
                pdf.cell(25, 10, str(end_date), border=1, ln=0, align='C')
                pdf.cell(20, 10, f"{DEFAULT_CURRENCY} {sub.get('amount_paid', 'N/A')}", border=1, ln=0, align='C')
                pdf.cell(20, 10, f"{duration_months} months", border=1, ln=0, align='C')
                pdf.cell(20, 10, str(sub.get('seat_number', 'N/A')), border=1, ln=0, align='C')
                pdf.cell(35, 10, str(sub.get('timeslot', 'N/A')), border=1, ln=0, align='C')
                pdf.cell(25, 10, str(sub.get('status', 'N/A')), border=1, ln=1, align='C')

            pdf.ln(10)

            # Summary Section
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Subscription Summary:', border=0, ln=1, align='L')
            pdf.ln(2)
            
            # Calculate summary data
            total_subscriptions = len(subscriptions_data)
            active_subscriptions = len([sub for sub in subscriptions_data if sub.get('status', '').lower() == 'active'])
            expired_subscriptions = len([sub for sub in subscriptions_data if sub.get('status', '').lower() == 'expired'])
            
            # Calculate total amount paid
            total_amount_paid = 0
            for sub in subscriptions_data:
                amount = sub.get('amount_paid', 0)
                if isinstance(amount, (int, float)):
                    total_amount_paid += amount
                elif isinstance(amount, str) and amount.replace('.', '', 1).isdigit():
                    total_amount_paid += float(amount)
            
            # Display summary data
            pdf.set_font('Arial', '', 11)
            pdf.cell(0, 6, f"Total Subscriptions: {total_subscriptions}", border=0, ln=1, align='L')
            pdf.cell(0, 6, f"Active Subscriptions: {active_subscriptions}", border=0, ln=1, align='L')
            pdf.cell(0, 6, f"Expired Subscriptions: {expired_subscriptions}", border=0, ln=1, align='L')
            pdf.cell(0, 6, f"Total Amount Paid: {DEFAULT_CURRENCY} {total_amount_paid:.2f}", border=0, ln=1, align='L')
            pdf.ln(8)

            # Terms and conditions
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, 'Terms and Conditions:', border=0, ln=1, align='L')
            pdf.set_font('Arial', '', 10)
            terms = [
                "1. This receipt is valid for the subscription period mentioned above.",
                "2. No refund will be provided for early termination.",
                "3. Library rules and regulations apply.",
                "4. Lost receipt should be reported immediately.",
                "5. Seat transfer is not allowed without prior approval."
            ]
            for term in terms:
                pdf.multi_cell(0, 5, term, border=0, align='L', ln=1)

            # Add QR codes at the bottom
            qr_y = pdf.get_y()
            if qr_y > 220: # Check if there is enough space for QR codes
                pdf.add_page()
                qr_y = pdf.get_y()

            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, 'Quick Access:', border=0, ln=1, align='L')
            pdf.ln(2)

            # Website QR code
            qr_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sangharsh_library_qr.png')
            if os.path.exists(qr_path):
                try:
                    pdf.image(qr_path, x=30, y=pdf.get_y(), w=25, h=25)
                    pdf.set_xy(20, pdf.get_y() + 26)
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(45, 3, 'Visit our website', border=0, ln=0, align='C')

                    # Library rules QR code
                    library_rules_url = "https://www.notion.so/Sangharsh-Library-rules-235ed2a2852c80fa980cf28ceeb9f5f1"
                    rules_qr_path = self.generate_qr_code(library_rules_url)
                    if rules_qr_path:
                        pdf.image(rules_qr_path, x=140, y=qr_y + 8, w=25, h=25)
                        pdf.set_xy(130, qr_y + 34)
                        pdf.set_font('Arial', '', 8)
                        pdf.cell(45, 3, 'Library rules & policies', border=0, ln=0, align='C')
                        try:
                            os.remove(rules_qr_path)
                        except: pass
                except Exception as e:
                    print(f"Error adding QR codes: {e}")

            # Move cursor below QR codes
            pdf.set_y(qr_y + 45)

            # Generate filename with student ID and name
            student_id = student_data.get('id', 'student')
            student_name = student_data.get('name', 'student').replace(' ', '_')
            filename = f"{student_id}_{student_name}_comprehensive_receipt.pdf"
            filepath = os.path.join(RECEIPTS_DIR, filename)

            # Ensure directory exists
            self.ensure_receipts_directory()
            pdf.output(filepath, 'F')
            return True, filepath
        except Exception as e:
            # Using a logger is better, but for now, print to console
            print(f"Error generating comprehensive receipt: {e}")
            return False, str(e)


# Alias for backward compatibility
ReceiptGenerator = PDFGenerator
