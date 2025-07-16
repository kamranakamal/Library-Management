"""
WhatsApp automation utilities
"""

import time
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from config.settings import WHATSAPP_WEB_URL, WHATSAPP_DELAY


class WhatsAppAutomation:
    """WhatsApp Web automation for sending messages"""
    
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
    
    def initialize_driver(self, headless=False):
        """Initialize Chrome WebDriver"""
        try:
            # Check if Chrome is installed
            chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium-browser',
                '/usr/bin/chromium',
                '/snap/bin/chromium'
            ]
            
            chrome_binary = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_binary = path
                    break
            
            if not chrome_binary:
                return False, "Chrome browser not found. Please install Google Chrome or Chromium."
            
            chrome_options = Options()
            chrome_options.binary_location = chrome_binary
            chrome_options.add_argument("--user-data-dir=./whatsapp_session")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            if headless:
                chrome_options.add_argument("--headless")
            
            # Use webdriver-manager to handle ChromeDriver
            try:
                service = webdriver.chrome.service.Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                return False, f"Failed to setup ChromeDriver: {str(e)}. Please install Google Chrome."
            
            # Execute script to avoid detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True, "Driver initialized successfully"
        
        except Exception as e:
            return False, f"Failed to initialize driver: {str(e)}. Make sure Chrome browser is installed."
    
    def login_to_whatsapp(self):
        """Login to WhatsApp Web"""
        try:
            if not self.driver:
                success, message = self.initialize_driver()
                if not success:
                    return False, message
            
            self.driver.get(WHATSAPP_WEB_URL)
            
            # Wait for QR code or main page to load
            wait = WebDriverWait(self.driver, 60)
            
            try:
                # Check if already logged in
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]')))
                self.is_logged_in = True
                return True, "Already logged in to WhatsApp Web"
            
            except TimeoutException:
                # QR code is present, need to scan
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//canvas')))
                    return False, "Please scan the QR code to login to WhatsApp Web"
                except TimeoutException:
                    return False, "Failed to load WhatsApp Web page"
        
        except Exception as e:
            return False, f"Login failed: {str(e)}"
    
    def wait_for_login(self, timeout=120):
        """Wait for user to complete QR code scan"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]')))
            self.is_logged_in = True
            return True, "Successfully logged in to WhatsApp Web"
        
        except TimeoutException:
            return False, "Login timeout. Please try again."
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def send_message(self, phone_number, message):
        """Send message to a phone number"""
        try:
            if not self.is_logged_in:
                return False, "Not logged in to WhatsApp Web"
            
            # Clean phone number (remove +, spaces, etc.)
            clean_number = re.sub(r'[^\d]', '', phone_number)
            
            # Open chat using WhatsApp Web URL
            chat_url = f"https://web.whatsapp.com/send?phone={clean_number}"
            self.driver.get(chat_url)
            
            # Wait for chat to load
            wait = WebDriverWait(self.driver, 30)
            
            try:
                # Wait for the message input box
                message_box = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="conversation-compose-box-input"]'))
                )
                
                # Click on message box and send message
                message_box.click()
                message_box.send_keys(message)
                message_box.send_keys(Keys.ENTER)
                
                # Add delay to avoid being detected as bot
                time.sleep(WHATSAPP_DELAY)
                
                return True, "Message sent successfully"
            
            except TimeoutException:
                # Try alternative method - check if number is invalid
                try:
                    self.driver.find_element(By.XPATH, '//*[contains(text(), "Phone number shared via url is invalid")]')
                    return False, f"Invalid phone number: {phone_number}"
                except Exception:
                    return False, f"Failed to send message to {phone_number}"
        
        except Exception as e:
            return False, f"Error sending message: {str(e)}"
    
    def send_bulk_messages(self, contacts_messages):
        """Send messages to multiple contacts"""
        results = []
        
        for contact in contacts_messages:
            phone_number = contact['phone']
            message = contact['message']
            name = contact.get('name', phone_number)
            
            success, result_message = self.send_message(phone_number, message)
            
            results.append({
                'name': name,
                'phone': phone_number,
                'success': success,
                'message': result_message
            })
            
            # Add delay between messages to avoid spam detection
            time.sleep(WHATSAPP_DELAY * 2)
        
        return results
    
    def send_subscription_reminders(self, expiring_subscriptions):
        """Send subscription expiry reminders"""
        messages = []
        
        for subscription in expiring_subscriptions:
            message = f"""
Hello {subscription['student_name']}!

This is a reminder that your library subscription is expiring soon.

Details:
- Seat Number: {subscription['seat_number']}
- Timeslot: {subscription['timeslot_name']}
- Expiry Date: {subscription['end_date']}

Please visit the library to renew your subscription.

Thank you!
Library Management
            """.strip()
            
            messages.append({
                'name': subscription['student_name'],
                'phone': subscription['mobile_number'],
                'message': message
            })
        
        return self.send_bulk_messages(messages)
    
    def send_overdue_book_reminders(self, overdue_borrowings):
        """Send overdue book return reminders"""
        messages = []
        
        for borrowing in overdue_borrowings:
            message = f"""
Hello {borrowing['student_name']}!

This is a reminder that you have an overdue book.

Book Details:
- Title: {borrowing['book_title']}
- Author: {borrowing['book_author']}
- Due Date: {borrowing['due_date']}
- Fine Amount: ₹{borrowing['fine_amount']}

Please return the book as soon as possible to avoid additional charges.

Thank you!
Library Management
            """.strip()
            
            messages.append({
                'name': borrowing['student_name'],
                'phone': borrowing['mobile_number'],
                'message': message
            })
        
        return self.send_bulk_messages(messages)
    
    def close_driver(self):
        """Close the WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.is_logged_in = False
            return True, "Driver closed successfully"
        except Exception as e:
            return False, f"Error closing driver: {str(e)}"
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
