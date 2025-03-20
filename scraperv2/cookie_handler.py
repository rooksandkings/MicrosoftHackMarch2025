import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def handle_cookies(driver):
    """
    Handles cookie consent banner on McKinsey website
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        None
    """
    print("Looking for cookie consent banner...", flush=True)
    try:
        # Wait for cookie banner and accept
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        ).click()
        print("[OK] Cookies banner found and accepted", flush=True)
    except (TimeoutException, NoSuchElementException):
        print("[!] Cookie banner not found or already accepted", flush=True)
    
    time.sleep(2)  # Allow time for cookie processing
    print("Cookie handling completed", flush=True) 