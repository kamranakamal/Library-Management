"""
WhatsApp automation utilities
"""

import time
import re
import os
import platform
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from config.settings import (WHATSAPP_WEB_URL, WHATSAPP_DELAY, LIBRARY_NAME, 
                           LIBRARY_PHONE, LIBRARY_EMAIL, LIBRARY_ADDRESS)


class WhatsAppAutomation:
    """WhatsApp Web automation for sending messages"""
    
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
    
    def find_chrome_executable(self):
        """Find Chrome executable on different operating systems"""
        system = platform.system()
        
        if system == "Windows":
            # Windows Chrome paths
            chrome_paths = [
                os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome\Application\chrome.exe"),
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
        elif system == "Darwin":  # macOS
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ]
        else:  # Linux (including Fedora)
            chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium-browser',
                '/usr/bin/chromium',
                '/snap/bin/chromium',
                '/usr/bin/chrome',
                '/opt/google/chrome/chrome',
                '/usr/local/bin/chrome',
                '/usr/local/bin/google-chrome',
                '/usr/bin/google-chrome-beta',
                '/usr/bin/google-chrome-unstable',
                '/var/lib/flatpak/app/com.google.Chrome/current/active/export/bin/com.google.Chrome',
                '/home/.local/share/flatpak/app/com.google.Chrome/current/active/export/bin/com.google.Chrome'
            ]
        
        # Check each path
        for path in chrome_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        # Try to find Chrome using 'which' command on Unix-like systems
        if system != "Windows":
            try:
                result = subprocess.run(['which', 'google-chrome'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    chrome_path = result.stdout.strip()
                    if os.path.exists(chrome_path):
                        return chrome_path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Try chromium as fallback
            try:
                result = subprocess.run(['which', 'chromium'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    chrome_path = result.stdout.strip()
                    if os.path.exists(chrome_path):
                        return chrome_path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        return None
    
    def get_chrome_install_instructions(self):
        """Get Chrome installation instructions for current OS"""
        system = platform.system()
        
        if system == "Windows":
            return ("Please install Google Chrome from: https://www.google.com/chrome/\n"
                   "Or install via winget: winget install Google.Chrome")
        elif system == "Darwin":
            return ("Please install Google Chrome from: https://www.google.com/chrome/\n"
                   "Or install via Homebrew: brew install --cask google-chrome")
        else:  # Linux
            distro_info = ""
            try:
                # Try to detect Linux distribution
                with open('/etc/os-release', 'r') as f:
                    os_release = f.read()
                if 'fedora' in os_release.lower():
                    distro_info = ("Fedora: sudo dnf install google-chrome-stable\n"
                                 "Or: sudo dnf install chromium")
                elif 'ubuntu' in os_release.lower() or 'debian' in os_release.lower():
                    distro_info = ("Ubuntu/Debian: sudo apt update && sudo apt install google-chrome-stable\n"
                                 "Or: sudo apt install chromium-browser")
                elif 'arch' in os_release.lower():
                    distro_info = ("Arch: sudo pacman -S google-chrome\n"
                                 "Or: sudo pacman -S chromium")
            except:
                pass
            
            return (f"Please install Google Chrome or Chromium browser.\n"
                   f"{distro_info}\n"
                   f"Universal: Download from https://www.google.com/chrome/")

    def initialize_driver(self, headless=False):
        """Initialize Chrome WebDriver"""
        try:
            # Find Chrome executable
            chrome_binary = self.find_chrome_executable()
            
            if not chrome_binary:
                install_instructions = self.get_chrome_install_instructions()
                return False, f"Chrome browser not found.\n\n{install_instructions}"
            
            print(f"Found Chrome at: {chrome_binary}")
            
            chrome_options = Options()
            # For Flatpak Chrome, we need to set the binary path correctly
            if chrome_binary.startswith('/var/lib/flatpak/'):
                chrome_options.binary_location = chrome_binary
            
            # User data directory for persistent session
            chrome_options.add_argument("--user-data-dir=./whatsapp_session")
            
            # Anti-detection options
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Stability and security options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            # Performance options
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins-discovery")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # Window and display options
            chrome_options.add_argument("--window-size=1200,800")
            chrome_options.add_argument("--start-maximized")
            
            if headless:
                chrome_options.add_argument("--headless")
            else:
                # Ensure window is visible when not headless
                chrome_options.add_argument("--disable-background-mode")
            
            # Use webdriver-manager to handle ChromeDriver
            try:
                print("Initializing ChromeDriver...")
                service = webdriver.chrome.service.Service(ChromeDriverManager().install())
                print("Creating Chrome browser instance...")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Execute script to avoid detection
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("ChromeDriver initialized successfully!")
                
                return True, f"Driver initialized successfully using Chrome at: {chrome_binary}"
                
            except Exception as e:
                # For Flatpak Chrome, don't try system ChromeDriver as it's incompatible
                if chrome_binary.startswith('/var/lib/flatpak/'):
                    return False, (f"ChromeDriver initialization failed with Flatpak Chrome.\n"
                                 f"Error: {str(e)}\n\n"
                                 f"Possible solutions:\n"
                                 f"1. Install Chrome from official .rpm package instead of Flatpak\n"
                                 f"2. Or try: pip install --upgrade webdriver-manager selenium\n"
                                 f"3. Install system ChromeDriver: sudo dnf install chromedriver\n"
                                 f"   (may require non-Flatpak Chrome)")
                
                # Fallback: try system chromedriver for non-Flatpak Chrome
                print(f"WebDriver Manager failed: {str(e)}")
                print("Trying system ChromeDriver as fallback...")
                error_msg = f"Failed to setup ChromeDriver: {str(e)}"
                
                # Try to find system chromedriver
                system_drivers = [
                    '/usr/bin/chromedriver',
                    '/usr/local/bin/chromedriver',
                    '/snap/bin/chromedriver'
                ]
                
                for driver_path in system_drivers:
                    if os.path.exists(driver_path):
                        try:
                            print(f"Trying system ChromeDriver at: {driver_path}")
                            service = webdriver.chrome.service.Service(driver_path)
                            self.driver = webdriver.Chrome(service=service, options=chrome_options)
                            
                            # Execute script to avoid detection
                            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                            print("System ChromeDriver initialized successfully!")
                            
                            return True, f"Driver initialized using system ChromeDriver at: {driver_path}"
                        except Exception as sys_e:
                            print(f"System ChromeDriver failed: {sys_e}")
                            continue
                
                # If all fails, provide comprehensive error message
                return False, (f"{error_msg}\n\n"
                             f"Possible solutions:\n"
                             f"1. Update Chrome browser to latest version\n"
                             f"2. Install system ChromeDriver: sudo dnf install chromedriver\n"
                             f"3. Or try: pip install --upgrade webdriver-manager selenium\n"
                             f"4. Manual download from: https://chromedriver.chromium.org/")
        
        except Exception as e:
            return False, f"Failed to initialize driver: {str(e)}\n\n{self.get_chrome_install_instructions()}"

    def login_to_whatsapp(self):
        """Login to WhatsApp Web"""
        try:
            if not self.driver:
                print("Driver not initialized. Initializing...")
                success, message = self.initialize_driver()
                if not success:
                    return False, message
            
            print("Opening WhatsApp Web...")
            self.driver.get(WHATSAPP_WEB_URL)
            print(f"Navigated to: {WHATSAPP_WEB_URL}")
            
            # Wait for page to load
            print("Waiting for WhatsApp Web to load...")
            wait = WebDriverWait(self.driver, 60)
            
            try:
                # Check if already logged in
                print("Checking if already logged in...")
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]')))
                self.is_logged_in = True
                print("Already logged in to WhatsApp Web!")
                return True, "Already logged in to WhatsApp Web"
            
            except TimeoutException:
                # QR code is present, need to scan
                print("QR code should be visible. Waiting for QR code element...")
                try:
                    # Wait for QR code canvas or container
                    qr_element = wait.until(EC.any_of(
                        EC.presence_of_element_located((By.XPATH, '//canvas')),
                        EC.presence_of_element_located((By.XPATH, '//div[contains(@data-testid, "qr")]')),
                        EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "scan")]'))
                    ))
                    print("QR code is now visible on screen")
                    return False, "Please scan the QR code to login to WhatsApp Web"
                except TimeoutException:
                    print("Failed to load WhatsApp Web page or QR code")
                    # Take a screenshot for debugging
                    try:
                        self.driver.save_screenshot("whatsapp_error.png")
                        print("Screenshot saved as whatsapp_error.png")
                    except:
                        pass
                    return False, "Failed to load WhatsApp Web page. Please check your internet connection."
        
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False, f"Login failed: {str(e)}"
    
    def wait_for_login(self, timeout=120):
        """Wait for user to complete QR code scan"""
        try:
            print(f"Waiting for login completion (timeout: {timeout} seconds)...")
            wait = WebDriverWait(self.driver, timeout)
            
            # Show progress every 10 seconds
            for i in range(0, timeout, 10):
                try:
                    # Try to find chat list (indicates successful login)
                    wait_short = WebDriverWait(self.driver, 10)
                    wait_short.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]')))
                    self.is_logged_in = True
                    print("Login successful!")
                    return True, "Successfully logged in to WhatsApp Web"
                except TimeoutException:
                    remaining = timeout - i - 10
                    if remaining > 0:
                        print(f"Still waiting for QR code scan... ({remaining} seconds remaining)")
                    continue
            
            # Final timeout
            print("Login timeout reached")
            return False, "Login timeout. Please try again."
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False, f"Login error: {str(e)}"
    
    def send_message(self, phone_number, message):
        """Send message to a phone number"""
        try:
            if not self.is_logged_in:
                return False, "Not logged in to WhatsApp Web"
            
            print(f"Sending message to {phone_number}...")
            
            # Clean phone number (remove +, spaces, etc.)
            clean_number = re.sub(r'[^\d]', '', phone_number)
            
            # Open chat using WhatsApp Web URL
            chat_url = f"https://web.whatsapp.com/send?phone={clean_number}"
            print(f"Opening chat: {chat_url}")
            self.driver.get(chat_url)
            
            # Wait for chat to load
            wait = WebDriverWait(self.driver, 30)
            
            try:
                print("Waiting for message input box...")
                # Wait for the message input box
                message_box = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="conversation-compose-box-input"]'))
                )
                
                print("Sending message...")
                # Click on message box and send message
                message_box.click()
                message_box.send_keys(message)
                message_box.send_keys(Keys.ENTER)
                
                # Add delay to avoid being detected as bot
                time.sleep(WHATSAPP_DELAY)
                print("Message sent successfully!")
                
                return True, "Message sent successfully"
            
            except TimeoutException:
                # Try alternative method - check if number is invalid
                try:
                    self.driver.find_element(By.XPATH, '//*[contains(text(), "Phone number shared via url is invalid")]')
                    print(f"Invalid phone number detected: {phone_number}")
                    return False, f"Invalid phone number: {phone_number}"
                except Exception:
                    print(f"Failed to load chat for {phone_number}")
                    return False, f"Failed to send message to {phone_number}"
        
        except Exception as e:
            print(f"Error sending message: {str(e)}")
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

This is a reminder from {LIBRARY_NAME} that your library subscription is expiring soon.

Details:
- Seat Number: {subscription['seat_number']}
- Timeslot: {subscription['timeslot_name']}
- Expiry Date: {subscription['end_date']}

Please visit us to renew your subscription.

{LIBRARY_NAME}
📍 {LIBRARY_ADDRESS}
📞 {LIBRARY_PHONE}
📧 {LIBRARY_EMAIL}

Thank you for choosing {LIBRARY_NAME}!
            """.strip()
            
            messages.append({
                'name': subscription['student_name'],
                'phone': subscription['mobile_number'],
                'message': message
            })
        
        return self.send_bulk_messages(messages)
    
    def send_subscription_cancellations(self, expired_subscriptions):
        """Send subscription cancellation messages to expired students"""
        messages = []
        
        for subscription in expired_subscriptions:
            message = f"""
Dear {subscription['student_name']},

We regret to inform you that your library subscription has been cancelled due to expiration.

📋 Expired Subscription Details:
- Seat Number: {subscription['seat_number']}
- Timeslot: {subscription['timeslot_name']}
- Expiry Date: {subscription['end_date']}

🔄 For Readmission:
If you wish to continue using our library services, please contact us immediately for readmission.

📞 Contact for Readmission:
WhatsApp: {LIBRARY_PHONE}
Visit: {LIBRARY_ADDRESS}
Email: {LIBRARY_EMAIL}

We understand that circumstances can cause delays, and we're here to help you get back on track with your studies.

💬 Quick Readmission:
Simply reply to this message or call us at {LIBRARY_PHONE} to discuss readmission options and available seats.

Thank you for being part of {LIBRARY_NAME}. We hope to welcome you back soon!

Best regards,
{LIBRARY_NAME} Team
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

This is a reminder from {LIBRARY_NAME} that you have an overdue book.

Book Details:
- Title: {borrowing['book_title']}
- Author: {borrowing['book_author']}
- Due Date: {borrowing['due_date']}
- Fine Amount: Rs. {borrowing['fine_amount']}

Please return the book as soon as possible to avoid additional charges.

{LIBRARY_NAME}
📍 {LIBRARY_ADDRESS}
📞 {LIBRARY_PHONE}
📧 {LIBRARY_EMAIL}

Thank you for choosing {LIBRARY_NAME}!
            """.strip()
            
            messages.append({
                'name': borrowing['student_name'],
                'phone': borrowing['mobile_number'],
                'message': message
            })
        
        return self.send_bulk_messages(messages)
    
    def send_subscription_confirmation(self, subscription_data):
        """Send subscription confirmation message"""
        message = f"""
🎉 Welcome to {LIBRARY_NAME}! 🎉

Dear {subscription_data['student_name']},

Your subscription has been successfully confirmed!

📋 Subscription Details:
- Receipt No: {subscription_data['receipt_number']}
- Seat Number: {subscription_data['seat_id']}
- Timeslot: {subscription_data['timeslot_name']}
- Duration: {subscription_data['start_date']} to {subscription_data['end_date']}
- Amount Paid: Rs. {subscription_data['amount_paid']}

🏢 {LIBRARY_NAME}
📍 {LIBRARY_ADDRESS}
📞 {LIBRARY_PHONE}
📧 {LIBRARY_EMAIL}

Thank you for choosing {LIBRARY_NAME}! We wish you all the best in your studies.

Best regards,
{LIBRARY_NAME} Team
        """.strip()
        
        return self.send_message(subscription_data['mobile_number'], message)
    
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
