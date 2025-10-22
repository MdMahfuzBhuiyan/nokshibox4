# main_script.py

import time
import random
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException # Import exceptions


# --- Global Settings ---
# Controls the overall speed of the demonstration.
# 1 = Normal speed, 0.5 = Twice as fast, 2 = Half speed.
SPEED_MULTIPLIER = 1


def setup_driver(browser_name):
    """
    Initializes and returns a Selenium WebDriver instance for the specified browser.

    This function uses webdriver-manager to automatically download and manage
    the appropriate driver, making the setup platform-independent.

    Args:
        browser_name (str): The name of the browser to use ('chrome' or 'firefox').

    Returns:
        A Selenium WebDriver instance or None if the browser is not supported.
    """
    try:
        if browser_name.lower() == 'firefox':
            print("Setting up the Selenium WebDriver for Firefox...")
            # Ensure the path uses double backslashes or forward slashes if needed on Windows
            driver_path = GeckoDriverManager().install().replace("\\","\\\\")
            service = FirefoxService(executable_path=driver_path)
            driver = webdriver.Firefox(service=service)
        elif browser_name.lower() == 'chrome':
            print("Setting up the Selenium WebDriver for Chrome...")
             # Ensure the path uses double backslashes or forward slashes if needed on Windows
            driver_path = ChromeDriverManager().install().replace("\\","\\\\")
            service = ChromeService(executable_path=driver_path)
            driver = webdriver.Chrome(service=service)
        else:
            print(f"Unsupported browser: {browser_name}. Please choose 'chrome' or 'firefox'.")
            return None

        print("WebDriver setup successful.")
        return driver
    except Exception as e:
        print(f"Error setting up WebDriver for {browser_name}: {e}")
        return None

def human_type(element, text):
    """
    Types the given text into a web element one character at a time
    to simulate human typing. Also clears the field first.

    Args:
        element: The Selenium web element to type into.
        text (str): The text to type.
    """
    # Clear the field before typing, especially for updates
    try:
        element.clear()
        time.sleep(0.1 * SPEED_MULTIPLIER) # Small pause after clearing
    except Exception as e:
        # It's okay if clear fails on some elements (like file inputs)
        # print(f"Note: Could not clear element before typing. Error: {e}")
        pass # Continue typing anyway

    for char in text:
        element.send_keys(char)
        # Add a short, random delay between keystrokes
        time.sleep(random.uniform(0.01, 0.1) * SPEED_MULTIPLIER)

def fill_signup_form(driver, user_details):
    """
    Finds and fills out the fields in the signup form and submits it.

    Args:
        driver: The Selenium WebDriver instance.
        user_details (dict): A dictionary containing the user's information.
    """
    print(f"Filling out the signup form for role: {user_details['role']}...")

    wait = WebDriverWait(driver, 10)

    try:
        # --- Fill in the form fields with typing effect ---
        human_type(wait.until(EC.presence_of_element_located((By.ID, "id_full_name"))), user_details["full_name"])
        time.sleep(0.5 * SPEED_MULTIPLIER)
        human_type(wait.until(EC.presence_of_element_located((By.ID, "id_mobile_no"))), user_details["mobile_no"])
        time.sleep(0.5 * SPEED_MULTIPLIER)
        human_type(wait.until(EC.presence_of_element_located((By.ID, "id_email"))), user_details["email"])
        time.sleep(0.5 * SPEED_MULTIPLIER)

        # --- Visually handle the dropdown ---
        print("Selecting role from dropdown...")
        role_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "id_role")))
        role_dropdown.click() # Open the dropdown
        time.sleep(1 * SPEED_MULTIPLIER) # Pause to show the options

        # Find and click the specified role option (Use title case as in dropdown)
        role_text = user_details['role'].title() # E.g., 'Seller' or 'Buyer'
        role_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//option[text()='{role_text}']")))
        time.sleep(0.5 * SPEED_MULTIPLIER)
        role_option.click()
        print(f"Role '{role_text}' selected.")

        time.sleep(0.5 * SPEED_MULTIPLIER)

        # --- Fill password fields ---
        human_type(wait.until(EC.presence_of_element_located((By.ID, "id_password1"))), user_details["password"])
        time.sleep(0.5 * SPEED_MULTIPLIER)
        human_type(wait.until(EC.presence_of_element_located((By.ID, "id_password2"))), user_details["password"])

        # --- Upload the photo ---
        # Generate the absolute path from the relative path in the JSON file
        relative_photo_path = user_details["photo"]
        # Ensure the path exists before trying to use it
        if not os.path.isabs(relative_photo_path):
             script_dir = os.path.dirname(__file__) if '__file__' in locals() else os.getcwd()
             absolute_photo_path = os.path.abspath(os.path.join(script_dir, relative_photo_path))
        else:
             absolute_photo_path = relative_photo_path

        if not os.path.exists(absolute_photo_path):
            print(f"⚠️ Warning: Photo file not found at {absolute_photo_path}. Skipping photo upload.")
        else:
            print(f"Uploading photo from: {absolute_photo_path}")
            photo_input = wait.until(EC.presence_of_element_located((By.ID, "id_photo")))
            photo_input.send_keys(absolute_photo_path)
            time.sleep(1 * SPEED_MULTIPLIER)

        # --- Submit the form ---
        print("Submitting the signup form...")
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        submit_button.click()

        print("Form filling and submission complete.")

    except TimeoutException as e:
        print(f"Timeout Error during signup: {e}")
        print("Could not find one of the signup form elements.")
    except Exception as e:
        print(f"An unexpected error occurred during signup form filling: {e}")


def perform_login(driver, user_details):
    """
    Waits for the login page to load, then fills in and submits the login form.

    Args:
        driver: The Selenium WebDriver instance.
        user_details (dict): A dictionary containing the user's email and password.
    """
    print("Performing login...")
    wait = WebDriverWait(driver, 15)

    try:
        # Use 'id_email' and 'id_password' based on your login.html
        email_field = wait.until(EC.presence_of_element_located((By.ID, "id_email")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "id_password")))

        human_type(email_field, user_details["email"])
        time.sleep(0.5 * SPEED_MULTIPLIER)
        human_type(password_field, user_details["password"])
        time.sleep(1 * SPEED_MULTIPLIER)

        print("Submitting the login form...")
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        submit_button.click()

        # Add a wait after login to ensure the next page loads
        WebDriverWait(driver, 10).until(
            EC.any_of(
                EC.url_contains('/seller'),
                EC.url_contains('/buyer'),
                EC.presence_of_element_located((By.ID, "navbar")) # Check if navbar exists
            )
        )
        print("Login successful.")
        time.sleep(1 * SPEED_MULTIPLIER) # Shorter pause after wait

    except TimeoutException:
        print("Login submitted, but redirection took too long or failed.")
        # Check if login form is still present, indicating failure
        try:
             # Check for a unique element on the login page, like the form itself if it has an ID
             driver.find_element(By.ID, "loginForm") # Assuming login form has id 'loginForm' in login.html
             print("Login failed: Still on login page. Check credentials or view logic.")
        except NoSuchElementException:
             print("Could not confirm login success or failure based on page elements.")
    except Exception as e:
        print(f"An unexpected error occurred during login: {e}")


def scroll_seller_homepage(driver):
    """
    Smoothly scrolls to each major section of the seller's homepage for demonstration.
    
    Args:
        driver: The Selenium WebDriver instance.
    """
    print("Starting seller homepage scroll demonstration...")
    wait = WebDriverWait(driver, 10)
    # Corrected IDs based on seller_home.html
    section_ids = [
        ("create-post", "Create New Post"), # Form container ID
        ("MyPost", "My Posts")          # Section container ID
    ]

    for section_id, section_name in section_ids:
        try:
            print(f"Scrolling to '{section_name}' section (ID: {section_id})...")
            section_element = wait.until(EC.visibility_of_element_located((By.ID, section_id)))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", section_element)
            time.sleep(1.5 * SPEED_MULTIPLIER) # Slightly longer pause to view the section
        except Exception as e:
            print(f"Could not scroll to section with ID '{section_id}'. Skipping. Error: {e}")

    print("Scrolling back to the top smoothly...")
    driver.execute_script("window.scrollTo({ top: 0, behavior: 'smooth' });")
    time.sleep(2 * SPEED_MULTIPLIER)

def view_product_details_and_seller_profile(driver, product_to_view):
    """
    After searching, clicks 'View Details' on the first product matching the title,
    then clicks 'Contact with Seller' to view the seller's profile.

    Args:
        driver: The Selenium WebDriver instance.
        product_to_view (str): The exact title of the product to view.
    """
    print("Navigating to product details and then to seller profile...")
    wait = WebDriverWait(driver, 15)
    try:
        # Step 1: Find and click "View Details" for the specific product
        print(f"Finding 'View Details' button for '{product_to_view}'...")
        # More specific XPath: Find the card with the exact title, then the 'View Details' link inside it
        # Adjusted selector based on products.html / buyer_home.html structure
        view_details_xpath = f"//div[contains(@class, 'product-card')][.//h5[normalize-space(text())='{product_to_view}']]/div/a[contains(text(), 'View Details')]"

        view_details_link = wait.until(EC.element_to_be_clickable((By.XPATH, view_details_xpath)))

        # Scroll to the button before clicking to ensure visibility
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", view_details_link)
        time.sleep(0.5 * SPEED_MULTIPLIER)
        view_details_link.click()
        print("Clicked 'View Details'.")

        # Wait for the product detail page to load (check for a unique element ID)
        wait.until(EC.presence_of_element_located((By.ID, "ContactSeller")))
        print("Product detail page loaded.")
        time.sleep(2 * SPEED_MULTIPLIER) # Pause to show the page


        # Step 2: On the product page, find and click "Contact with Seller"
        contact_seller_link = wait.until(EC.element_to_be_clickable((By.ID, "ContactSeller")))
        print("Finding 'Contact with Seller' button...")
        # Scroll to the button before clicking
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", contact_seller_link)
        time.sleep(0.5 * SPEED_MULTIPLIER)
        contact_seller_link.click()
        print("Clicked 'Contact with Seller'. Navigating to profile page.")

        # Add a wait to observe the seller's profile
        wait.until(EC.url_contains('/profile/')) # Wait until profile URL is loaded
        print("Seller profile page loaded.")
        time.sleep(2 * SPEED_MULTIPLIER) # Short pause before next action

    except TimeoutException:
         print(f"Timeout: Could not find 'View Details' for '{product_to_view}' or 'Contact Seller' button. Skipping.")
    except Exception as e:
        print(f"An error occurred while navigating product/profile pages. Error: {e}")

# --- UPDATED FUNCTION ---
def buyer_interact_with_seller_profile(driver):
    """ Buyer scrolls, requests customization, enters text, sends, clicks FB link, then returns. """
    print("Interacting with seller profile...")
    wait = WebDriverWait(driver, 10)
    original_window = driver.current_window_handle
    print(f"Original window handle: {original_window}")
    
    try:
        # --- Request Customization Flow ---
        # Scroll down smoothly to find the button area
        print("Scrolling down seller profile...")
        driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        time.sleep(1.5 * SPEED_MULTIPLIER)
        driver.execute_script("window.scrollBy({ top: -300, behavior: 'smooth'});")
        time.sleep(1 * SPEED_MULTIPLIER)

        # Click "Request for Customization"
        print("Clicking 'Request for Customization'...")
        request_btn = wait.until(EC.element_to_be_clickable((By.ID, "requestBtn")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", request_btn)
        time.sleep(0.5 * SPEED_MULTIPLIER)
        request_btn.click()
        time.sleep(1 * SPEED_MULTIPLIER) # Wait for box to appear

        # Add text to the message box
        print("Typing customization request...")
        message_box = wait.until(EC.visibility_of_element_located((By.ID, "customMessage")))
        human_type(message_box, "Hello, I would like to request a custom version of this product.")
        time.sleep(1 * SPEED_MULTIPLIER) # Pause after typing

        # Click "Send"
        print("Clicking 'Send'...")
        send_btn = wait.until(EC.element_to_be_clickable((By.ID, "sendBtn")))
        send_btn.click()
        time.sleep(2 * SPEED_MULTIPLIER) # Pause after mailto is triggered

        # Switch back to the original tab
        print("Checking for new tabs after request...")
        all_windows = driver.window_handles
        if len(all_windows) > 1:
            print("New tab detected. Closing new tab(s) and switching back...")
            for window_handle in all_windows:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    driver.close()
            driver.switch_to.window(original_window)
            print(f"Switched back to window: {driver.current_window_handle}")
            time.sleep(1 * SPEED_MULTIPLIER)
        else:
            print("No new tab detected, continuing on the current tab.")

        # Verify we are on the profile page
        try:
             WebDriverWait(driver, 5).until(EC.url_contains('/profile/'))
             print("Confirmed back on seller profile page.")
        except TimeoutException:
             print("Warning: Did not confirm return to profile page. Continuing anyway...")
             driver.switch_to.window(original_window) # Re-assert focus

        time.sleep(1 * SPEED_MULTIPLIER)

        # --- NEW: Click Facebook Link ---
        print("Looking for Facebook link...")
        try:
            # Find the link by looking for the one containing the facebook icon class or href
            fb_link_xpath = "//a[contains(@href, 'facebook.com')]" # More general
            fb_link = wait.until(EC.presence_of_element_located((By.XPATH, fb_link_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", fb_link)
            time.sleep(0.5 * SPEED_MULTIPLIER)
            
            print("Clicking Facebook link...")
            fb_link.click()
            time.sleep(3 * SPEED_MULTIPLIER) # Wait for potential new tab to open

            # Check for new tab and verify URL
            print("Checking for Facebook tab...")
            fb_windows = driver.window_handles
            if len(fb_windows) > 1:
                 print("Facebook tab opened. Switching and verifying...")
                 # Find the new window handle
                 new_window = [window for window in fb_windows if window != original_window][0]
                 driver.switch_to.window(new_window)
                 time.sleep(2 * SPEED_MULTIPLIER) # Let FB page load a bit
                 current_fb_url = driver.current_url
                 if "facebook.com" in current_fb_url:
                      print(f"✅ Successfully navigated to Facebook URL: {current_fb_url}")
                 else:
                      print(f"⚠️ Warning: Navigated to unexpected URL: {current_fb_url}")
                 
                 print("Closing Facebook tab and switching back...")
                 driver.close()
                 driver.switch_to.window(original_window)
                 time.sleep(1 * SPEED_MULTIPLIER)
            else:
                 # It might have opened in the same tab (less likely with target="_blank")
                 current_url_after_click = driver.current_url
                 if "facebook.com" in current_url_after_click:
                     print(f"✅ Facebook link opened in the same tab: {current_url_after_click}")
                     print("Navigating back to profile page...")
                     driver.back() # Go back if it opened in the same tab
                     wait.until(EC.url_contains('/profile/')) # Wait to return
                 else:
                     print("Facebook link did not open in a new tab or navigate.")


        except TimeoutException:
            print("Facebook link not found on the profile page. Skipping click.")
        except Exception as fb_e:
            print(f"An error occurred while clicking/verifying Facebook link: {fb_e}")
            # Ensure switch back if something went wrong
            if driver.current_window_handle != original_window:
                 try:
                     print("Attempting to switch back to original window after FB error...")
                     driver.switch_to.window(original_window)
                 except Exception as switch_err:
                      print(f"Could not switch back after FB error: {switch_err}")
        # --- END NEW ---


        time.sleep(2 * SPEED_MULTIPLIER) # Final pause on profile page
        print("Seller profile interaction complete.")

    except TimeoutException as e:
         print(f"Timeout: Could not find element during profile interaction. {e}")
         print("Maybe 'Request for Customization' button, text box, or send button not found?")
    except Exception as e:
        print(f"An error occurred during seller profile interaction: {e}")


def fill_contact_form_and_send(driver):
    """ Navigates to contact page, fills form, clicks Email."""
    print("Navigating to Contact Us page...")
    wait = WebDriverWait(driver, 10)
    original_window_contact = driver.current_window_handle # Store before potential new tabs
    try:
        # Find and click the 'Contact Us' link in the navbar
        # Use a more robust selector that finds the link by text within the navbar
        contact_xpath = "//nav[@id='navbar']//a[normalize-space()='Contact Us']"
        contact_link = wait.until(EC.element_to_be_clickable((By.XPATH, contact_xpath)))
        contact_link.click()
        wait.until(EC.url_contains('/contact/'))
        print("On Contact Us page. Filling form...")

        # Fill form fields
        human_type(wait.until(EC.presence_of_element_located((By.ID, "email"))), "test.buyer@example.com")
        time.sleep(0.5 * SPEED_MULTIPLIER)
        human_type(wait.until(EC.presence_of_element_located((By.ID, "phone"))), "01234567890")
        time.sleep(0.5 * SPEED_MULTIPLIER)
        human_type(wait.until(EC.presence_of_element_located((By.ID, "message"))), "This is a test message from Selenium.")
        time.sleep(1 * SPEED_MULTIPLIER)

        # Click the Email button
        print("Clicking the Email button...")
        email_button_xpath = "//button[contains(@onclick, 'sendViaEmail')]" # Find button by onclick
        email_button = wait.until(EC.element_to_be_clickable((By.XPATH, email_button_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", email_button)
        time.sleep(0.5 * SPEED_MULTIPLIER)
        email_button.click()

        print("Pausing to observe mail action...")
        time.sleep(5 * SPEED_MULTIPLIER)

        # Switch back logic for contact form email
        print("Checking for new tabs after contact email...")
        all_windows_contact = driver.window_handles
        print(f"Current window handles: {all_windows_contact}")
        if len(all_windows_contact) > 1:
            print("New tab detected. Closing new tab(s) and switching back...")
            for window_handle in all_windows_contact:
                if window_handle != original_window_contact:
                    driver.switch_to.window(window_handle)
                    driver.close()
            driver.switch_to.window(original_window_contact)
            print(f"Switched back to window: {driver.current_window_handle}")
            time.sleep(1 * SPEED_MULTIPLIER)
        else:
            print("No new tab detected after contact email.")

        print("Contact form interaction complete.")

    except TimeoutException as e:
         print(f"Timeout Error during contact form interaction: {e}")
         print("Could not find Contact Us link, form fields, or Email button.")
    except Exception as e:
        print(f"An error occurred during contact form interaction: {e}")

# --- NEW FUNCTION ---
def final_navigation_and_scroll(driver, home_url):
    """Clicks Home, scrolls, clicks About Us, scrolls."""
    print("Starting final navigation and scroll sequence...")
    wait = WebDriverWait(driver, 10)
    
    try:
        # --- Go Home ---
        print("Navigating to Home page...")
        # Use a reliable selector for the Home link (main logo or nav link)
        try:
            # Try the logo first
            home_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//nav[@id='navbar']//a[contains(@class, 'text-5xl')]")))
        except TimeoutException:
            # Fallback to nav link
            home_link_xpath = "//nav[@id='navbar']//ul//a[normalize-space()='Home']"
            home_link = wait.until(EC.element_to_be_clickable((By.XPATH, home_link_xpath)))
            
        home_link.click()
        # Wait for home page - check for a unique element or URL
        # Using URL check which seems more reliable based on structure
        wait.until(EC.url_to_be(home_url + "/")) # Wait for exact home URL
        print("On Home page. Scrolling...")
        time.sleep(1 * SPEED_MULTIPLIER)

        # Scroll down and up
        print("Scrolling down Home page...")
        driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        time.sleep(2.5 * SPEED_MULTIPLIER)
        print("Scrolling up Home page...")
        driver.execute_script("window.scrollTo({ top: 0, behavior: 'smooth' });")
        time.sleep(2 * SPEED_MULTIPLIER)

        # --- Go About Us ---
        print("Navigating to About Us page...")
        about_link = wait.until(EC.element_to_be_clickable((By.ID, "AboutUs"))) # Use the ID from base.html
        about_link.click()
        wait.until(EC.url_contains('/about/')) # Wait for about page URL
        print("On About Us page. Scrolling...")
        time.sleep(1 * SPEED_MULTIPLIER)

        # Scroll down and up
        print("Scrolling down About Us page...")
        driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        time.sleep(2.5 * SPEED_MULTIPLIER)
        print("Scrolling up About Us page...")
        driver.execute_script("window.scrollTo({ top: 0, behavior: 'smooth' });")
        time.sleep(2 * SPEED_MULTIPLIER)

        print("Final navigation and scroll complete.")

    except TimeoutException as e:
        print(f"Timeout Error during final navigation: {e}")
        print("Could not find Home or About Us link, or page did not load correctly.")
    except Exception as e:
        print(f"An error occurred during final navigation: {e}")


def create_product_post(driver, product_details):
    """
    Fills out and submits the form to create a new product post.

    Args:
        driver: The Selenium WebDriver instance.
        product_details (dict): A dictionary with the product's information.
    """
    print(f"Creating a new post for product: {product_details['title']}...")
    wait = WebDriverWait(driver, 10)

    try:
        # --- Fill in the text fields ---
        human_type(wait.until(EC.presence_of_element_located((By.ID, "id_title"))), product_details["title"])
        time.sleep(0.5 * SPEED_MULTIPLIER)
        human_type(wait.until(EC.presence_of_element_located((By.ID, "id_details"))), product_details["details"])
        time.sleep(0.5 * SPEED_MULTIPLIER)
        human_type(wait.until(EC.presence_of_element_located((By.ID, "id_price"))), product_details["price"])
        time.sleep(0.5 * SPEED_MULTIPLIER)
        
        # --- Select the category from the dropdown ---
        print("Selecting product category...")
        category_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "id_category")))
        category_dropdown.click()
        time.sleep(1 * SPEED_MULTIPLIER)
        
        # Use category name from JSON
        category_name = product_details["category"]
        category_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//option[normalize-space()='{category_name}']")))
        category_option.click()
        print(f"Category '{category_name}' selected.")
        time.sleep(0.5 * SPEED_MULTIPLIER)
        
        # --- Upload the product image ---
        relative_image_path = product_details["image"]
        if not os.path.isabs(relative_image_path):
             script_dir = os.path.dirname(__file__) if '__file__' in locals() else os.getcwd()
             absolute_image_path = os.path.abspath(os.path.join(script_dir, relative_image_path))
        else:
            absolute_image_path = relative_image_path

        if not os.path.exists(absolute_image_path):
             print(f"⚠️ Warning: Product image file not found at {absolute_image_path}. Skipping image upload.")
        else:
             print(f"Uploading product image from: {absolute_image_path}")
             image_input = wait.until(EC.presence_of_element_located((By.ID, "id_image")))
             image_input.send_keys(absolute_image_path)
             time.sleep(1 * SPEED_MULTIPLIER)
        
        # --- Submit the post ---
        print("Submitting the new post...")
        # Target the submit button within the form more specifically if needed
        # Looking for the button with text POST inside the form in seller_home.html
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//form//button[normalize-space()='POST']")))
        submit_button.click()
        print("Product post submitted.")
        # Wait for redirect back to seller home
        wait.until(EC.url_contains('/seller'))
        print("Product post created successfully.")

    except TimeoutException as e:
         print(f"Timeout Error during product creation: {e}")
         print("Could not find form fields, category dropdown/option, or submit button.")
    except Exception as e:
        print(f"An error occurred during product post creation: {e}")


def edit_product_post(driver, product_title, updated_details):
    """
    Finds the edit button for a product, navigates to the edit page,
    updates the price and image, then submits.
    
    Args:
        driver: The Selenium WebDriver instance.
        product_title (str): The title of the product to find and edit.
        updated_details (dict): A dictionary with the new price and image path.
    """
    print("Starting product edit process...")
    wait = WebDriverWait(driver, 10)

    try:
        # --- Find and click the 'Edit' button ---
        print(f"Finding the 'Edit' button for '{product_title}'...")
        # More specific XPath targeting the link based on product title in the card in seller_home.html
        edit_button_xpath = f"//div[contains(@class, 'product-card')][.//h3[normalize-space(text())='{product_title}']]/div/div/a[contains(text(), 'Edit')]"
        edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, edit_button_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", edit_button) # Ensure visibility
        time.sleep(0.5 * SPEED_MULTIPLIER)
        edit_button.click()
        print("Navigating to the edit page...")

        # --- Wait for edit page and perform updates ---
        wait.until(EC.url_contains('/edit/'))
        print("Edit page loaded. Updating details...")

        # --- Update Price ---
        price_field = wait.until(EC.presence_of_element_located((By.ID, "id_price")))
        print(f"Updating price to: {updated_details['price']}")
        # Use human_type which includes clear()
        human_type(price_field, updated_details["price"])
        time.sleep(0.5 * SPEED_MULTIPLIER) # Reduced pause after typing

        # --- Upload new photo ---
        relative_image_path = updated_details["image"]
        # Ensure path exists
        if not os.path.isabs(relative_image_path):
             script_dir = os.path.dirname(__file__) if '__file__' in locals() else os.getcwd()
             absolute_image_path = os.path.abspath(os.path.join(script_dir, relative_image_path))
        else:
             absolute_image_path = relative_image_path

        if not os.path.exists(absolute_image_path):
             print(f"⚠️ Warning: New image file not found at {absolute_image_path}. Skipping image update.")
        else:
             print(f"Uploading new product image from: {absolute_image_path}")
             image_input = wait.until(EC.presence_of_element_located((By.ID, "id_image")))
             image_input.send_keys(absolute_image_path)
             time.sleep(1 * SPEED_MULTIPLIER) # Pause after selecting file

        # --- FIX: Add longer pause before submitting ---
        print("Pausing before submitting changes...")
        time.sleep(2 * SPEED_MULTIPLIER) # Wait 2 seconds for image upload to potentially register

        # --- Submit the form ---
        print("Submitting the updated post...")
        # More specific submit button selector for edit page
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//form//button[contains(text(), 'Save Changes')]")))
        submit_button.click()
        print("Product post update submitted.")

        # --- Wait for redirect back to seller home ---
        wait.until(EC.url_contains('/seller'))
        print("Returned to seller homepage after edit.")
        time.sleep(1 * SPEED_MULTIPLIER) # Pause to let page settle


    except TimeoutException as e:
         print(f"Timeout Error during product edit: {e}")
         print(f"Could not find edit button for '{product_title}', form fields, or submit button.")
    except Exception as e:
        print(f"An error occurred during the product edit process: {e}")


def verify_product_price(driver, product_title, expected_price):
     """
     Scrolls to 'My Posts', finds the product, and verifies its displayed price.

     Args:
         driver: The Selenium WebDriver instance.
         product_title (str): The title of the product to check.
         expected_price (str): The expected price string (e.g., "19.99").
     Returns:
         bool: True if the price matches, False otherwise.
     """
     print(f"Verifying price for '{product_title}'. Expected: Tk {expected_price}")
     wait = WebDriverWait(driver, 10)
     try:
          # Scroll to My Posts section first
          my_posts_section = wait.until(EC.visibility_of_element_located((By.ID, "MyPost")))
          driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", my_posts_section)
          time.sleep(1.5 * SPEED_MULTIPLIER) # Wait for scroll and content

          # Find the specific product card
          product_card_xpath = f"//div[contains(@class, 'product-card')][.//h3[normalize-space(text())='{product_title}']]"
          product_card = wait.until(EC.visibility_of_element_located((By.XPATH, product_card_xpath)))

          # Find the price element within that card (using updated HTML structure from seller_home.html)
          price_element_xpath = ".//p[contains(text(), 'Tk')]"
          price_element = product_card.find_element(By.XPATH, price_element_xpath)
          actual_price_text = price_element.text
          print(f"Found displayed price text: '{actual_price_text}'")

          # Extract only the number part for comparison
          actual_price = actual_price_text.replace('Tk', '').strip()

          if actual_price == expected_price:
               print(f"✅ Price verification successful for '{product_title}'!")
               return True
          else:
               print(f"❌ Price verification FAILED for '{product_title}'. Expected 'Tk {expected_price}', but found '{actual_price_text}'.")
               return False

     except (TimeoutException, NoSuchElementException) as e:
          print(f"Error finding product '{product_title}' or its price for verification. {e}")
          return False
     except Exception as e:
          print(f"An unexpected error occurred during price verification: {e}")
          return False


def delete_product_if_exists(driver, product_title):
    """
    Checks if a product exists in 'My Posts' and deletes it if found.

    Args:
        driver: The Selenium WebDriver instance.
        product_title (str): The title of the product to delete.
    """
    print(f"Checking if product '{product_title}' exists and deleting if found...")
    wait = WebDriverWait(driver, 5) # Use a shorter wait, as it might not exist

    try:
        # Ensure we are on the seller homepage
        if '/seller' not in driver.current_url:
            print("Not on seller homepage. Skipping deletion check.")
            return # Or navigate to seller home if preferred

        # Scroll to My Posts to make sure elements are loaded
        my_posts_section = wait.until(EC.visibility_of_element_located((By.ID, "MyPost")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", my_posts_section)
        time.sleep(1 * SPEED_MULTIPLIER)

        # Find the delete button form specifically for this product (updated xpath based on seller_home.html)
        delete_button_xpath = f"//div[contains(@class, 'product-card')][.//h3[normalize-space(text())='{product_title}']]/div/div/form[contains(@action, '/delete/')]//button"
        
        # Use find_elements to check presence without failing immediately
        delete_buttons = driver.find_elements(By.XPATH, delete_button_xpath)

        if delete_buttons:
            print(f"Product '{product_title}' found. Proceeding with deletion...")
            delete_button = delete_buttons[0] # Get the first match
            
            # Scroll to the button just in case
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", delete_button)
            time.sleep(0.5 * SPEED_MULTIPLIER)
            
            # Click the delete button - this should trigger the JS confirm
            delete_button.click()
            
            # Handle the confirmation alert
            print("Handling delete confirmation alert...")
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()
            print("Delete confirmed.")
            
            # Wait for the page to potentially reload or update after deletion
            # Wait until the old button is gone from the DOM
            wait.until(EC.staleness_of(delete_button)) 
            print(f"Product '{product_title}' deleted successfully.")
            time.sleep(2 * SPEED_MULTIPLIER) # Pause after deletion
        else:
            print(f"Product '{product_title}' not found in 'My Posts'. No deletion needed.")

    except TimeoutException:
        # This is okay, means the product wasn't found or alert didn't appear as expected
        print(f"Product '{product_title}' not found or alert confirmation issue. No deletion action taken.")
    except NoAlertPresentException:
         print("Warning: Delete button clicked, but no confirmation alert appeared.")
         # Assume deleted or handle differently if needed
         time.sleep(1 * SPEED_MULTIPLIER)
    except Exception as e:
        print(f"An error occurred during the deletion check/process for '{product_title}': {e}")
        # Optionally handle alert dismissal if it popped up unexpectedly
        try:
            driver.switch_to.alert.dismiss()
            print("Dismissed unexpected alert during deletion.")
        except NoAlertPresentException:
            pass # No alert was present


def edit_seller_profile(driver, user_name, new_user_details):
    """
    Navigates to the seller's profile edit page and updates the full name
    and adds a Facebook link.

    Args:
        driver: The Selenium WebDriver instance.
        user_name (str): The original full name used to find the dropdown button if needed.
        new_user_details (dict): A dictionary containing the updated full name.
    """
    print("Starting seller profile edit process...")
    wait = WebDriverWait(driver, 15)
    try:
        # Step 1: Open the dropdown menu using a more robust selector
        print("Finding dropdown button...")
        try:
            dropdown_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.relative > img.cursor-pointer[onclick*='dropdown-menu']")))
        except TimeoutException:
            print("Image dropdown not found, trying placeholder div...")
            dropdown_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.relative > div.cursor-pointer[onclick*='dropdown-menu']")))
        except Exception as e_find:
             print(f"Error finding dropdown button: {e_find}")
             try:
                 print("Trying base.html dropdown selector...")
                 base_dropdown_selector = "button.flex.items-center.space-x-2"
                 dropdown_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, base_dropdown_selector)))
             except Exception as e_fallback:
                 print(f"All dropdown selectors failed: {e_fallback}")
                 raise

        dropdown_button.click()
        time.sleep(1 * SPEED_MULTIPLIER)

        # Step 2: Click the 'Profile' link within the now visible dropdown
        try:
             profile_link_xpath = "//div[@id='dropdown-menu']//a[normalize-space()='Profile']"
             profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, profile_link_xpath)))
        except TimeoutException:
             print("Trying base.html profile link selector...")
             profile_link_xpath_base = "//div[contains(@class, 'dropdown-menu')]//a[normalize-space()='Profile']"
             profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, profile_link_xpath_base)))

        profile_link.click()
        print("Navigating to profile page...")
        wait.until(EC.url_contains('/profile/'))
        
        # Step 3: Click the 'Edit Profile' link on the profile page
        print('Waiting for profile page to load...')
        edit_profile_link = wait.until(EC.element_to_be_clickable((By.ID, "EditProfile")))
        edit_profile_link.click()
        print("Navigating to edit profile page...")
        wait.until(EC.url_contains('/edit/'))
        print("Edit profile page loaded.")
        
        # Step 4: Change the name
        name_field = wait.until(EC.presence_of_element_located((By.ID, "id_full_name")))
        human_type(name_field, new_user_details["full_name"]) # human_type includes clear()
        time.sleep(0.5 * SPEED_MULTIPLIER)

        # --- NEW: Add Facebook Link ---
        try:
            print("Adding Facebook link...")
            facebook_field = wait.until(EC.presence_of_element_located((By.ID, "id_facebook_link")))
            # Generate a simple placeholder link
            placeholder_fb_link = f"https://facebook.com/testprofile{random.randint(100,999)}"
            human_type(facebook_field, placeholder_fb_link)
            print(f"Entered Facebook link: {placeholder_fb_link}")
            time.sleep(0.5 * SPEED_MULTIPLIER)
        except TimeoutException:
            print("Facebook link field not found (maybe not a seller?). Skipping.")
        # --- END NEW ---
        
        # Step 5: Submit
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//form//button[contains(text(), 'Save Changes')]")))
        submit_button.click()
        print("Profile update submitted.")
        # Wait for redirect back to profile
        wait.until(EC.url_contains('/profile/'))
        print("Profile updated successfully.")


    except TimeoutException as e:
         print(f"Timeout Error during profile edit: {e}")
         print("Could not find dropdown, profile link, edit link, form field, or submit button.")
    except Exception as e:
        print(f"An error occurred during the profile edit process: {e}")


def scroll_to_my_products(driver):
    """
    Scrolls smoothly to the 'My Posts' section on the page to show a new product.

    Args:
        driver: The Selenium WebDriver instance.
    """
    print("Scrolling to the 'My Posts' section...")
    wait = WebDriverWait(driver, 10)
    try:
        # Using the specific ID for the 'My Posts' section from seller_home.html
        my_posts_section = wait.until(EC.visibility_of_element_located((By.ID, "MyPost")))
        
        # Scroll the element into the middle of the view for better visibility
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", my_posts_section)
        print("Successfully scrolled to 'My Posts' section.")
        time.sleep(3 * SPEED_MULTIPLIER) # Pause to view the new product
    except Exception as e:
        # Corrected ID in error message
        print(f"Could not find or scroll to the 'My Posts' section with ID 'MyPost'. Error: {e}")


def search_for_product(driver, product_to_search):
    """
    Finds the search bar, types the product name, and lets JS filter.

    Args:
        driver: The Selenium WebDriver instance.
        product_to_search (str): The name of the product to search for.
    """
    print(f"Searching for product: '{product_to_search}'...")
    wait = WebDriverWait(driver, 10)
    try:
        search_bar = wait.until(EC.presence_of_element_located((By.ID, "searchBar")))
        human_type(search_bar, product_to_search) # human_type includes clear()
        time.sleep(0.5 * SPEED_MULTIPLIER)
        # Your base.html JS triggers search on keyup, no need for Enter
        print("Search text entered, allowing time for filtering...")
        # Add a pause to allow search results JS to filter
        time.sleep(2 * SPEED_MULTIPLIER)
    except Exception as e:
        print(f"Could not find or interact with the search bar. Error: {e}")


def demonstrate_seller_flow(driver, user_data, product_data):
    """Orchestrates the entire demonstration for the seller."""
    home_url = "http://127.0.0.1:8000"
    signup_url = f"{home_url}/signup/"
    login_url = f"{home_url}/login/"
    login_url_fragment = "login"
    seller_home_url_fragment = "/seller" # Target URL after seller login
    create_post_section_id = "create-post" # ID from seller_home.html

    original_product = product_data["candle_art"]
    updated_product = product_data["candle_art_updated"]
    # Determine the title to delete (could be original or updated from previous run)
    title_to_delete = updated_product.get("title", original_product["title"])

    driver.get(home_url)
    driver.maximize_window()
    time.sleep(1 * SPEED_MULTIPLIER)

    print(f"Navigating to signup page: {signup_url}")
    driver.get(signup_url)
    
    fill_signup_form(driver, user_data["seller"])
    
    # --- Check URL after signup ---
    print("Signup submitted. Checking current URL...")
    time.sleep(2 * SPEED_MULTIPLIER)
    current_url = driver.current_url

    if "signup" in current_url.lower():
        print("Still on signup page. Signup likely failed (e.g., user already exists).")
        print("Proceeding directly to login page...")
        driver.get(login_url)
    else:
        print("Redirect detected. Waiting for login page to fully load...")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.any_of(
            EC.url_contains(login_url_fragment),
            EC.presence_of_element_located((By.ID, "id_email")) # Check for login form element
        ))
        print("Redirected to login page successfully.")

    perform_login(driver, user_data["seller"]) # This function now includes waits

    print("Waiting for seller homepage to load...")
    wait = WebDriverWait(driver, 15)
    wait.until(EC.url_contains(seller_home_url_fragment)) # Wait for seller home URL
    print("Seller homepage loaded.")

    # --- >>> ADD DELETION STEP HERE <<< ---
    delete_product_if_exists(driver, title_to_delete)
    # --- >>> END DELETION STEP <<< ---
    
    # --- Product Creation/Edit Logic ---
    try:
        # Ensure create post section exists before proceeding
        wait.until(EC.visibility_of_element_located((By.ID, create_post_section_id)))
        
        # Scroll to create post form and create the initial product
        create_post_section = driver.find_element(By.ID, create_post_section_id)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", create_post_section)
        time.sleep(1 * SPEED_MULTIPLIER)
        
        create_product_post(driver, original_product) # This function waits for redirect
        print("Returned to seller homepage after creating post.")

        # Verify the initial price
        verify_product_price(driver, original_product["title"], original_product["price"])
        
        # Edit the product
        edit_product_post(driver, original_product["title"], updated_product) # This function waits for redirect

        # Verify the updated price
        # Make sure to use the correct title for verification if it also changed
        verify_title = updated_product.get("title", original_product["title"])
        verify_product_price(driver, verify_title, updated_product["price"])

    except TimeoutException:
        print("Could not find create post section or elements. Skipping product creation/edit steps.")
    except Exception as e:
         print(f"An error occurred during product creation/edit flow: {e}")


    # --- EDIT THE SELLER'S PROFILE ---
    # Make sure we are on a page where the dropdown exists (e.g., seller home)
    if seller_home_url_fragment in driver.current_url:
         edit_seller_profile(driver, user_data["seller"]["full_name"], user_data["seller_updated"])
         # edit_seller_profile waits for redirect to profile page
         print("Returned to profile page after edit. Pausing to observe.")
         time.sleep(3 * SPEED_MULTIPLIER) # Reduced pause
    else:
         print("Not on seller homepage, skipping profile edit.")

    # --- FINAL NAVIGATION REMOVED FROM SELLER ---
    # final_navigation_and_scroll(driver, home_url)

    print("--- Seller Demonstration Finished ---")


def demonstrate_buyer_flow(driver, user_data, product_data):
    """Orchestrates the entire demonstration for the buyer."""
    home_url = "http://127.0.0.1:8000"
    signup_url = f"{home_url}/signup/"
    login_url = f"{home_url}/login/"
    login_url_fragment = "login"
    buyer_home_url_fragment = "/buyer" # Assuming this is the buyer redirect URL

    driver.get(signup_url)
    driver.maximize_window()
    
    fill_signup_form(driver, user_data["buyer"])

    # --- Check URL after signup ---
    print("Signup submitted. Checking current URL...")
    time.sleep(2 * SPEED_MULTIPLIER)
    current_url = driver.current_url

    if "signup" in current_url.lower():
        print("Still on signup page. Signup likely failed (e.g., user already exists).")
        print("Proceeding directly to login page...")
        driver.get(login_url)
    else:
        print("Redirect successful. Waiting for login page to fully load...")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.any_of(
            EC.url_contains(login_url_fragment),
            EC.presence_of_element_located((By.ID, "id_email")) # Check for login form element
        ))
        print("Redirected to login page successfully.")
    
    perform_login(driver, user_data["buyer"]) # This function now includes waits

    print("Waiting for buyer homepage to load...")
    wait = WebDriverWait(driver, 15)
    wait.until(EC.url_contains(buyer_home_url_fragment)) # Wait for buyer home URL
    wait.until(EC.presence_of_element_located((By.ID, "searchBar"))) # Ensure search bar is there
    print("Buyer homepage loaded.")
    
    # --- Get the correct product title to search ---
    # Use updated title if available, otherwise original
    product_title_to_search = product_data.get("candle_art_updated", {}).get("title") or product_data.get("candle_art", {}).get("title")

    if product_title_to_search:
        search_for_product(driver, product_title_to_search)
        view_product_details_and_seller_profile(driver, product_title_to_search)
        # Interact with seller profile (scroll, request customization, send, switch back tab, click FB link)
        buyer_interact_with_seller_profile(driver)
    else:
        print("⚠️ Warning: Could not find 'title' for candle_art or candle_art_updated in products.json. Skipping product search and seller profile interaction.")

    # Go to contact us, fill form, click Email
    fill_contact_form_and_send(driver)

    # --- FINAL NAVIGATION ---
    final_navigation_and_scroll(driver, home_url) # Pass home_url

    print("--- Buyer Demonstration Finished ---")


if __name__ == "__main__":
    all_user_data = None
    all_product_data = None
    
    try:
        # Assuming JSON files are in the same directory as the script
        script_dir = os.path.dirname(__file__) if '__file__' in locals() else os.getcwd() # Handle if run interactively
        signup_path = os.path.join(script_dir, 'signup.json')
        products_path = os.path.join(script_dir, 'products.json')

        print(f"Looking for signup.json at: {signup_path}")
        print(f"Looking for products.json at: {products_path}")

        with open(signup_path, 'r') as f:
            all_user_data = json.load(f)
        with open(products_path, 'r') as f:
            all_product_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Required JSON file not found - {e}. Please ensure both signup.json and products.json exist in the same directory as the script: {script_dir}")
        exit() # Exit if files are missing
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from a file. Please check for syntax errors. Details: {e}")
        exit() # Exit if JSON is invalid
    except Exception as e:
        print(f"An unexpected error occurred reading the JSON files: {e}")
        exit()


    if all_user_data and all_product_data:
        browser_choice = "chrome" # Hardcoded for simplicity
        
        # --- SELLER FLOW ---
        seller_driver = None
        try:
            print("--- Initializing Seller Session ---")
            seller_driver = setup_driver(browser_choice)
            if seller_driver:
                demonstrate_seller_flow(seller_driver, all_user_data, all_product_data)
        except Exception as e:
            print(f"An unexpected error occurred during the seller demonstration: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if seller_driver:
                print("Closing seller browser.")
                seller_driver.quit()
        
        # --- BUYER FLOW ---
        buyer_driver = None
        try:
            print("\n--- Initializing Buyer Session ---")
            buyer_driver = setup_driver(browser_choice)
            if buyer_driver:
                demonstrate_buyer_flow(buyer_driver, all_user_data, all_product_data)
        except Exception as e:
            print(f"An unexpected error occurred during the buyer demonstration: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if buyer_driver:
                print("Closing buyer browser.")
                buyer_driver.quit()
            
        print("\nFull demonstration complete.")