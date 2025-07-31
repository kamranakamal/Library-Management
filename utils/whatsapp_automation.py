"""
WhatsApp automation utilities
"""

import time
import re
import os
import platform
import subprocess
import unicodedata
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
        self._status_check_lock = False  # Simple lock to prevent concurrent status checks
    
    def get_session_directory(self):
        """Get appropriate session directory for the platform"""
        import tempfile
        import platform
        
        if platform.system() == "Windows":
            # Use temp directory on Windows to avoid permission issues
            temp_dir = tempfile.gettempdir()
            session_dir = os.path.join(temp_dir, "whatsapp_session")
        else:
            # Use local directory on Linux/Mac
            session_dir = os.path.join(os.getcwd(), "whatsapp_session")
        
        # Create directory if it doesn't exist
        try:
            os.makedirs(session_dir, exist_ok=True)
            # Test write access
            test_file = os.path.join(session_dir, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            print(f"⚠️ Warning: Session directory issue: {e}")
            # Fallback to temp directory
            session_dir = os.path.join(tempfile.gettempdir(), f"whatsapp_session_{os.getpid()}")
            os.makedirs(session_dir, exist_ok=True)
        
        return session_dir

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
                # Additional Windows 11 paths
                os.path.expandvars(r"%USERPROFILE%\AppData\Local\Google\Chrome SxS\Application\chrome.exe"),
                os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome Beta\Application\chrome.exe"),
                os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome Beta\Application\chrome.exe"),
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
            print("=== WhatsApp Driver Initialization ===")
            
            # Find Chrome executable
            print("Looking for Chrome browser...")
            chrome_binary = self.find_chrome_executable()
            
            if not chrome_binary:
                install_instructions = self.get_chrome_install_instructions()
                error_msg = f"Chrome browser not found.\n\n{install_instructions}"
                print(f"ERROR: {error_msg}")
                return False, error_msg
            
            print(f"✅ Found Chrome at: {chrome_binary}")
            
            chrome_options = Options()
            # For Flatpak Chrome, we need to set the binary path correctly
            if chrome_binary.startswith('/var/lib/flatpak/'):
                chrome_options.binary_location = chrome_binary
                print("📦 Using Flatpak Chrome")
            
            # User data directory for persistent session
            import tempfile
            session_dir = self.get_session_directory()
            chrome_options.add_argument(f"--user-data-dir={session_dir}")
            print(f"📁 Session directory: {session_dir}")
            
            # Windows-specific fixes
            if platform.system() == "Windows":
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-first-run")
                chrome_options.add_argument("--disable-default-apps")
                chrome_options.add_argument("--disable-background-mode")
            
            # Anti-detection options
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Stability and security options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-gpu-sandbox")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-field-trial-config")
            chrome_options.add_argument("--disable-back-forward-cache")
            chrome_options.add_argument("--disable-hang-monitor")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_argument("--disable-prompt-on-repost")
            chrome_options.add_argument("--disable-client-side-phishing-detection")
            chrome_options.add_argument("--disable-component-update")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-domain-reliability")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-login-animations")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-password-generation")
            chrome_options.add_argument("--disable-permissions-api")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-print-preview")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--memory-pressure-off")
            chrome_options.add_argument("--max_old_space_size=4096")
            
            # Keep alive options
            chrome_options.add_argument("--keep-alive-for-test")
            chrome_options.add_argument("--disable-background-mode")
            
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
            
            # Prevent browser from closing unexpectedly
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            if headless:
                chrome_options.add_argument("--headless")
                print("🔧 Running in headless mode")
            else:
                # Ensure window is visible when not headless
                chrome_options.add_argument("--disable-background-mode")
                chrome_options.add_argument("--no-first-run")
                chrome_options.add_argument("--no-default-browser-check")
                print("🔧 Running with visible window")
            
            # Use webdriver-manager to handle ChromeDriver
            try:
                print("🔄 Setting up ChromeDriver using WebDriver Manager...")
                service = webdriver.chrome.service.Service(ChromeDriverManager().install())
                print("🚀 Creating Chrome browser instance...")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Execute script to avoid detection
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("✅ ChromeDriver initialized successfully!")
                
                return True, f"Driver initialized successfully using Chrome at: {chrome_binary}"
                
            except Exception as e:
                print(f"❌ WebDriver Manager failed: {str(e)}")
                
                # For Flatpak Chrome, don't try system ChromeDriver as it's incompatible
                if chrome_binary.startswith('/var/lib/flatpak/'):
                    error_msg = (f"ChromeDriver initialization failed with Flatpak Chrome.\n"
                                 f"Error: {str(e)}\n\n"
                                 f"Possible solutions:\n"
                                 f"1. Install Chrome from official .rpm package instead of Flatpak\n"
                                 f"2. Or try: pip install --upgrade webdriver-manager selenium\n"
                                 f"3. Install system ChromeDriver: sudo dnf install chromedriver\n"
                                 f"   (may require non-Flatpak Chrome)")
                    print(f"ERROR: {error_msg}")
                    return False, error_msg
                
                # Fallback: try system chromedriver for non-Flatpak Chrome
                print("🔄 Trying system ChromeDriver as fallback...")
                
                # Try to find system chromedriver
                system_drivers = [
                    '/usr/bin/chromedriver',
                    '/usr/local/bin/chromedriver',
                    '/snap/bin/chromedriver'
                ]
                
                for driver_path in system_drivers:
                    if os.path.exists(driver_path):
                        try:
                            print(f"🔄 Trying system ChromeDriver at: {driver_path}")
                            service = webdriver.chrome.service.Service(driver_path)
                            self.driver = webdriver.Chrome(service=service, options=chrome_options)
                            
                            # Execute script to avoid detection
                            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                            print("✅ System ChromeDriver initialized successfully!")
                            
                            return True, f"Driver initialized using system ChromeDriver at: {driver_path}"
                        except Exception as sys_e:
                            print(f"❌ System ChromeDriver failed: {sys_e}")
                            continue
                
                # If all fails, provide comprehensive error message
                error_msg = (f"All ChromeDriver initialization attempts failed.\n\n"
                             f"Original error: {str(e)}\n\n"
                             f"Possible solutions:\n"
                             f"1. Update Chrome browser to latest version\n"
                             f"2. Install system ChromeDriver: sudo dnf install chromedriver\n"
                             f"3. Or try: pip install --upgrade webdriver-manager selenium\n"
                             f"4. Manual download from: https://chromedriver.chromium.org/")
                print(f"ERROR: {error_msg}")
                return False, error_msg
        
        except Exception as e:
            error_msg = f"Failed to initialize driver: {str(e)}\n\n{self.get_chrome_install_instructions()}"
            print(f"ERROR: {error_msg}")
            return False, error_msg

    def login_to_whatsapp(self):
        """Login to WhatsApp Web"""
        try:
            if not self.driver:
                print("❌ Driver not initialized. Initializing...")
                success, message = self.initialize_driver()
                if not success:
                    return False, message
            
            print("🌐 Opening WhatsApp Web...")
            self.driver.get(WHATSAPP_WEB_URL)
            print(f"✅ Navigated to: {WHATSAPP_WEB_URL}")
            
            # Wait for page to load
            print("⏳ Waiting for WhatsApp Web to load...")
            wait = WebDriverWait(self.driver, 60)
            
            # Wait for the page to fully load first
            import time
            time.sleep(3)
            
            try:
                print("🔍 Checking if already logged in...")
                
                # Use the comprehensive login status check method
                is_logged_in, status_message = self.check_login_status()
                
                if is_logged_in:
                    self.is_logged_in = True
                    print(f"✅ Already logged in! Status: {status_message}")
                    
                    # Additional wait for page stability if just logged in
                    if "may be loading" in status_message.lower() or "interface loading" in status_message.lower():
                        print("⏳ Waiting for interface to fully load...")
                        stable, stability_msg = self.wait_for_page_stability(timeout=15)
                        if stable:
                            print("✅ Interface fully loaded!")
                        else:
                            print(f"⚠️ Interface may still be loading: {stability_msg}")
                    
                    return True, "Already logged in to WhatsApp Web"
                
                print("📱 Not logged in yet, checking for QR code or login elements...")
                
            except Exception as e:
                print(f"⚠️ Error checking login status: {e}")
            
            try:
                # Check for QR code or login screen elements
                qr_selectors = [
                    '//canvas[@aria-label="Scan me!"]',  # QR code canvas with aria-label
                    '//canvas',  # Any canvas (likely QR code)
                    '//div[@data-testid="qr-canvas"]',  # QR canvas container
                    '//div[contains(@class, "qr")]',  # QR code container
                    '//div[contains(text(), "scan")]',  # Text mentioning scan
                    '//div[contains(text(), "phone")]',  # Text mentioning phone
                    '//div[contains(text(), "WhatsApp")]//canvas',  # Canvas within WhatsApp context
                    '//div[@role="img"]//canvas'  # Canvas with img role
                ]
                
                for selector in qr_selectors:
                    try:
                        wait_short = WebDriverWait(self.driver, 5)
                        qr_element = wait_short.until(EC.presence_of_element_located((By.XPATH, selector)))
                        if qr_element and qr_element.is_displayed():
                            print(f"✅ QR code found! (Selector: {selector})")
                            return False, "Please scan the QR code to login to WhatsApp Web"
                    except TimeoutException:
                        continue
                
                # If no QR code found, check what's on the page
                print("❓ No QR code found, checking page content...")
                try:
                    page_title = self.driver.title
                    current_url = self.driver.current_url
                    print(f"📄 Page title: {page_title}")
                    print(f"🔗 Current URL: {current_url}")
                    
                    # Check for any WhatsApp-related content
                    whatsapp_elements = self.driver.find_elements(By.XPATH, '//*[contains(text(), "WhatsApp")]')
                    print(f"🔍 Found {len(whatsapp_elements)} WhatsApp elements")
                    
                    # Check for loading states
                    loading_elements = self.driver.find_elements(By.XPATH, '//*[contains(@class, "loading") or contains(text(), "Loading") or contains(text(), "loading")]')
                    if loading_elements:
                        print("⏳ Page appears to be loading...")
                        return False, "WhatsApp Web is loading. Please wait and try again."
                    
                except Exception as e:
                    print(f"⚠️ Error checking page content: {e}")
                
                print("❌ Could not find QR code or determine page state")
                # Take a screenshot for debugging
                try:
                    screenshot_path = "whatsapp_debug.png"
                    self.driver.save_screenshot(screenshot_path)
                    print(f"📸 Debug screenshot saved as {screenshot_path}")
                except Exception as screenshot_error:
                    print(f"❌ Failed to save screenshot: {screenshot_error}")
                
                return False, "Could not find QR code. Please check the browser window and ensure WhatsApp Web loaded properly."
                
            except Exception as e:
                print(f"❌ Error looking for QR code: {e}")
                return False, f"Failed to load WhatsApp Web page properly: {str(e)}"
        
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False, f"Login failed: {str(e)}"
    
    def wait_for_login(self, timeout=120):
        """Wait for user to complete QR code scan"""
        try:
            print(f"⏳ Waiting for login completion (timeout: {timeout} seconds)...")
            
            import time
            start_time = time.time()
            
            # Show progress every 10 seconds
            while time.time() - start_time < timeout:
                try:
                    # Try multiple selectors for logged-in state
                    logged_in_selectors = [
                        '//div[@data-testid="chat-list"]',  # Main chat list
                        '//div[contains(@class, "chat-list")]',  # Alternative chat list
                        '//div[@data-testid="chatlist-header"]',  # Chat list header
                        '//span[@data-testid="default-user"]',  # User profile
                        '//div[@id="main"]',  # Main WhatsApp container
                        '//header[@data-testid="chatlist-header"]',  # Header with user info
                        '//div[contains(@class, "two") and contains(@class, "copyable")]',  # Two-pane layout
                        '//div[@role="application"]//div[contains(@class, "app")]'  # App container
                    ]
                    
                    for selector in logged_in_selectors:
                        try:
                            wait_short = WebDriverWait(self.driver, 2)
                            element = wait_short.until(EC.presence_of_element_located((By.XPATH, selector)))
                            if element and element.is_displayed():
                                print(f"✅ Login detected! (Found: {selector})")
                                
                                # Wait for page to fully stabilize after login
                                print("⏳ Waiting for WhatsApp Web to fully load...")
                                time.sleep(3)  # Initial wait
                                
                                # Use the new stability check method
                                stable, stability_msg = self.wait_for_page_stability(timeout=30)
                                
                                if stable:
                                    print("✅ WhatsApp Web is stable and ready!")
                                    self.is_logged_in = True
                                    return True, "Successfully logged in to WhatsApp Web"
                                else:
                                    print(f"⚠️ Page may not be fully stable: {stability_msg}")
                                    # Still consider login successful even if stability check failed
                                    self.is_logged_in = True
                                    return True, "Login detected - WhatsApp Web may still be loading"
                                
                        except TimeoutException:
                            continue
                    
                    # Still waiting, show progress
                    remaining = int(timeout - (time.time() - start_time))
                    if remaining > 0 and remaining % 10 == 0:  # Every 10 seconds
                        print(f"⏳ Still waiting for QR code scan... ({remaining} seconds remaining)")
                    
                    time.sleep(2)  # Wait 2 seconds before next check
                    
                except Exception as e:
                    print(f"⚠️ Error during login wait: {e}")
                    time.sleep(2)
                    continue
            
            # Final timeout
            print("⌛ Login timeout reached")
            return False, "Login timeout. Please try again."
            
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False, f"Login error: {str(e)}"
    
    def wait_for_page_stability(self, timeout=30, required_checks=3):
        """Wait for WhatsApp Web page to be stable after login"""
        try:
            print(f"⏳ Waiting for page stability (timeout: {timeout}s, checks: {required_checks})...")
            
            import time
            stable_count = 0
            start_time = time.time()
            
            # Elements that should be present and stable
            stability_selectors = [
                '//div[@data-testid="chat-list"]',
                '//div[@data-testid="chatlist-header"]',
                '//div[@data-testid="side"]',
            ]
            
            while time.time() - start_time < timeout:
                try:
                    # Check if the key elements are present and stable
                    elements_found = 0
                    
                    for selector in stability_selectors:
                        try:
                            element = self.driver.find_element(By.XPATH, selector)
                            if element.is_displayed() and element.size['height'] > 0:
                                elements_found += 1
                        except:
                            continue
                    
                    if elements_found >= 2:  # At least 2 key elements found
                        stable_count += 1
                        print(f"✓ Stability check {stable_count}/{required_checks} passed")
                        
                        if stable_count >= required_checks:
                            print("✅ Page is stable!")
                            return True, "Page is stable and ready"
                    else:
                        stable_count = 0  # Reset if not stable
                    
                    time.sleep(1)  # Wait 1 second between checks
                    
                except Exception as e:
                    print(f"⚠️ Stability check error: {e}")
                    stable_count = 0
                    time.sleep(1)
                    continue
            
            print("⚠️ Stability timeout reached")
            return False, "Page stability timeout"
            
        except Exception as e:
            print(f"❌ Stability check failed: {e}")
            return False, f"Stability check error: {str(e)}"
    
    def is_driver_valid(self):
        """Check if driver is still valid and responsive"""
        try:
            if not self.driver:
                return False
            
            # Simple test to see if driver is responsive
            title = self.driver.title
            return True
        except Exception as e:
            error_str = str(e).lower()
            if any(error in error_str for error in ["session deleted", "chrome not reachable", "connection refused", "no such session"]):
                return False
            return False
    
    def check_login_status(self):
        """Check if logged into WhatsApp Web with comprehensive detection"""
        # Simple lock to prevent concurrent status checks
        if self._status_check_lock:
            return self.is_logged_in, "Status check already in progress"
        
        self._status_check_lock = True
        
        try:
            return self._do_status_check()
        finally:
            self._status_check_lock = False
    
    def _do_status_check(self):
        """Internal status check implementation"""
        try:
            if not self.driver:
                return False, "No driver initialized"
            
            # Check if session is still active with multiple fallbacks
            try:
                current_url = self.driver.current_url
                if "web.whatsapp.com" not in current_url:
                    return False, f"Not on WhatsApp Web (URL: {current_url})"
            except Exception as e:
                if "session deleted" in str(e).lower() or "no such session" in str(e).lower():
                    return False, "Browser session ended"
                elif "chrome not reachable" in str(e).lower():
                    return False, "Chrome browser not reachable"
                else:
                    # Try to recover by checking if page is responsive
                    try:
                        # Check if we can get page title as a simple responsiveness test
                        title = self.driver.title
                        if not title:
                            return False, "Page not responding"
                        # If we got here, driver is responsive, continue with checks
                    except:
                        return False, f"Driver error: {str(e)}"
            
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            from selenium.common.exceptions import TimeoutException
            import time
            
            # Multiple selectors for logged-in state (WhatsApp Web 2024/2025)
            logged_in_selectors = [
                '//div[@data-testid="chat-list"]',  # Main chat list
                '//div[@data-testid="chatlist-header"]',  # Chat list header
                '//header[@data-testid="chatlist-header"]',  # Alternative header
                '//div[@data-testid="side"]',  # Sidebar
                '//div[contains(@class, "chat-list")]',  # Class-based selector
                '//div[@id="side"]',  # ID-based selector
                '//span[@data-testid="default-user"]',  # User profile
                '//div[@data-testid="conversations-list"]',  # Conversations list
                '//div[contains(@aria-label, "Chat list")]',  # Aria-label based
                '//div[@role="application"]//header',  # Header within app
                '//div[contains(@class, "app-wrapper")]//div[contains(@class, "chat")]',  # App wrapper with chat
                '//div[@role="main"]',  # Main content area
                '//div[contains(@class, "app")]//div[contains(@class, "two")]',  # Two-pane layout
            ]
            
            # Check for logged-in indicators with better error handling
            login_detected = False
            detected_selector = None
            
            for selector in logged_in_selectors:
                try:
                    wait = WebDriverWait(self.driver, 2)
                    element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    if element.is_displayed() and element.size['height'] > 0 and element.size['width'] > 0:
                        login_detected = True
                        detected_selector = selector
                        break
                except TimeoutException:
                    continue
                except Exception as e:
                    if "stale element" in str(e).lower():
                        # Page is changing, wait a bit and continue
                        time.sleep(1)
                        continue
                    else:
                        continue
            
            if login_detected:
                # Additional verification - check if we can find any interactive elements
                try:
                    # Look for elements that indicate the interface is fully loaded
                    interface_elements = [
                        '//div[@data-testid="chat-list-search"]',
                        '//div[@data-testid="search-input"]',
                        '//div[@contenteditable="true"]',
                        '//input[@type="text"]',
                        '//div[@role="textbox"]',
                        '//span[@data-testid="default-user"]',
                    ]
                    
                    interface_ready = False
                    for interface_selector in interface_elements:
                        try:
                            element = self.driver.find_element(By.XPATH, interface_selector)
                            if element.is_displayed():
                                interface_ready = True
                                break
                        except:
                            continue
                    
                    if interface_ready:
                        return True, f"Logged in and interface ready (found: {detected_selector})"
                    else:
                        # Logged in but interface might still be loading
                        return True, f"Logged in but interface loading (found: {detected_selector})"
                    
                except Exception as e:
                    # Login detected but may not be fully ready
                    return True, f"Logged in but may be loading (found: {detected_selector})"
            
            # Check for QR code (not logged in)
            qr_selectors = [
                '//canvas[@aria-label="Scan me!"]',  # QR canvas with aria-label
                '//canvas',  # Any canvas (usually QR)
                '//div[@data-testid="qr-canvas"]',  # QR canvas container
                '//div[contains(@class, "qr")]',  # QR container by class
                '//div[contains(text(), "scan")]',  # Text containing "scan"
                '//div[contains(text(), "phone")]',  # Text containing "phone"
                '//div[contains(text(), "WhatsApp")]//canvas',  # Canvas near WhatsApp text
                '//div[@data-testid="intro-componentqr"]',  # QR intro component
            ]
            
            for selector in qr_selectors:
                try:
                    wait = WebDriverWait(self.driver, 1)
                    element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    if element.is_displayed():
                        return False, f"QR code visible (found: {selector})"
                except TimeoutException:
                    continue
                except Exception as e:
                    continue
            
            # Check for loading state
            loading_selectors = [
                '//div[contains(@class, "landing")]',
                '//div[contains(@class, "intro")]',
                '//div[contains(text(), "Loading")]',
                '//div[contains(text(), "Connecting")]',
                '//div[contains(@class, "progress")]',
                '//div[contains(@class, "spinner")]',
                '//div[contains(@class, "loading")]',
            ]
            
            for selector in loading_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        return False, f"Page loading (found: {selector})"
                except:
                    continue
            
            # If we can't determine status clearly, try to analyze page content
            try:
                # Get page source and look for indicators
                page_source = self.driver.page_source.lower()
                
                # Check for positive indicators
                positive_indicators = ['chat-list', 'chatlist', 'conversation', 'message', 'contact']
                positive_count = sum(1 for indicator in positive_indicators if indicator in page_source)
                
                # Check for negative indicators  
                negative_indicators = ['qr', 'scan', 'loading', 'connecting']
                negative_count = sum(1 for indicator in negative_indicators if indicator in page_source)
                
                if positive_count >= 2:
                    return True, f"Likely logged in (found {positive_count} positive indicators in page source)"
                elif negative_count >= 2:
                    return False, f"Likely not logged in (found {negative_count} negative indicators in page source)"
                else:
                    # Try to get any visible text content as last resort
                    try:
                        body_elements = self.driver.find_elements(By.XPATH, '//body//*[text()]')
                        if len(body_elements) > 10:  # Page has content
                            return True, "Page has content - likely logged in"
                        else:
                            return False, "Page appears empty or loading"
                    except:
                        return False, "Cannot determine page state"
                        
            except Exception as e:
                return False, f"Cannot analyze page content: {str(e)}"
                
        except Exception as e:
            return False, f"Status check failed: {str(e)}"
    
    def wait_for_page_stability(self, timeout=30):
        """Wait for WhatsApp Web page to become stable after login"""
        try:
            print("⏳ Waiting for page to stabilize...")
            
            from selenium.webdriver.common.by import By
            import time
            
            start_time = time.time()
            consecutive_stable_checks = 0
            required_stable_checks = 3  # Need 3 consecutive stable checks
            
            while time.time() - start_time < timeout:
                try:
                    # Check if page is stable by looking for key elements
                    stable_elements = [
                        '//div[@data-testid="chat-list"]',
                        '//div[@data-testid="chatlist-header"]',
                        '//span[@data-testid="default-user"]',
                    ]
                    
                    stable_count = 0
                    for selector in stable_elements:
                        try:
                            element = self.driver.find_element(By.XPATH, selector)
                            if element and element.is_displayed() and element.size['height'] > 0:
                                stable_count += 1
                        except:
                            pass
                    
                    if stable_count >= 2:  # At least 2 stable elements found
                        consecutive_stable_checks += 1
                        print(f"🔍 Stability check {consecutive_stable_checks}/{required_stable_checks} passed")
                        
                        if consecutive_stable_checks >= required_stable_checks:
                            print("✅ Page is stable!")
                            return True, "Page is stable and ready"
                    else:
                        consecutive_stable_checks = 0  # Reset counter
                        print("⏳ Page still stabilizing...")
                    
                    time.sleep(2)  # Wait between checks
                    
                except Exception as e:
                    consecutive_stable_checks = 0  # Reset on error
                    print(f"⚠️ Stability check error: {e}")
                    time.sleep(2)
            
            # Timeout reached
            print("⌛ Stability timeout reached")
            return False, "Page stabilization timeout"
            
        except Exception as e:
            print(f"❌ Error waiting for stability: {e}")
            return False, f"Stability check failed: {str(e)}"

    def ensure_connection(self):
        """Ensure WhatsApp Web connection is stable"""
        try:
            print("🔍 Checking WhatsApp Web connection...")
            
            # First, basic driver check
            if not self.driver:
                return False, "No driver initialized"
                
            # Try to get current URL as basic connectivity test
            try:
                current_url = self.driver.current_url
                if "web.whatsapp.com" not in current_url:
                    print(f"⚠️ Not on WhatsApp Web. Current URL: {current_url}")
                    try:
                        self.driver.get(WHATSAPP_WEB_URL)
                        time.sleep(3)
                        print("🔄 Navigated back to WhatsApp Web")
                    except Exception as nav_error:
                        return False, f"Cannot navigate to WhatsApp Web: {nav_error}"
            except Exception as url_error:
                if "chrome not reachable" in str(url_error).lower():
                    return False, "Chrome browser not reachable"
                elif "session deleted" in str(url_error).lower():
                    return False, "Browser session ended"
                else:
                    return False, f"Connection error: {url_error}"
            
            # Check login status with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    is_logged_in, status_msg = self.check_login_status()
                    
                    if is_logged_in:
                        print(f"✅ Connection stable: {status_msg}")
                        return True, status_msg
                    
                    # If not logged in, check if it's a temporary loading state
                    if "loading" in status_msg.lower():
                        print(f"⏳ Page loading (attempt {attempt + 1}/{max_retries}), waiting...")
                        time.sleep(5)
                        continue
                    elif "QR code" in status_msg:
                        print(f"📱 QR code detected: {status_msg}")
                        return False, status_msg
                    else:
                        # Connection issue, try to refresh if not last attempt
                        if attempt < max_retries - 1:
                            print(f"🔄 Connection issue (attempt {attempt + 1}/{max_retries}), trying refresh...")
                            try:
                                self.driver.refresh()
                                time.sleep(5)
                                continue
                            except Exception as refresh_error:
                                print(f"❌ Refresh failed: {refresh_error}")
                                continue
                        else:
                            print(f"❌ Connection check failed: {status_msg}")
                            return False, status_msg
                            
                except Exception as check_error:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Status check error (attempt {attempt + 1}/{max_retries}): {check_error}")
                        time.sleep(3)
                        continue
                    else:
                        return False, f"Status check failed: {check_error}"
            
            return False, "Connection verification failed after retries"
            
        except Exception as e:
            print(f"❌ Error checking connection: {e}")
            return False, f"Connection check failed: {str(e)}"

    def sanitize_message_for_chrome(self, message):
        """Sanitize message to be compatible with ChromeDriver while preserving important emojis"""
        try:
            # Define replacements for common emojis with descriptive field names
            # Replace emoji placeholders with actual field names as requested
            emoji_replacements = {
                '📍': 'LOCATION',
                '📞': 'PHONE', 
                '📧': 'EMAIL',
                '📱': 'MOBILE',
                '💬': 'MESSAGE',
                '🔍': 'SEARCH',
                '🧪': 'TEST',
                '🔔': 'NOTIFICATION',
                '🎉': 'CELEBRATION',
                '📋': 'DETAILS',
                '📚': 'BOOKS',
                '🏢': 'BUILDING',
                '🙏': 'THANKS',
                '👋': 'GREETING',
                '✨': 'SPARKLE',
                '📅': 'CALENDAR',
                '🔄': 'RENEWAL',
                '⏰': 'TIME',
                '💰': 'MONEY',
                '📖': 'BOOK',
                # Keep these as they're in BMP range and work well
                # '✅': '✅',  # U+2705 (BMP)
                # '❌': '❌',  # U+274C (BMP)
            }
            
            # First, replace problematic emojis with text alternatives
            sanitized = message
            for emoji, replacement in emoji_replacements.items():
                sanitized = sanitized.replace(emoji, replacement)
            
            # Handle variation selectors (like ⚠️ which is warning + variation selector)
            # These cause issues with ord() but often work fine in browsers
            variation_selectors = [
                '\uFE0E',  # Text variation selector
                '\uFE0F',  # Emoji variation selector
            ]
            
            # Remove variation selectors but keep the base character
            for vs in variation_selectors:
                sanitized = sanitized.replace(vs, '')
            
            # Now check for any remaining non-BMP characters
            final_sanitized = ""
            for char in sanitized:
                try:
                    if ord(char) <= 0xFFFF:
                        # Character is in BMP, keep it
                        final_sanitized += char
                    else:
                        # Non-BMP character, replace with generic placeholder
                        final_sanitized += '[emoji]'
                except TypeError:
                    # This shouldn't happen now, but just in case
                    final_sanitized += '[char]'
            
            return final_sanitized.strip()
            
        except Exception as e:
            print(f"❌ Error sanitizing message: {e}")
            # If sanitization fails completely, try basic replacement
            try:
                # Basic fallback - replace known problematic emojis
                basic_sanitized = message.replace('📍', '[Location]').replace('📞', '[Phone]').replace('📧', '[Email]')
                return basic_sanitized
            except:
                return "Message contains unsupported characters"

    def send_message(self, phone_number, message):
        """
        Send message to a phone number with optimized performance
        
        Optimizations applied:
        - Reduced WebDriverWait timeouts from 30s to 10s for chat loading
        - Reduced invalid number check timeout from 5s to 2s  
        - Optimized selector search with 5s per selector instead of 10s
        - Reduced delays: click delay 1s→0.5s, pre-send delay 1s→0.3s
        - Minimized post-send delay from 3s to 1s while maintaining bot detection avoidance
        - Faster delivery verification with 2s timeout instead of 5s
        - Bulk message delay reduced from 6s to 2s between contacts
        """
        try:
            # Sanitize message to handle Unicode characters
            original_message = message
            sanitized_message = self.sanitize_message_for_chrome(message)
            
            if sanitized_message != original_message:
                print(f"ℹ️ Message sanitized for Chrome compatibility")
                print(f"Original: {original_message[:50]}{'...' if len(original_message) > 50 else ''}")
                print(f"Sanitized: {sanitized_message[:50]}{'...' if len(sanitized_message) > 50 else ''}")
            
            # Use sanitized message
            message = sanitized_message
            
            # Ensure connection is stable before sending
            connection_ok, connection_msg = self.ensure_connection()
            if not connection_ok:
                print(f"❌ Connection not stable: {connection_msg}")
                return False, f"Connection error: {connection_msg}"
            
            print(f"📱 Sending message to {phone_number}...")
            
            # Clean phone number (remove +, spaces, etc.)
            clean_number = re.sub(r'[^\d]', '', phone_number)
            
            # Open chat using WhatsApp Web URL
            chat_url = f"https://web.whatsapp.com/send?phone={clean_number}"
            print(f"🔗 Opening chat: {chat_url}")
            
            try:
                self.driver.get(chat_url)
                print("✅ Navigated to chat URL")
            except Exception as e:
                print(f"❌ Failed to navigate to chat URL: {e}")
                return False, f"Failed to open chat for {phone_number}: {str(e)}"
            
            # Wait for chat to load with optimized timeout
            wait = WebDriverWait(self.driver, 10)  # Reduced from 30 to 10 seconds
            
            # Quick check for invalid number
            try:
                print("🔍 Checking if phone number is valid...")
                invalid_elements = [
                    '//*[contains(text(), "Phone number shared via url is invalid")]',
                    '//*[contains(text(), "invalid")]',
                    '//*[contains(text(), "not found")]',
                ]
                
                # Quick check with reduced timeout
                for invalid_selector in invalid_elements:
                    try:
                        invalid_element = WebDriverWait(self.driver, 2).until(  # Reduced from 5 to 2 seconds
                            EC.presence_of_element_located((By.XPATH, invalid_selector))
                        )
                        if invalid_element.is_displayed():
                            print(f"❌ Invalid phone number detected: {phone_number}")
                            return False, f"Invalid phone number: {phone_number}"
                    except TimeoutException:
                        continue
                        
            except Exception as e:
                print(f"⚠️ Error checking number validity: {e}")
            
            # Find message input with optimized approach - try most reliable selectors first
            # Updated selectors to specifically target chat input box instead of search bar
            message_input_selectors = [
                '//div[@data-testid="conversation-compose-box-input" and not(contains(@class, "search"))]',  # Primary selector (most reliable, exclude search)
                '//div[@data-testid="conversation-compose-box-input"]',  # Fallback primary selector
                '//div[@contenteditable="true"][@data-tab="10" and not(contains(@class, "search"))]',  # Alternative (exclude search)
                '//div[@role="textbox" and @data-tab="10"]',  # Role-based with tab (more specific)
                '//div[@contenteditable="true"][contains(@class, "compose") and not(contains(@class, "search"))]',  # Class-based (exclude search)
                '//div[@contenteditable="true"][contains(@data-testid, "compose")]',  # Data-testid based
                '//div[@contenteditable="true"][@data-tab="10"]',  # Contenteditable with tab
            ]
            
            message_box = None
            # Use shorter timeout per selector for faster overall speed
            quick_wait = WebDriverWait(self.driver, 5)  # 5 seconds per selector instead of 10
            
            for attempt, selector in enumerate(message_input_selectors, 1):
                try:
                    print(f"🔍 Trying to find message input (attempt {attempt}): {selector}")
                    message_box = quick_wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if message_box.is_displayed():
                        print(f"✅ Found message input with selector: {selector}")
                        break
                except TimeoutException:
                    print(f"⏰ Timeout for selector {attempt}: {selector}")
                    continue
                except Exception as e:
                    print(f"❌ Error with selector {attempt}: {e}")
                    continue
            
            if not message_box:
                print("❌ Could not find message input box")
                # Take a screenshot for debugging
                try:
                    screenshot_path = f"whatsapp_error_{clean_number}.png"
                    self.driver.save_screenshot(screenshot_path)
                    print(f"📸 Debug screenshot saved as {screenshot_path}")
                except:
                    pass
                return False, f"Could not find message input for {phone_number}"
            
            try:
                print("📝 Sending message...")
                
                # Click on message box
                message_box.click()
                time.sleep(0.5)  # Reduced delay after click (was 1 second)
                # Add a small additional delay to ensure focus
                time.sleep(0.2)
                
                # Clear any existing text first
                message_box.clear()
                
                # Send message using optimized approach
                # Ensure message is a single continuous string without line breaks
                clean_message = ' '.join(message.split())  # Remove all line breaks and extra spaces
                try:
                    # Direct send_keys (preferred for most text)
                    message_box.send_keys(clean_message)
                    print(f"✅ Message typed successfully: {len(clean_message)} characters")
                except Exception as send_error:
                    print(f"⚠️ Direct send_keys failed: {send_error}")
                    
                    # Fallback: Try using JavaScript to set the value
                    print("🔄 Trying JavaScript input method...")
                    try:
                        self.driver.execute_script("arguments[0].innerText = arguments[1];", message_box, clean_message)
                        print("✅ JavaScript input completed")
                    except Exception as js_error:
                        print(f"⚠️ JavaScript method failed: {js_error}")
                        
                        # Last resort: character-by-character but keep Unicode
                        print("🔄 Trying careful character-by-character input...")
                        message_box.clear()
                        for char in clean_message:
                            try:
                                # Try to send each character, including Unicode
                                message_box.send_keys(char)
                            except Exception as char_error:
                                # If this specific character fails, try a safe alternative
                                if ord(char) > 127:
                                    # For Unicode characters that fail, try field name alternatives
                                    if char == '📍':
                                        message_box.send_keys('LOCATION')
                                    elif char == '📧':
                                        message_box.send_keys('EMAIL')
                                    elif char == '📞':
                                        message_box.send_keys('PHONE')
                                    elif char == '📱':
                                        message_box.send_keys('MOBILE')
                                    elif char == '🔔':
                                        message_box.send_keys('NOTIFICATION')
                                    elif char == '📋':
                                        message_box.send_keys('DETAILS')
                                    elif char == '🎉':
                                        message_box.send_keys('CELEBRATION')
                                    else:
                                        # Skip other problematic characters
                                        continue
                                else:
                                    message_box.send_keys(char)
                        print("✅ Character-by-character input completed")
                
                # Minimal wait before sending (reduced from 1 second)
                time.sleep(0.3)
                
                # Send the message with Enter key
                try:
                    message_box.send_keys(Keys.ENTER)
                    print("✅ Enter key sent")
                except Exception as enter_error:
                    print(f"⚠️ Enter key failed: {enter_error}")
                    # Try alternative send button
                    try:
                        send_button = self.driver.find_element(By.XPATH, '//span[@data-testid="send"]')
                        send_button.click()
                        print("✅ Send button clicked")
                    except Exception as button_error:
                        print(f"❌ Send button also failed: {button_error}")
                        return False, f"Could not send message: {str(button_error)}"
                
                print("✅ Message sent successfully!")
                
                # Reduced delay to avoid bot detection (still necessary but shorter)
                time.sleep(1)  # Reduced from WHATSAPP_DELAY (3 seconds) to 1 second
                
                # Quick verification of message delivery (optional with reduced timeout)
                try:
                    # Look for sent message indicators with shorter timeout
                    sent_indicators = [
                        '//span[@data-testid="msg-time"]',  # Message timestamp
                        '//span[contains(@class, "check")]',  # Check marks
                        '//div[contains(@class, "message-out")]',  # Outgoing message
                    ]
                    
                    for indicator in sent_indicators:
                        try:
                            element = WebDriverWait(self.driver, 2).until(  # Reduced from 5 to 2 seconds
                                EC.presence_of_element_located((By.XPATH, indicator))
                            )
                            if element.is_displayed():
                                print(f"✅ Message delivery confirmed: {indicator}")
                                break
                        except:
                            continue
                            
                except Exception as e:
                    print(f"⚠️ Could not verify message delivery: {e}")
                
                return True, "Message sent successfully"
                
            except Exception as e:
                print(f"❌ Error sending message: {e}")
                return False, f"Failed to send message: {str(e)}"
        
        except Exception as e:
            print(f"❌ Error in send_message: {str(e)}")
            return False, f"Error sending message: {str(e)}"
    
    def send_bulk_messages(self, contacts_messages):
        """Send messages to multiple contacts with optimized speed"""
        results = []
        total_contacts = len(contacts_messages)
        
        print(f"📤 Starting bulk message sending to {total_contacts} contacts...")
        
        for index, contact in enumerate(contacts_messages, 1):
            phone_number = contact['phone']
            message = contact['message']
            name = contact.get('name', phone_number)
            
            print(f"📱 Sending message {index}/{total_contacts} to {name} ({phone_number})")
            
            success, result_message = self.send_message(phone_number, message)
            
            results.append({
                'name': name,
                'phone': phone_number,
                'success': success,
                'message': result_message
            })
            
            # Add spacing between messages for better delivery and readability
            if index < total_contacts:  # Don't wait after the last message
                time.sleep(2)  # 2 seconds between messages for better spacing
        
        print(f"✅ Bulk message sending completed. {sum(1 for r in results if r['success'])}/{total_contacts} messages sent successfully.")
        return results
    
    def _format_time(self, t):
        """Convert a time/datetime/str into a readable 'H:MM AM/PM' string"""
        import datetime
        if t is None:
            return None
        if isinstance(t, datetime.datetime):
            t = t.time()
        if isinstance(t, datetime.time):
            return t.strftime('%I:%M %p').lstrip('0')
        if isinstance(t, str):
            # Accept 'HH:MM[:SS]' strings
            for fmt in ('%H:%M:%S', '%H:%M'):
                try:
                    parsed = datetime.datetime.strptime(t, fmt).time()
                    return parsed.strftime('%I:%M %p').lstrip('0')
                except ValueError:
                    continue
            return t  # fallback
        return str(t)

    def send_subscription_reminders(self, expiring_subscriptions):
        """Send subscription expiry reminders with timeslot duration and optimized speed"""
        messages = []
        
        for subscription in expiring_subscriptions:
            # Format message professionally with proper structure and spacing
            # Build a user-friendly timeslot string "HH:MM AM/PM – HH:MM AM/PM (X hrs)"
            def _get(key, default=None):
                return subscription[key] if key in subscription.keys() else default

            start_raw = _get('timeslot_start')
            end_raw   = _get('timeslot_end')
            if start_raw and end_raw:
                start_f = self._format_time(start_raw)
                end_f   = self._format_time(end_raw)
                # Calculate duration in hours
                try:
                    import datetime as _dt
                    s_dt = _dt.datetime.strptime(start_f, '%I:%M %p')
                    e_dt = _dt.datetime.strptime(end_f,   '%I:%M %p')
                    # Handle overnight
                    if e_dt <= s_dt:
                        e_dt += _dt.timedelta(days=1)
                    dur_hrs = round((e_dt - s_dt).seconds / 3600, 1)
                    timeslot_str = f"{start_f} – {end_f}  ({dur_hrs} hrs)"
                except Exception:
                    timeslot_str = f"{start_f} – {end_f}"
            else:
                timeslot_str = _get('timeslot_name', 'N/A')

            # Professionally formatted message with clear spacing and Markdown styling
            message = (
                "*🔔 SUBSCRIPTION EXPIRY REMINDER*\n\n\n"
                f"Dear *{subscription['student_name']}*,\n\n"
                "Your library subscription is about to expire. Please review the details below:\n\n"
                "*Subscription Details*\n"
                f"• *Seat Number:* {subscription['seat_number']}\n"
                f"• *Timeslot:* {timeslot_str}\n"
                f"• *Expiry Date:* {subscription['end_date']}\n\n"
                "Kindly renew before the expiry date to avoid cancellation.\n\n"
                f"*{LIBRARY_NAME} Location*\n{LIBRARY_ADDRESS}\n\n"
                "*Contact*\n"
                f"• Phone: {LIBRARY_PHONE}\n"
                f"• Email: {LIBRARY_EMAIL}\n\n"
                "Thank you for choosing *Sangharsh Library*! We look forward to serving you again.\n\n"
                "Best regards,\n"
                f"{LIBRARY_NAME} Team"
            )
            
            messages.append({
                'name': subscription['student_name'],
                'phone': subscription['mobile_number'],
                'message': message
            })
        
        return self.send_bulk_messages(messages)
    
    def send_subscription_cancellations(self, expired_subscriptions):
        """Send subscription cancellation messages to expired students with timeslot duration"""
        messages = []
        
        for subscription in expired_subscriptions:
            # Format message professionally with proper structure and spacing
            # Include timeslot duration (from-to) instead of just timeslot name
            timeslot_duration = f"{subscription['timeslot_start']} to {subscription['timeslot_end']}" if 'timeslot_start' in subscription and 'timeslot_end' in subscription and subscription['timeslot_start'] and subscription['timeslot_end'] else subscription['timeslot_name']
            
            # Create a professionally formatted message with clear sections and proper line breaks
            message = (
                "📢 *SUBSCRIPTION CANCELLATION NOTICE*\n\n\n"
                f"Dear {subscription['student_name']},\n\n"
                "We regret to inform you that your library subscription has expired and has been cancelled.\n\n"
                "📋 *Subscription Details:*\n"
                f"   • Seat Number: {subscription['seat_number']}\n"
                f"   • Timeslot: {timeslot_duration}\n"
                f"   • Expiry Date: {subscription['end_date']}\n\n"
                "🔄 *Readmission Process:*\n"
                "If you wish to continue using our library services, please contact us immediately for readmission.\n\n"
                "📞 *Contact Information:*\n"
                f"   • WhatsApp: {LIBRARY_PHONE}\n"
                f"   • Visit: {LIBRARY_ADDRESS}\n"
                f"   • Email: {LIBRARY_EMAIL}\n\n"
                "We understand that circumstances can cause delays, and we're here to help you get back on track with your studies.\n\n"
                "⚡ *Quick Readmission:*\n"
                f"Simply reply to this message or call us at {LIBRARY_PHONE} to discuss readmission options and available seats.\n\n"
                f"Thank you for being part of {LIBRARY_NAME}. We hope to welcome you back soon!\n\n"
                "Best regards,\n"
                f"{LIBRARY_NAME} Team"
            )
            
            messages.append({
                'name': subscription['student_name'],
                'phone': subscription['mobile_number'],
                'message': message
            })
        
        return self.send_bulk_messages(messages)
    
    def send_overdue_book_reminders(self, overdue_borrowings):
        """Send overdue book return reminders with optimized speed"""
        messages = []
        
        for borrowing in overdue_borrowings:
            # Format message professionally with proper structure and spacing
            # Create a professionally formatted message with clear sections and proper line breaks
            message = (
                "📚 *OVERDUE BOOK REMINDER*\n\n\n"
                f"Hello {borrowing['student_name']}!\n\n"
                "This is a reminder that the following book is now overdue:\n\n\n"
                "📖 *Book Details:*\n"
                f"   • Title: {borrowing['book_title']}\n"
                f"   • Author: {borrowing['author']}\n"
                f"   • Borrowed On: {borrowing['borrow_date']}\n"
                f"   • Due Date: {borrowing['due_date']}\n\n\n"
                "Please return the book as soon as possible to avoid late fees.\n\n\n"
                f"📍 *{LIBRARY_NAME} Location:*\n"
                f"{LIBRARY_ADDRESS}\n\n\n"
                "📞 *Contact Information:*\n"
                f"   • Phone: {LIBRARY_PHONE}\n"
                f"   • Email: {LIBRARY_EMAIL}\n\n\n"
                "Thank you for your cooperation!\n\n"
                "Best regards,\n"
                f"{LIBRARY_NAME} Team"
            )
            
            messages.append({
                'name': borrowing['student_name'],
                'phone': borrowing['mobile_number'],
                'message': message
            })
        
        return self.send_bulk_messages(messages)
        """Send subscription expiry reminders as consolidated messages per student"""
        # Group subscriptions by student
        student_groups = {}
        for subscription in expiring_subscriptions:
            phone = subscription['mobile_number']
            if phone not in student_groups:
                student_groups[phone] = {
                    'name': subscription['student_name'],
                    'subscriptions': []
                }
            student_groups[phone]['subscriptions'].append(subscription)
        
        messages = []
        for phone, data in student_groups.items():
            name = data['name']
            subscriptions = data['subscriptions']
            
            if len(subscriptions) == 1:
                sub = subscriptions[0]
                timeslot_duration = f"{sub['timeslot_start']} to {sub['timeslot_end']}" if 'timeslot_start' in sub and 'timeslot_end' in sub and sub['timeslot_start'] and sub['timeslot_end'] else sub['timeslot_name']
                message = (
                    f"🔔 *SUBSCRIPTION EXPIRY REMINDER*\n\n\n"
                    f"Hello {name}!\n\n"
                    "This is a reminder that your library subscription is expiring soon.\n\n\n"
                    "📋 *Subscription Details:*\n"
                    f"   • Seat Number: {sub['seat_number']}\n"
                    f"   • Timeslot: {timeslot_duration}\n"
                    f"   • Expiry Date: {sub['end_date']}\n\n\n"
                    "Please visit us to renew your subscription before the expiry date to avoid cancellation.\n\n\n"
                    f"📍 *{LIBRARY_NAME} Location:*\n"
                    f"{LIBRARY_ADDRESS}\n\n\n"
                    "📞 *Contact Information:*\n"
                    f"   • Phone: {LIBRARY_PHONE}\n"
                    f"   • Email: {LIBRARY_EMAIL}\n\n\n"
                    f"Thank you for choosing {LIBRARY_NAME}!\n\n"
                    "Best regards,\n"
                    f"{LIBRARY_NAME} Team"
                )
            else:
                subs_details = "\n".join([f"   • Seat {sub['seat_number']} | {sub['timeslot_start'] + ' to ' + sub['timeslot_end'] if 'timeslot_start' in sub and 'timeslot_end' in sub and sub['timeslot_start'] and sub['timeslot_end'] else sub['timeslot_name']} | Expires: {sub['end_date']}" for sub in subscriptions])
                message = (
                    "🔔 *MULTIPLE SUBSCRIPTION REMINDERS*\n\n\n"
                    f"Hello {name}!\n\n"
                    "You have {len(subscriptions)} library subscriptions expiring soon.\n\n\n"
                    "📋 *Subscription Details:*\n"
                    f"{subs_details}\n\n\n"
                    "Please visit us to renew your subscriptions before the expiry dates to avoid cancellation.\n\n\n"
                    f"📍 *{LIBRARY_NAME} Location:*\n"
                    f"{LIBRARY_ADDRESS}\n\n\n"
                    "📞 *Contact Information:*\n"
                    f"   • Phone: {LIBRARY_PHONE}\n"
                    f"   • Email: {LIBRARY_EMAIL}\n\n\n"
                    f"Thank you for choosing {LIBRARY_NAME}!\n\n"
                    "Best regards,\n"
                    f"{LIBRARY_NAME} Team"
                )
            
            messages.append({'name': name, 'phone': phone, 'message': message})
        
        return self.send_bulk_messages(messages)

    def test_message_with_emojis(self, phone_number):
        """Test sending a message with emojis to verify they display correctly"""
        test_message = f"""
🧪 Test Message from {LIBRARY_NAME}

This is a test to verify emoji display:
📍 Location: {LIBRARY_ADDRESS}
📞 Phone: {LIBRARY_PHONE}
📧 Email: {LIBRARY_EMAIL}

Common symbols:
✅ Check mark
❌ Cross mark
⚠️ Warning
ℹ️ Information
🔍 Search
📱 Mobile
💬 Message

If you can see all the emojis above correctly, the messaging system is working properly!

Thank you for testing {LIBRARY_NAME}!
        """.strip()
        
        return self.send_message(phone_number, test_message)
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass

    def close_driver(self):
        """Close the WebDriver"""
        try:
            if self.driver:
                print("🔄 Closing WebDriver...")
                self.driver.quit()
                self.driver = None
                self.is_logged_in = False
                print("✅ Driver closed successfully")
            return True, "Driver closed successfully"
        except Exception as e:
            print(f"❌ Error closing driver: {str(e)}")
            return False, f"Error closing driver: {str(e)}"
    
    def test_chrome_installation(self):
        """Test Chrome installation and return diagnostic information"""
        import platform
        import subprocess
        
        result = {
            'system': platform.system(),
            'chrome_found': False,
            'chrome_path': None,
            'diagnostics': []
        }
        
        diagnostics = []
        diagnostics.append("=== Chrome Installation Diagnostic ===")
        diagnostics.append(f"Operating System: {platform.system()} {platform.release()}")
        diagnostics.append("")
        
        # Find Chrome
        chrome_path = self.find_chrome_executable()
        if chrome_path:
            result['chrome_found'] = True
            result['chrome_path'] = chrome_path
            diagnostics.append(f"✅ Chrome found at: {chrome_path}")
            
            # Test if Chrome is executable
            try:
                if os.access(chrome_path, os.X_OK):
                    diagnostics.append("✅ Chrome is executable")
                else:
                    diagnostics.append("❌ Chrome is not executable")
            except Exception as e:
                diagnostics.append(f"❌ Error checking Chrome executable: {e}")
            
            # Try to get Chrome version
            try:
                version_result = subprocess.run([chrome_path, '--version'], 
                                              capture_output=True, text=True, timeout=10)
                if version_result.returncode == 0:
                    diagnostics.append(f"✅ Chrome version: {version_result.stdout.strip()}")
                else:
                    diagnostics.append(f"❌ Failed to get Chrome version: {version_result.stderr}")
            except Exception as e:
                diagnostics.append(f"❌ Error getting Chrome version: {e}")
                
        else:
            diagnostics.append("❌ Chrome not found")
            diagnostics.append("")
            diagnostics.append("Searched locations:")
            
            # Show all searched paths
            system = platform.system()
            if system == "Linux":
                search_paths = [
                    '/usr/bin/google-chrome',
                    '/usr/bin/google-chrome-stable',
                    '/usr/bin/chromium-browser',
                    '/usr/bin/chromium',
                    '/snap/bin/chromium',
                    '/usr/bin/chrome',
                    '/opt/google/chrome/chrome',
                    '/usr/local/bin/chrome',
                    '/usr/local/bin/google-chrome',
                    '/var/lib/flatpak/app/com.google.Chrome/current/active/export/bin/com.google.Chrome'
                ]
                for path in search_paths:
                    exists = "✅" if os.path.exists(path) else "❌"
                    diagnostics.append(f"  {exists} {path}")
        
        diagnostics.append("")
        diagnostics.append("=== ChromeDriver Information ===")
        
        # Check for ChromeDriver
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver_path = ChromeDriverManager().install()
            diagnostics.append(f"✅ WebDriver Manager can install ChromeDriver at: {driver_path}")
        except Exception as e:
            diagnostics.append(f"❌ WebDriver Manager failed: {e}")
        
        # Check system ChromeDrivers
        system_drivers = [
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver',
            '/snap/bin/chromedriver'
        ]
        
        diagnostics.append("")
        diagnostics.append("System ChromeDriver locations:")
        for driver_path in system_drivers:
            exists = "✅" if os.path.exists(driver_path) else "❌"
            diagnostics.append(f"  {exists} {driver_path}")
        
        diagnostics.append("")
        if not result['chrome_found']:
            install_instructions = self.get_chrome_install_instructions()
            diagnostics.append("=== Installation Instructions ===")
            diagnostics.extend(install_instructions.split('\n'))
        
        result['diagnostics'] = diagnostics
        return result

    def test_message_with_emojis(self, phone_number):
        """Test sending a message with emojis to verify they display correctly"""
        test_message = f"""
🧪 Test Message from {LIBRARY_NAME}

This is a test to verify emoji display:
📍 Location: {LIBRARY_ADDRESS}
📞 Phone: {LIBRARY_PHONE}
📧 Email: {LIBRARY_EMAIL}

Common symbols:
✅ Check mark
❌ Cross mark
⚠️ Warning
ℹ️ Information
🔍 Search
📱 Mobile
💬 Message

If you can see all the emojis above correctly, the messaging system is working properly!

Thank you for testing {LIBRARY_NAME}!
        """.strip()
        
        return self.send_message(phone_number, test_message)
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
