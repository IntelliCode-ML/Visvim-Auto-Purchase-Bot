"""
Visvim Web Scraper and Automated Checkout System

This module provides functionality to automate the process of purchasing products from the Visvim online store.
It handles login, product selection, cart management, and PayPal payment processing.

Key Features:
- Automated login to Visvim store
- Product availability checking
- Cart management
- PayPal payment processing with both PayPal account and credit card options
- Scheduled checkout functionality

Dependencies:
- selenium
- undetected_chromedriver
- webdriver_manager
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import undetected_chromedriver as uc


def allow_paypal_payment(driver, main_window):
    """
    Handles the PayPal payment window transition and button clicking.
    
    Args:
        driver: Selenium WebDriver instance
        main_window: Handle of the main browser window
    """
    try:
        # Log all iframes for debug
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes on the page.")

        for i, iframe in enumerate(iframes):
            try:
                driver.switch_to.frame(iframe)
                paypal_button = driver.find_element(By.CLASS_NAME, 'paypal-button')
                print(f"✅ PayPal button found in iframe {i}")
                paypal_button.click()
                driver.switch_to.default_content()
                break
            except:
                driver.switch_to.default_content()
                continue        
    except Exception as e:
        print(f"❌ Error clicking PayPal button: {e}")
    
    
    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

    for handle in driver.window_handles:
        if handle != main_window:
            driver.switch_to.window(handle)
            print("✅ Switched to PayPal window.")
            break
    time.sleep(5)  # Wait for the PayPal window to load


def wait_until_time(target_time_str):
    """
    Waits until the specified target time before proceeding.
    
    Args:
        target_time_str (str): Target time in format "YYYY-MM-DD HH:MM:SS"
    """
    from datetime import datetime, timedelta

    target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S")
    print(f"⏳ Waiting until {target_time} to proceed with PayPal payment...")

    while True:
        now = datetime.now()
        if now >= target_time:
            print(f"🕒 Time reached: {now}. Proceeding with payment.")
            break
        else:
            remaining = (target_time - now).total_seconds()
            if remaining > 60:
                time.sleep(30)
            elif remaining > 10:
                time.sleep(5)
            else:
                time.sleep(1)


def pay_with_paypal_2(driver, paypal_email, paypal_password, card_info=None, personal_info=None):
    """
    Processes PayPal payment with either PayPal account or credit card.
    
    Args:
        driver: Selenium WebDriver instance
        paypal_email (str): PayPal account email
        paypal_password (str): PayPal account password
        card_info (dict, optional): Credit card information
        personal_info (dict, optional): Personal information for billing
    """
    # time.sleep(5)  # Give PayPal page time to load

    try:
        wait = WebDriverWait(driver, 10)

        # Click "Pay with Debit or Credit Card"
        try:
            card_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Debit or Credit Card') or contains(text(), 'Pay with a card')]")))
            driver.execute_script("arguments[0].click();", card_button)
            print("Clicked 'Pay with Debit or Credit Card'")
        except:
            print("Could not find card option, proceeding with login...")

            # Login with PayPal email
            try:
                email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
                email_input.send_keys(paypal_email)
                next_btn = driver.find_element(By.ID, "btnNext")
                next_btn.click()
            except Exception as e:
                print(f"Email step error: {e}")

            # Enter password
            try:
                password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
                password_input.send_keys(paypal_password)
                login_btn = driver.find_element(By.ID, "btnLogin")
                login_btn.click()
            except Exception as e:
                print(f"Password step error: {e}")

            # Handle Captcha
        try:
            captcha_available = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(., 'I'm not a robot') or contains(., 'recaptcha') or contains(., 'reCAPTCHA') or contains(., 'Captcha')]")))
            time.sleep(10)
        except:
            print("No reCAPTCHA found.")

        # Handle Card Payment
        if card_info:
            try:
                time.sleep(3)
                phone = wait.until(EC.presence_of_element_located((By.ID, "phone")))
                phone.send_keys(personal_info['phone'])

                try:
                    card_number = wait.until(EC.presence_of_element_located((By.ID, "cardNumber")))
                    card_number.send_keys(card_info['number'])
                except:
                    print("Card number input not found.")

                # Expiry
                try:
                    driver.execute_script("document.getElementById('cardExpiry').value = arguments[0];", card_info['expiry'])
                except Exception as e:
                    print("Expiry input not found via JS:", e)

                # CVV
                try:
                    driver.execute_script("document.getElementById('cardCvv').value = arguments[0];", card_info['cvv'])
                except Exception as e:
                    print("CVV input not found via JS:", e)

                # First Name
                try:
                    driver.execute_script("document.getElementById('firstName').value = arguments[0];", personal_info['first_name'])
                except Exception as e:
                    print("First name input not found via JS:", e)

                # Last Name
                try:
                    driver.execute_script("document.getElementById('lastName').value = arguments[0];", personal_info['last_name'])
                except Exception as e:
                    print("Last name input not found via JS:", e)

                # Address
                try:
                    driver.execute_script("document.getElementById('billingLine1').value = arguments[0];", personal_info['address'])
                except Exception as e:
                    print("Address input not found via JS:", e)

                # City
                try:
                    driver.execute_script("document.getElementsByName('billingCity')[0].value = arguments[0];", personal_info['city'])
                except Exception as e:
                    print("City input not found via JS:", e)

                # State (Dropdown)
                try:
                    driver.execute_script("""
                        let sel = document.getElementById('billingState');
                        for (let i = 0; i < sel.options.length; i++) {
                            if (sel.options[i].text === arguments[0]) {
                                sel.selectedIndex = i;
                                sel.dispatchEvent(new Event('change'));
                                break;
                            }
                        }
                    """, personal_info['state'])
                except Exception as e:
                    print("State dropdown not found via JS:", e)

                # ZIP Code
                try:
                    driver.execute_script("document.getElementById('billingPostalCode').value = arguments[0];", personal_info['zip_code'])
                except Exception as e:
                    print("Zip code input not found via JS:", e)

                try:
                    checkbox = driver.find_element("css selector", 'label[for^="Switch"]')
                    # if not checkbox.is_selected():
                    driver.execute_script("arguments[0].click();", checkbox)
                except:
                    print("Checkbox input not found.")

                try:
                    shippingSame = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.css-ltr-109pikv-checkmark_container')))
                    driver.execute_script("arguments[0].click();", shippingSame)
                except Exception as e:
                    print(f"Shipping address checkbox not found: {e}")

                time.sleep(500)  # Wait for the payment to process

                try:
                    pay_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Pay Now') or contains(., 'Agree and Pay') or contains(., 'Agree and Continue')]")))
                    driver.execute_script("arguments[0].click();", pay_btn)
                except:
                    print("Pay button not found.")
                
                continue_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue')]")))
                driver.execute_script("arguments[0].click();", continue_btn)

                print("✅ Card info submitted.")
            except Exception as e:
                print(f"Error filling card details: {e}")
        else:
            print("No card info provided; assuming PayPal login used.")

        time.sleep(10)  # Give time for payment to process
        print("✅ Payment flow completed.")

    except Exception as e:
        print(f"❌ Payment process failed: {e}")
        return False


def pay_with_paypal(driver, paypal_email, paypal_password):
    time.sleep(5)  # Wait for the PayPal page to load
    try:
        wait = WebDriverWait(driver, 10)

        try:
            email_input = driver.find_element(By.ID, "email")
            if email_input:
                email_input.send_keys(paypal_email)
        except Exception as e:
            print(f"Error finding email input: {e}")
        
        try:
            Next = driver.find_element(By.XPATH, "//*[contains(text(), 'Next')]")
            if Next:
                driver.execute_script("arguments[0].click();", Next)
        except Exception as e:
            print(f"Error finding login button: {e}")
        
        try:
            password_input = driver.find_element(By.ID, 'password')
            if password_input:
                password_input.send_keys(paypal_password)
        except Exception as e:
            print(f"Error finding password input: {e}")
        
        try:
            login_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Log In')]")
            if login_button:
                driver.execute_script("arguments[0].click();", login_button)
        except Exception as e:
            print(f"Error finding login button: {e}")
        
        try:
            pay_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button//*[contains(text(), 'Pay') or contains(text(), 'Continue')]/..")))
            driver.execute_script("arguments[0].click();", pay_button)
        except Exception as e:
            print(f"Error finding PayPal pay button: {e}")
        
        time.sleep(100)  # Wait for the payment to process


        print("✅ Successfully logged in to PayPal and proceeded with payment.")
        print("✅ Proceeded to PayPal payment.")
    except Exception as e:
        print(f"Error proceeding to PayPal payment: {e}")


def setup_driver():
    """
    Sets up and configures the Chrome WebDriver with necessary options.
    
    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    options = uc.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("incognito")  # Use incognito mode
    driver = uc.Chrome(options=options)
    return driver


def proceed_payment(driver, paypal_email, paypal_password, card_info=None, personal_info=None, timer=None):
    """
    Handles the payment process flow including delivery address selection and PayPal integration.
    
    Args:
        driver: Selenium WebDriver instance
        paypal_email (str): PayPal account email
        paypal_password (str): PayPal account password
        card_info (dict, optional): Credit card information
        personal_info (dict, optional): Personal information for billing
        timer (str, optional): Target time for payment in format "YYYY-MM-DD HH:MM:SS"
    """
    wait = WebDriverWait(driver, 20)
    # Step 1
    try:
        # Click on "Proceed Payment" button
        proceed_payment_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-primary.block-cart--order-btn')))
        driver.execute_script("arguments[0].click();", proceed_payment_btn)
        print("✅ Proceeded to order confirmation.")
    except Exception as e:
        print(f"Error clicking proceed payment button: {e}")
        return

    # Step 2
    try:
        # Select the last delivery address from the list
        addresses = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.block-order-method--dest-item.js-sender-item')))
        if not addresses:
            print("No delivery address elements found.")
            return
        input_to_click = addresses[-1].find_element(By.TAG_NAME, 'input')
        driver.execute_script("arguments[0].click();", input_to_click)
        print("✅ Selected delivery address.")
    except Exception as e:
        print(f"Error selecting delivery address: {e}")
        return

    # Step 3
    try:
        # Click on "Proceed Checkout" button
        proceed_checkout = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-primary.block-order-method--next-btn')))
        driver.execute_script("arguments[0].click();", proceed_checkout)
        print("✅ Proceeded to checkout.")
    except Exception as e:
        print(f"Error clicking proceed checkout button: {e}")
        return

    # Step 4
    '''
    TIMER
    '''
    wait_until_time(timer)

    main_window = driver.current_window_handle

    allow_paypal_payment(driver, main_window)

    pay_with_paypal_2(driver, paypal_email, paypal_password, card_info, personal_info)
    
    # result = pay_with_paypal(driver, paypal_email, paypal_password, card_info, personal_info)
    # while not result:
    #     result = pay_with_paypal(driver, paypal_email, paypal_password, card_info, personal_info)

    driver.close()  # closes PayPal window
    driver.switch_to.window(main_window)


def add_to_cart_if_available(driver, color_name, size_number):
    """
    Attempts to add a product to cart if the specified color and size are available.
    
    Args:
        driver: Selenium WebDriver instance
        color_name (str): Desired product color
        size_number (str): Desired product size
    
    Returns:
        bool: True if product was added to cart, False otherwise
    """
    wait = WebDriverWait(driver, 10)
    try:
        try:
            colors = driver.find_elements(By.CSS_SELECTOR, '.carousel-link-item')
        except:
            print("No colors found.")
            return False
        
        colors = [color.text for color in colors]
        print(colors)

        if color_name not in colors:
            print('[INFO] Available Colors Are: ', colors)
            print(f"Color {color_name} not found in available options")
            return False

        # Find the color block by alt attribute of the image or span text
        color_xpath = f"//table[contains(@class, 'detail-shoppingbag-list-color')]//span[text()='{color_name}']/ancestor::table"
        color_block = wait.until(EC.presence_of_element_located((By.XPATH, color_xpath)))
        print(f"Found color block for color: {color_name}")


        try:
            sizes = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.detail-shoppingbag-list-size-no')))
        except:
            sizes = []

        if sizes:
            sizes = [size.text for size in sizes]
        print(sizes)

        if size_number not in sizes:
            print('[INFO] Available Sizes Are: ', sizes)
            print(f"Size {size_number} not found in available options")
            return False

        # Now find the row for the desired size
        size_row_xpath = f".//td[text()='{size_number}']/parent::tr"
        size_row = color_block.find_element(By.XPATH, size_row_xpath)
        print(f"Found size row for size: {size_number}")

        # Check if "Sold Out" is NOT present
        stock_status = size_row.find_element(By.CLASS_NAME, "detail-shoppingbag-list-size-stock").text.strip()
        print('stock Status', stock_status)

        if stock_status != "Sold Out":
            # Click the button
            add_btn = size_row.find_element(By.CLASS_NAME, "block-variation-add-cart--btn")
            driver.execute_script("arguments[0].click();", add_btn)
            time.sleep(2)  # Wait for the action to complete
            print(f"Clicked 'Add to Shopping Bag' for color: {color_name}, size: {size_number}")
        else:
            print(f"Size {size_number} for color {color_name} is Sold Out.")
            return False

        return True

    except Exception as e:
        print(f"Error processing color '{color_name}' and size '{size_number}': {e}")


def login_improved(driver):
    driver.get('https://shop.visvim.tv/hk/en/shop/customer/menu.aspx')
    wait = WebDriverWait(driver, 20)

    try:
        email_input = wait.until(EC.visibility_of_element_located((By.ID, 'login_uid')))
        password_input = wait.until(EC.visibility_of_element_located((By.ID, 'login_pwd')))
        
        email_input.clear()
        email_input.send_keys('craftbuilder119@gmail.com')
        password_input.clear()
        password_input.send_keys('Guest123')

        # Scroll down with a specific offset to avoid the header
        driver.execute_script("window.scrollBy(0,200);")
        
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-primary.block-login--login')))
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        login_button.click()
        print("Login button clicked.")
    except Exception as e:
        print(f"Login failed: {e}")


def login(driver, username, password):
    """
    Handles the login process to the Visvim store.
    
    Args:
        driver: Selenium WebDriver instance
        username (str): Store account email
        password (str): Store account password
    """
    driver.get('https://shop.visvim.tv/hk/en/shop/customer/menu.aspx')
    wait = WebDriverWait(driver, 10)

    # Fill in login credentials
    try:
        email_input = wait.until(EC.presence_of_element_located((By.ID, 'login_uid')))
        email_input.clear()
        email_input.send_keys(username)
    except Exception as e:
        print(f"Error finding email input: {e}")

    try:
        password_input = wait.until(EC.presence_of_element_located((By.ID, 'login_pwd')))
        password_input.clear()
        password_input.send_keys(password)
    except Exception as e:
        print(f"Error finding password input: {e}")

    # Trigger reCAPTCHA token generation if available.
    try:
        recaptcha_available = driver.execute_script(
            "return typeof ecblib !== 'undefined' && ecblib.recaptcha && ecblib.recaptcha.ReCaptchaExecuteAndSetToken ? true : false"
        )
        if recaptcha_available:
            driver.execute_script("ecblib.recaptcha.ReCaptchaExecuteAndSetToken();")
            try:
                token_elem = wait.until(EC.presence_of_element_located((By.ID, 'id-recaptcha-token')))
                max_wait = 10  # seconds
                for _ in range(max_wait * 10):  # check every 0.1 sec
                    token = token_elem.get_attribute('value')
                    if token and len(token) > 10:
                        break
                    time.sleep(0.1)
                else:
                    print("[ERROR] reCAPTCHA token not set")
                    return None
            except Exception as inner_e:
                print("No reCAPTCHA token found; proceeding if not required.")
        else:
            print("Recaptcha JS not available; skipping recaptcha step.")
    except Exception as e:
        print(f"Error processing reCAPTCHA: {e}")

    try:
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-primary.block-login--login')))
        driver.execute_script("arguments[0].click();", login_button)
        print("Login button clicked.")
    except Exception as e:
        print(f"Error clicking login button: {e}")
    
    try:
        # Wait for Logout element to confirm login success.
        logout_element = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Log Out')]")))
        if logout_element:
            print("✅ Successfully logged in.")
    except Exception as e:
        print("Login did not complete successfully; review the page structure or try again.")
        login(driver, username, password)


def login_via_js(driver):
    driver.get('https://shop.visvim.tv/hk/en/shop/customer/menu.aspx')
    # Wait until the page is fully loaded
    WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
    
    js = """
    // Remove any interfering element that contains "Top Page"
    document.querySelectorAll('*').forEach(el => {
        if (el.textContent && el.textContent.trim().includes("Top Page")) {
            el.style.display = "none";
            console.log("Removed interfering element:", el);
        }
    });

    // Fill in the login credentials
    var emailInput = document.getElementById("login_uid");
    var passwordInput = document.getElementById("login_pwd");
    if(emailInput && passwordInput) {
        emailInput.value = "craftbuilder119@gmail.com";
        passwordInput.value = "Guest123";
        console.log("Credentials set.");
    } else {
        console.error("Login inputs not found.");
    }

    // Click the login button
    var loginButton = document.querySelector(".btn.btn-primary.block-login--login");
    if(loginButton) {
        loginButton.click();
        console.log("Login button clicked.");
    } else {
        console.error("Login button not found.");
    }
    """
    driver.execute_script(js)



'''
Main Code
'''
def main(username, password, product_id, size, color, paypal_email, paypal_password, card_info=None, personal_info=None, timer=None):
    """
    Main function to execute the automated purchase process.
    
    Args:
        username (str): Store account email
        password (str): Store account password
        product_id (list): List of product IDs to purchase
        size (list): List of sizes corresponding to products
        color (list): List of colors corresponding to products
        paypal_email (str): PayPal account email
        paypal_password (str): PayPal account password
        card_info (dict, optional): Credit card information
        personal_info (dict, optional): Personal information for billing
        timer (str, optional): Target time for payment in format "YYYY-MM-DD HH:MM:SS"
    """
    url = "https://shop.visvim.tv/hk/en/shop/g/g"

    # Getting User Data
    product_id = product_id
    color = color   
    size = size   
 
    driver = setup_driver()
    login(driver, username, password)

    # Make payment for each product
    for index, pid in enumerate(product_id):
        full_url = f"{url}{pid}"
        color_ = color[index] if isinstance(color, list) else color
        size_ = size[index] if isinstance(size, list) else size

        driver.get(full_url)
        print(f"🌐 Opening product page: {full_url}")
        if 'is no longer available.' in driver.page_source:
            print(f"❌ Product {pid} is no longer available.")
            continue

        try:
            if add_to_cart_if_available(driver, color_, size_):
                proceed_payment(driver, paypal_email, paypal_password, card_info, personal_info, timer)

            #proceed_payment(driver, paypal_email, paypal_password, card_info, personal_info, timer)

            time.sleep(10)  # Wait for the page to load after selecting color and size

        except Exception as e:
            print(f"Error processing product {pid}: {e}")


    driver.quit()
    