"""
PDF receipt generation utilities
"""

import os
from datetime import datetime
from fpdf import FPDF
from config.settings import RECEIPTS_DIR, DEFAULT_CURRENCY, APP_NAME


class ReceiptGenerator:
    """Generate PDF receipts for subscriptions"""
    
    def __init__(self):
        self.ensure_receipts_directory()
    
    def ensure_receipts_directory(self):
        """Ensure receipts directory exists"""
        if not os.path.exists(RECEIPTS_DIR):
            os.makedirs(RECEIPTS_DIR)
    
    def generate_subscription_receipt(self, subscription_data):
        """Generate PDF receipt for subscription"""
        try:
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            
            # Header
            pdf.cell(0, 10, APP_NAME, 0, 1, 'C')
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
            
            pdf.cell(0, 8, f"Name: {subscription_data['student_name']}", 0, 1)
            pdf.cell(0, 8, f"Father's Name: {subscription_data['father_name']}", 0, 1)
            pdf.cell(0, 8, f"Mobile: {subscription_data['mobile_number']}", 0, 1)
            
            if subscription_data.get('aadhaar_number'):
                pdf.cell(0, 8, f"Aadhaar: {subscription_data['aadhaar_number']}", 0, 1)
            
            pdf.ln(5)
            
            # Subscription details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Subscription Details:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(0, 8, f"Seat Number: {subscription_data['seat_id']}", 0, 1)
            pdf.cell(0, 8, f"Timeslot: {subscription_data['timeslot_name']}", 0, 1)
            pdf.cell(0, 8, f"Duration: {subscription_data['start_date']} to {subscription_data['end_date']}", 0, 1)
            
            if subscription_data.get('locker_number'):
                pdf.cell(0, 8, f"Locker Number: {subscription_data['locker_number']}", 0, 1)
            
            pdf.ln(5)
            
            # Payment details
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'Payment Details:', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            pdf.cell(0, 8, f"Amount Paid: {DEFAULT_CURRENCY}{subscription_data['amount_paid']}", 0, 1)
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
            filename = f"receipt_{subscription_data['receipt_number']}.pdf"
            filepath = os.path.join(RECEIPTS_DIR, filename)
            pdf.output(filepath)
            
            return True, filepath
            
        except Exception as e:
            return False, f"Error generating receipt: {str(e)}"
    
    def generate_renewal_receipt(self, renewal_data):
        """Generate PDF receipt for subscription renewal"""
        try:
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            
            # Header
            pdf.cell(0, 10, APP_NAME, 0, 1, 'C')
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
            filename = f"renewal_{renewal_data['receipt_number']}.pdf"
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
            pdf.cell(0, 10, APP_NAME, 0, 1, 'C')
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
