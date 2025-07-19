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
                # Try multiple selectors for logged-in state
                logged_in_selectors = [
                    '//div[@data-testid="chat-list"]',  # Main chat list
                    '//div[contains(@class, "chat-list")]',  # Alternative chat list
                    '//div[@data-testid="chatlist-header"]',  # Chat list header
                    '//span[@data-testid="default-user"]',  # User profile
                    '//div[@id="main"]',  # Main WhatsApp container
                    '//div[contains(@class, "two") and contains(@class, "copyable")]',  # Two-pane layout
                    '//header[@data-testid="chatlist-header"]',  # Header with user info
                    '//div[@role="application"]//div[contains(@class, "app")]'  # App container
                ]
                
                for selector in logged_in_selectors:
                    try:
                        wait_short = WebDriverWait(self.driver, 5)
                        element = wait_short.until(EC.presence_of_element_located((By.XPATH, selector)))
                        if element and element.is_displayed():
                            self.is_logged_in = True
                            print(f"✅ Already logged in! (Found: {selector})")
                            return True, "Already logged in to WhatsApp Web"
                    except TimeoutException:
                        continue
                
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
                                time.sleep(5)  # Initial wait
                                
                                # Verify page is stable and ready
                                stability_check_count = 0
                                max_stability_checks = 6  # 30 seconds total (6 x 5s)
                                
                                while stability_check_count < max_stability_checks:
                                    try:
                                        # Check if we can find key elements that indicate a stable page
                                        stable_elements = [
                                            '//div[@data-testid="chat-list"]',
                                            '//div[@data-testid="chatlist-header"]',
                                            '//span[@data-testid="default-user"]',
                                        ]
                                        
                                        stable_count = 0
                                        for stable_selector in stable_elements:
                                            try:
                                                element = self.driver.find_element(By.XPATH, stable_selector)
                                                if element and element.is_displayed():
                                                    stable_count += 1
                                            except:
                                                pass
                                        
                                        if stable_count >= 2:  # At least 2 stable elements found
                                            print("✅ WhatsApp Web is stable and ready!")
                                            self.is_logged_in = True
                                            return True, "Successfully logged in to WhatsApp Web"
                                        else:
                                            print(f"⏳ Waiting for page to stabilize... ({stability_check_count + 1}/{max_stability_checks})")
                                            time.sleep(5)
                                            stability_check_count += 1
                                            
                                    except Exception as e:
                                        print(f"⚠️ Stability check error: {e}")
                                        time.sleep(5)
                                        stability_check_count += 1
                                
                                # If we reach here, page might not be fully stable but login was detected
                                print("⚠️ Login detected but page may not be fully stable")
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
    
    def check_login_status(self):
        """Check if logged into WhatsApp Web with comprehensive detection"""
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
                    # Try to recover by refreshing
                    try:
                        print("⚠️ Connection issue detected, attempting to refresh...")
                        self.driver.refresh()
                        time.sleep(3)
                        current_url = self.driver.current_url
                        if "web.whatsapp.com" not in current_url:
                            return False, f"Connection lost (URL: {current_url})"
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
            ]
            
            # Check for logged-in indicators with better error handling
            login_detected = False
            detected_selector = None
            
            for selector in logged_in_selectors:
                try:
                    wait = WebDriverWait(self.driver, 3)
                    element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    if element.is_displayed():
                        login_detected = True
                        detected_selector = selector
                        break
                except TimeoutException:
                    continue
                except Exception as e:
                    if "stale element" in str(e).lower():
                        # Page is changing, wait a bit and continue
                        time.sleep(2)
                        continue
                    else:
                        continue
            
            if login_detected:
                # Double-check that we can interact with the page
                try:
                    # Try to find search box or any interactive element
                    interactive_elements = [
                        '//div[@data-testid="chat-list-search"]',
                        '//div[@data-testid="search-input"]',
                        '//input[@type="text"]',
                        '//div[@contenteditable="true"]',
                    ]
                    
                    for interactive_selector in interactive_elements:
                        try:
                            element = self.driver.find_element(By.XPATH, interactive_selector)
                            if element.is_displayed():
                                return True, f"Logged in and interactive (found: {detected_selector})"
                        except:
                            continue
                    
                    # Even if no interactive elements found, if login detected, probably OK
                    return True, f"Logged in (found: {detected_selector})"
                    
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
                    wait = WebDriverWait(self.driver, 2)
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
            ]
            
            for selector in loading_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        return False, f"Page loading (found: {selector})"
                except:
                    continue
            
            # If we can't determine status, try to get page title and content
            try:
                title = self.driver.title
                if "WhatsApp" in title:
                    # Look for any element that might indicate the page state
                    all_elements = self.driver.find_elements(By.XPATH, '//*[@data-testid]')
                    testids = [el.get_attribute('data-testid') for el in all_elements if el.get_attribute('data-testid')]
                    
                    if any('chat' in testid.lower() for testid in testids):
                        return True, f"Likely logged in (found chat-related elements: {testids[:3]})"
                    elif any('qr' in testid.lower() for testid in testids):
                        return False, f"Likely QR code (found QR-related elements: {testids[:3]})"
                    else:
                        # Check page source for clues
                        try:
                            page_source = self.driver.page_source.lower()
                            if 'chat-list' in page_source or 'chatlist' in page_source:
                                return True, "Likely logged in (found chat references in page source)"
                            elif 'qr' in page_source and 'scan' in page_source:
                                return False, "Likely QR code (found QR references in page source)"
                            else:
                                return False, f"Unknown state (found elements: {testids[:5]})"
                        except:
                            return False, f"Unknown state (found elements: {testids[:5]})"
                else:
                    return False, f"Invalid page (title: {title})"
            except Exception as e:
                return False, f"Cannot determine status: {str(e)}"
                
        except Exception as e:
            return False, f"Status check failed: {str(e)}"
    
    def ensure_connection(self):
        """Ensure WhatsApp Web connection is stable"""
        try:
            print("🔍 Checking WhatsApp Web connection...")
            
            is_logged_in, status_msg = self.check_login_status()
            
            if is_logged_in:
                print(f"✅ Connection stable: {status_msg}")
                return True, status_msg
            
            print(f"⚠️ Connection issue detected: {status_msg}")
            
            # Try to recover connection
            if "connection lost" in status_msg.lower() or "driver error" in status_msg.lower():
                print("🔄 Attempting to recover connection...")
                try:
                    # Try to refresh the page
                    self.driver.refresh()
                    time.sleep(5)
                    
                    # Check again
                    is_logged_in, new_status = self.check_login_status()
                    if is_logged_in:
                        print(f"✅ Connection recovered: {new_status}")
                        return True, new_status
                    else:
                        print(f"❌ Could not recover connection: {new_status}")
                        return False, new_status
                        
                except Exception as e:
                    print(f"❌ Error during connection recovery: {e}")
                    return False, f"Connection recovery failed: {str(e)}"
            
            return False, status_msg
            
        except Exception as e:
            print(f"❌ Error checking connection: {e}")
            return False, f"Connection check failed: {str(e)}"

    def send_message(self, phone_number, message):
        """Send message to a phone number"""
        try:
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
            
            # Wait for chat to load with multiple retry attempts
            wait = WebDriverWait(self.driver, 30)
            
            # Check for invalid number first
            try:
                print("🔍 Checking if phone number is valid...")
                invalid_elements = [
                    '//*[contains(text(), "Phone number shared via url is invalid")]',
                    '//*[contains(text(), "invalid")]',
                    '//*[contains(text(), "not found")]',
                ]
                
                for invalid_selector in invalid_elements:
                    try:
                        invalid_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, invalid_selector))
                        )
                        if invalid_element.is_displayed():
                            print(f"❌ Invalid phone number detected: {phone_number}")
                            return False, f"Invalid phone number: {phone_number}"
                    except TimeoutException:
                        continue
                        
            except Exception as e:
                print(f"⚠️ Error checking number validity: {e}")
            
            # Wait for the page to load and find message input
            message_input_selectors = [
                '//div[@data-testid="conversation-compose-box-input"]',  # Primary selector
                '//div[@contenteditable="true"][@data-tab="10"]',  # Alternative
                '//div[@contenteditable="true"][contains(@class, "compose")]',  # Class-based
                '//div[@role="textbox"]',  # Role-based
                '//div[@contenteditable="true"]',  # Generic contenteditable
            ]
            
            message_box = None
            for attempt, selector in enumerate(message_input_selectors, 1):
                try:
                    print(f"🔍 Trying to find message input (attempt {attempt}): {selector}")
                    message_box = wait.until(
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
                time.sleep(1)  # Small delay after click
                
                # Clear any existing text and send message
                message_box.clear()
                message_box.send_keys(message)
                
                # Wait a moment before sending
                time.sleep(1)
                
                # Send the message
                message_box.send_keys(Keys.ENTER)
                
                print("✅ Message sent successfully!")
                
                # Add delay to avoid being detected as bot
                time.sleep(WHATSAPP_DELAY)
                
                # Verify message was sent (optional check)
                try:
                    # Look for sent message indicators
                    sent_indicators = [
                        '//span[@data-testid="msg-time"]',  # Message timestamp
                        '//span[contains(@class, "check")]',  # Check marks
                        '//div[contains(@class, "message-out")]',  # Outgoing message
                    ]
                    
                    for indicator in sent_indicators:
                        try:
                            element = WebDriverWait(self.driver, 5).until(
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
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
