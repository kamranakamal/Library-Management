"""
PDF receipt generation utilities
"""

import os
from datetime import datetime
from fpdf import FPDF
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
            pdf = FPDF()
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
            
            pdf.cell(0, 8, f"Name: {subscription_data['student_name']}", 0, 1)
            pdf.cell(0, 8, f"Father's Name: {subscription_data['father_name']}", 0, 1)
            pdf.cell(0, 8, f"Mobile: {subscription_data['mobile_number']}", 0, 1)
            
            if subscription_data.get('aadhaar_number'):
                pdf.cell(0, 8, f"Aadhaar: {subscription_data['aadhaar_number']}", 0, 1)
            
            # Add QR code on the right side of student details
            qr_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sangharsh_library_qr.png')
            if os.path.exists(qr_path):
                try:
                    # Position QR code on the right side
                    pdf.set_xy(140, student_details_y)
                    pdf.image(qr_path, x=140, y=student_details_y, w=30, h=30)
                    
                    # Add text below QR code
                    pdf.set_xy(125, student_details_y + 32)
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(60, 3, 'Scan to visit our website', 0, 1, 'C')
                except Exception as e:
                    print(f"Error adding QR code: {e}")
            
            pdf.ln(5)
            
            # Subscription details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Subscription Details:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(0, 8, f"Seat Number: {subscription_data['seat_id']}", 0, 1)
            pdf.cell(0, 8, f"Timeslot: {subscription_data['timeslot_name']}", 0, 1)
            pdf.cell(0, 8, f"Time: {subscription_data['timeslot_time']}", 0, 1)  # Added timeslot time
            pdf.cell(0, 8, f"Duration: {subscription_data['start_date']} to {subscription_data['end_date']}", 0, 1)
            
            if subscription_data.get('locker_number'):
                pdf.cell(0, 8, f"Locker Number: {subscription_data['locker_number']}", 0, 1)
            
            pdf.ln(5)
            
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
            
            # Footer
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 8, 'Thank you for choosing our library!', 0, 1, 'C')
            pdf.cell(0, 8, f'Generated on: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
            
            # Save PDF
            filename = custom_filename or f"receipt_{subscription_data['receipt_number']}.pdf"
            filepath = os.path.join(RECEIPTS_DIR, filename)
            pdf.output(filepath)
            
            return True, filepath
            
        except Exception as e:
            return False, f"Error generating receipt: {str(e)}"
    
    def generate_renewal_receipt(self, new_subscription, student, seat, timeslot, filename=None):
        """Generate PDF receipt for subscription renewal - Compatible interface"""
        try:
            # Convert objects to data dictionary format
            renewal_data = {
                'receipt_number': new_subscription.receipt_number,
                'previous_receipt_number': 'N/A',  # This would need to be passed if available
                'student_name': student.name,
                'mobile_number': student.mobile_number,
                'seat_id': seat.id,  # Changed from seat.seat_number to seat.id
                'timeslot_name': timeslot.name,
                'timeslot_time': f"{timeslot.start_time} - {timeslot.end_time}",  # Added timeslot time
                'previous_start': 'N/A',  # These would need to be calculated
                'previous_end': 'N/A',
                'new_start': new_subscription.start_date,
                'new_end': new_subscription.end_date,
                'amount_paid': new_subscription.amount_paid
            }
            
            return self._generate_renewal_receipt_from_data(renewal_data, filename)
            
        except Exception as e:
            return False, f"Error generating renewal receipt: {str(e)}"
    
    def _generate_renewal_receipt_from_data(self, renewal_data, custom_filename=None):
        """Generate PDF receipt for subscription renewal from data dictionary"""
        try:
            # Create PDF
            pdf = FPDF()
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
            pdf.cell(0, 10, 'Subscription Renewal Receipt', 0, 1, 'C')
            pdf.ln(10)
            
            # Receipt details
            pdf.set_font('Arial', '', 12)
            
            # Receipt number and date
            pdf.cell(0, 8, f"Receipt No: {renewal_data['receipt_number']}", 0, 1)
            pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
            pdf.cell(0, 8, f"Previous Receipt: {renewal_data['previous_receipt_number']}", 0, 1)
            pdf.ln(5)
            
            # Student details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Student Details:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(0, 8, f"Name: {renewal_data['student_name']}", 0, 1)
            pdf.cell(0, 8, f"Mobile: {renewal_data['mobile_number']}", 0, 1)
            pdf.cell(0, 8, f"Seat Number: {renewal_data['seat_id']}", 0, 1)
            pdf.cell(0, 8, f"Timeslot: {renewal_data['timeslot_name']}", 0, 1)
            pdf.cell(0, 8, f"Time: {renewal_data['timeslot_time']}", 0, 1)
            pdf.ln(5)
            
            # Renewal details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Renewal Details:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(0, 8, f"Previous Period: {renewal_data['previous_start']} to {renewal_data['previous_end']}", 0, 1)
            pdf.cell(0, 8, f"New Period: {renewal_data['new_start']} to {renewal_data['new_end']}", 0, 1)
            pdf.cell(0, 8, f"Amount Paid: {DEFAULT_CURRENCY}{renewal_data['amount_paid']}", 0, 1)
            pdf.ln(10)
            
            # Footer
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 8, 'Thank you for renewing your subscription!', 0, 1, 'C')
            pdf.cell(0, 8, f'Generated on: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
            
            # Save PDF
            filename = custom_filename or f"renewal_{renewal_data['receipt_number']}.pdf"
            filepath = os.path.join(RECEIPTS_DIR, filename)
            pdf.output(filepath)
            
            return True, filepath
            
        except Exception as e:
            return False, f"Error generating renewal receipt: {str(e)}"
    
    def generate_monthly_report(self, month_data):
        """Generate monthly financial report"""
        try:
            # Create PDF
            pdf = FPDF()
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
            pdf.cell(0, 10, f'Monthly Report - {month_data["month"]} {month_data["year"]}', 0, 1, 'C')
            pdf.ln(10)
            
            # Summary
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Summary:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(0, 8, f"Total Revenue: {DEFAULT_CURRENCY}{month_data['total_revenue']}", 0, 1)
            pdf.cell(0, 8, f"New Registrations: {month_data['new_registrations']}", 0, 1)
            pdf.cell(0, 8, f"Active Subscriptions: {month_data['active_subscriptions']}", 0, 1)
            pdf.cell(0, 8, f"Book Borrowings: {month_data['book_borrowings']}", 0, 1)
            pdf.ln(10)
            
            # Detailed breakdown if provided
            if 'details' in month_data:
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, 'Detailed Breakdown:', 0, 1)
                pdf.set_font('Arial', '', 10)
                
                for detail in month_data['details']:
                    pdf.cell(0, 6, detail, 0, 1)
            
            # Save PDF
            filename = f"monthly_report_{month_data['year']}_{month_data['month']:02d}.pdf"
            filepath = os.path.join(RECEIPTS_DIR, filename)
            pdf.output(filepath)
            
            return True, filepath
            
        except Exception as e:
            return False, f"Error generating monthly report: {str(e)}"

    def generate_student_comprehensive_receipt(self, student_data, subscriptions_data, filename=None):
        """Generate comprehensive receipt showing all subscriptions of a student"""
        try:
            # Create filename if not provided
            if not filename:
                safe_name = student_data['name'].replace(' ', '_').replace('/', '_')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"comprehensive_receipt_{safe_name}_{timestamp}.pdf"
            
            filepath = os.path.join(RECEIPTS_DIR, filename)
            
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font('Arial', 'B', 18)
            pdf.cell(0, 12, LIBRARY_NAME, 0, 1, 'C')
            
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, LIBRARY_ADDRESS, 0, 1, 'C')
            pdf.cell(0, 6, f"Phone: {LIBRARY_PHONE} | Email: {LIBRARY_EMAIL}", 0, 1, 'C')
            
            pdf.ln(8)
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Comprehensive Subscription Receipt', 0, 1, 'C')
            pdf.ln(8)
            
            # Receipt details
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%d/%m/%Y at %H:%M')}", 0, 1)
            pdf.ln(5)
            
            # Student details
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Student Information:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            # Save Y position before student details
            student_details_y = pdf.get_y()
            
            pdf.cell(0, 8, f"Name: {student_data['name']}", 0, 1)
            pdf.cell(0, 8, f"Father's Name: {student_data['father_name']}", 0, 1)
            pdf.cell(0, 8, f"Mobile: {student_data['mobile_number']}", 0, 1)
            if student_data.get('email'):
                pdf.cell(0, 8, f"Email: {student_data['email']}", 0, 1)
            if student_data.get('aadhaar_number'):
                pdf.cell(0, 8, f"Aadhaar: {student_data['aadhaar_number']}", 0, 1)
            pdf.cell(0, 8, f"Registration Date: {student_data['registration_date']}", 0, 1)
            
            # Add QR code on the right side of student details
            qr_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sangharsh_library_qr.png')
            if os.path.exists(qr_path):
                try:
                    # Position QR code on the right side
                    pdf.set_xy(140, student_details_y)
                    pdf.image(qr_path, x=140, y=student_details_y, w=30, h=30)
                    
                    # Add text below QR code
                    pdf.set_xy(125, student_details_y + 32)
                    pdf.set_font('Arial', '', 8)
                    pdf.cell(60, 3, 'Scan to visit our website', 0, 1, 'C')
                except Exception as e:
                    print(f"Error adding QR code: {e}")
            
            pdf.ln(10)
            
            # Subscription summary
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, f'Subscription History ({len(subscriptions_data)} subscriptions):', 0, 1)
            pdf.ln(5)
            
            # Table header
            pdf.set_font('Arial', 'B', 10)
            pdf.set_fill_color(230, 230, 230)
            
            # Column widths
            col_widths = [15, 45, 30, 25, 25, 20, 30]  # Adjusted for Receipt column
            headers = ['S.No', 'Receipt No.', 'Timeslot', 'Seat', 'Duration', 'Amount', 'Status']
            
            # Print headers
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 8, header, 1, 0, 'C', True)
            pdf.ln()
            
            # Table data
            pdf.set_font('Arial', '', 9)
            total_amount = 0
            active_count = 0
            expired_count = 0
            
            for i, sub in enumerate(subscriptions_data, 1):
                # Alternate row colors
                if i % 2 == 0:
                    pdf.set_fill_color(245, 245, 245)
                else:
                    pdf.set_fill_color(255, 255, 255)
                
                # Calculate duration in months
                from datetime import datetime as dt
                start = dt.strptime(sub['start_date'], '%Y-%m-%d')
                end = dt.strptime(sub['end_date'], '%Y-%m-%d')
                duration_days = (end - start).days + 1
                duration_months = round(duration_days / 30.0, 1)
                
                # Status
                today = dt.now().date()
                end_date = dt.strptime(sub['end_date'], '%Y-%m-%d').date()
                status = 'Active' if end_date >= today else 'Expired'
                
                if status == 'Active':
                    active_count += 1
                else:
                    expired_count += 1
                
                total_amount += float(sub['amount_paid'])
                
                # Data for each column
                row_data = [
                    str(i),
                    sub['receipt_number'][:12] + '...' if len(sub['receipt_number']) > 15 else sub['receipt_number'],
                    sub['timeslot_name'][:25] + '...' if len(sub['timeslot_name']) > 28 else sub['timeslot_name'],
                    str(sub['seat_number']),
                    f"{duration_months}m",
                    f"{DEFAULT_CURRENCY}{sub['amount_paid']:.0f}",
                    status
                ]
                
                # Print row
                for j, data in enumerate(row_data):
                    pdf.cell(col_widths[j], 8, data, 1, 0, 'C', True)
                pdf.ln()
            
            pdf.ln(5)
            
            # Summary section
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Summary:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(0, 8, f"Total Subscriptions: {len(subscriptions_data)}", 0, 1)
            pdf.cell(0, 8, f"Active Subscriptions: {active_count}", 0, 1)
            pdf.cell(0, 8, f"Expired Subscriptions: {expired_count}", 0, 1)
            pdf.cell(0, 8, f"Total Amount Paid: {DEFAULT_CURRENCY}{total_amount:.2f}", 0, 1)
            
            # Current active subscription details (if any)
            current_subscriptions = [sub for sub in subscriptions_data if sub.get('status') == 'Active' or 
                                   (dt.strptime(sub['end_date'], '%Y-%m-%d').date() >= dt.now().date())]
            
            if current_subscriptions:
                pdf.ln(8)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, 'Current Active Subscription(s):', 0, 1)
                pdf.set_font('Arial', '', 11)
                
                for sub in current_subscriptions:
                    pdf.cell(0, 6, f"- Seat {sub['seat_number']} - {sub['timeslot_name']} (Valid till {sub['end_date']})", 0, 1)
            
            pdf.ln(10)
            
            # Footer
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 6, f"This is a computer-generated receipt from {LIBRARY_NAME}", 0, 1, 'C')
            pdf.cell(0, 6, f"Generated on {datetime.now().strftime('%d/%m/%Y at %H:%M')}", 0, 1, 'C')
            pdf.ln(5)
            pdf.cell(0, 6, "Thank you for choosing our library services!", 0, 1, 'C')
            
            # Save PDF
            pdf.output(filepath)
            
            return True, filepath
            
        except Exception as e:
            return False, f"Error generating comprehensive receipt: {str(e)}"


# Alias for backward compatibility
ReceiptGenerator = PDFGenerator
