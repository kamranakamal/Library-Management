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
            chrome_options.binary_location = chrome_binary
            chrome_options.add_argument("--user-data-dir=./whatsapp_session")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Additional options for better compatibility
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins-discovery")
            chrome_options.add_argument("--disable-default-apps")
            
            if headless:
                chrome_options.add_argument("--headless")
            
            # Use webdriver-manager to handle ChromeDriver
            try:
                service = webdriver.chrome.service.Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Execute script to avoid detection
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                return True, f"Driver initialized successfully using Chrome at: {chrome_binary}"
                
            except Exception as e:
                return False, f"Failed to setup ChromeDriver: {str(e)}\n\nTry installing ChromeDriver manually or updating Chrome browser."
        
        except Exception as e:
            return False, f"Failed to initialize driver: {str(e)}\n\n{self.get_chrome_install_instructions()}"
    
    def test_chrome_installation(self):
        """Test Chrome installation and provide diagnostic information"""
        system = platform.system()
        chrome_binary = self.find_chrome_executable()
        
        result = {
            'system': system,
            'chrome_found': chrome_binary is not None,
            'chrome_path': chrome_binary,
            'diagnostics': []
        }
        
        if chrome_binary:
            result['diagnostics'].append(f"✓ Chrome found at: {chrome_binary}")
            
            # Test if Chrome can be executed
            try:
                if system == "Windows":
                    test_cmd = [chrome_binary, '--version']
                else:
                    test_cmd = [chrome_binary, '--version']
                
                proc_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
                if proc_result.returncode == 0:
                    version = proc_result.stdout.strip()
                    result['diagnostics'].append(f"✓ Chrome executable works: {version}")
                    result['chrome_version'] = version
                else:
                    result['diagnostics'].append(f"✗ Chrome executable failed: {proc_result.stderr}")
            except Exception as e:
                result['diagnostics'].append(f"✗ Failed to test Chrome executable: {str(e)}")
        else:
            result['diagnostics'].append("✗ Chrome not found")
            result['diagnostics'].append(f"Installation instructions:\n{self.get_chrome_install_instructions()}")
        
        # Test ChromeDriver
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver_path = ChromeDriverManager().install()
            result['diagnostics'].append(f"✓ ChromeDriver available at: {driver_path}")
            result['chromedriver_found'] = True
        except Exception as e:
            result['diagnostics'].append(f"✗ ChromeDriver issue: {str(e)}")
            result['chromedriver_found'] = False
        
        return result

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
