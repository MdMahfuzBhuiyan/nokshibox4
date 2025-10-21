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
            driver_path = GeckoDriverManager().install()
            service = FirefoxService(executable_path=driver_path)
            driver = webdriver.Firefox(service=service)
        elif browser_name.lower() == 'chrome':
            print("Setting up the Selenium WebDriver for Chrome...")
            driver_path = ChromeDriverManager().install()
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
    to simulate human typing.

    Args:
        element: The Selenium web element to type into.
        text (str): The text to type.
    """
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

    # Find and click the specified role option
    role_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//option[text()='{user_details['role']}']")))
    time.sleep(0.5 * SPEED_MULTIPLIER)
    role_option.click()
    print(f"Role '{user_details['role']}' selected.")

    time.sleep(0.5 * SPEED_MULTIPLIER)

    # --- Fill password fields ---
    human_type(wait.until(EC.presence_of_element_located((By.ID, "id_password1"))), user_details["password"])
    time.sleep(0.5 * SPEED_MULTIPLIER)
    human_type(wait.until(EC.presence_of_element_located((By.ID, "id_password2"))), user_details["password"])

    # --- Upload the photo ---
    # Generate the absolute path from the relative path in the JSON file
    relative_photo_path = user_details["photo"]
    absolute_photo_path = os.path.abspath(relative_photo_path)

    print(f"Uploading photo from: {absolute_photo_path}")
    photo_input = wait.until(EC.presence_of_element_located((By.ID, "id_photo")))
    photo_input.send_keys(absolute_photo_path)
    time.sleep(1 * SPEED_MULTIPLIER)

    # --- Submit the form ---
    print("Submitting the signup form...")
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    submit_button.click()

    print("Form filling and submission complete.")

def perform_login(driver, user_details):
    """
    Waits for the login page to load, then fills in and submits the login form.

    Args:
        driver: The Selenium WebDriver instance.
        user_details (dict): A dictionary containing the user's email and password.
    """
    print("Performing login...")
    wait = WebDriverWait(driver, 15)

    # Use 'id_username' as it is the Django default for the login form's username/email field
    email_field = wait.until(EC.presence_of_element_located((By.ID, "id_email")))
    password_field = wait.until(EC.presence_of_element_located((By.ID, "id_password")))

    human_type(email_field, user_details["email"])
    time.sleep(0.5 * SPEED_MULTIPLIER)
    human_type(password_field, user_details["password"])
    time.sleep(1 * SPEED_MULTIPLIER)

    print("Submitting the login form...")
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    submit_button.click()
    print("Login successful.")
    time.sleep(2 * SPEED_MULTIPLIER)

def scroll_seller_homepage(driver):
    """
    Smoothly scrolls to each major section of the seller's homepage for demonstration.
    
    Args:
        driver: The Selenium WebDriver instance.
    """
    print("Starting homepage scroll demonstration...")
    wait = WebDriverWait(driver, 10)
    section_ids = [
        ("PostProduct", "Create New Post"),
        ("MyPost", "My Posts")
    ]

    for section_id, section_name in section_ids:
        try:
            print(f"Scrolling to '{section_name}' section...")
            section_element = wait.until(EC.visibility_of_element_located((By.ID, section_id)))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", section_element)
            time.sleep(1 * SPEED_MULTIPLIER) # Pause to view the section
        except Exception as e:
            print(f"Could not scroll to section with ID '{section_id}'. Skipping. Error: {e}")

    print("Scrolling back to the top smoothly...")
    driver.execute_script("window.scrollTo({ top: 0, behavior: 'smooth' });")
    time.sleep(2 * SPEED_MULTIPLIER)

def view_product_details_and_seller_profile(driver, product_to_view):
    """
    After searching, clicks 'View Details' on the first product,
    then clicks 'Contact with Seller' to view the seller's profile.

    Args:
        driver: The Selenium WebDriver instance.
    """
    print("Navigating to product details and then to seller profile...")
    wait = WebDriverWait(driver, 15)
    try:
        # Step 1: Find and click "View Details"
        print("Finding 'View Details' button...")
        # Using XPath to find the first link containing the text "View Details"
        view_details_link = wait.until(EC.element_to_be_clickable((
            By.XPATH, f"//div[contains(@class, 'product-card')][contains(., '{product_to_view}')]//a"
)       ))
        view_details_link.click()
        print("Clicked 'View Details'.")

        time.sleep(2 * SPEED_MULTIPLIER) # Pause to show the page


        # Step 2: On the product page, find and click "Contact with Seller"
        print("Waiting for product details page to load...")
        contact_seller_link = wait.until(EC.element_to_be_clickable(
            (By.ID, "ContactSeller")
        ))
        print("Product details page loaded. Finding 'Contact with Seller' button...")
        contact_seller_link.click()
        print("Clicked 'Contact with Seller'. Navigating to profile page.")

        # Add a pause to observe the seller's profile
        time.sleep(5 * SPEED_MULTIPLIER)
        print("Seller profile page demonstration complete.")

    except Exception as e:
        print(f"An error occurred while navigating product/profile pages. Error: {e}")

def create_product_post(driver, product_details):
    """
    Fills out and submits the form to create a new product post.

    Args:
        driver: The Selenium WebDriver instance.
        product_details (dict): A dictionary with the product's information.
    """
    print(f"Creating a new post for product: {product_details['title']}...")
    wait = WebDriverWait(driver, 10)

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
    
    category_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//option[text()='{product_details['category']}']")))
    category_option.click()
    print(f"Category '{product_details['category']}' selected.")
    time.sleep(0.5 * SPEED_MULTIPLIER)
    
    # --- Upload the product image ---
    relative_image_path = product_details["image"]
    absolute_image_path = os.path.abspath(relative_image_path)
    print(f"Uploading product image from: {absolute_image_path}")
    image_input = wait.until(EC.presence_of_element_located((By.ID, "id_image")))
    image_input.send_keys(absolute_image_path)
    time.sleep(1 * SPEED_MULTIPLIER)
    
    # --- Submit the post ---
    print("Submitting the new post...")
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    submit_button.click()
    print("Product post created successfully.")

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
        edit_button_xpath = f"//div[contains(@class, 'product-card')][contains(., '{product_title}')]//a[contains(@href, '/edit/')]"
        edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, edit_button_xpath)))
        edit_button.click()
        print("Navigating to the edit page...")

        # --- Wait for edit page and perform updates ---
        wait.until(EC.url_contains('/edit/'))
        print("Edit page loaded. Updating details...")

        # --- Update Price ---
        price_field = wait.until(EC.presence_of_element_located((By.ID, "id_price")))
        price_field.clear()
        human_type(price_field, updated_details["price"])
        time.sleep(1.5 * SPEED_MULTIPLIER)

        # --- Upload new photo ---
        relative_image_path = updated_details["image"]
        absolute_image_path = os.path.abspath(relative_image_path)
        print(f"Uploading new product image from: {absolute_image_path}")
        image_input = wait.until(EC.presence_of_element_located((By.ID, "id_image")))
        image_input.send_keys(absolute_image_path)
        time.sleep(1.5 * SPEED_MULTIPLIER)

        # --- Submit the form ---
        print("Submitting the updated post...")
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        submit_button.click()
        print("Product post updated successfully.")

        time.sleep(2.5 * SPEED_MULTIPLIER)


    except Exception as e:
        print(f"An error occurred during the product edit process: {e}")

def edit_seller_profile(driver, user_name, new_user_details):
    """
    Navigates to the seller's profile edit page and updates the full name.

    Args:
        driver: The Selenium WebDriver instance.
        new_user_details (dict): A dictionary containing the updated full name.
    """
    print("Starting seller profile edit process...")
    wait = WebDriverWait(driver, 15)
    try:
        # Step 1: Open the dropdown menu
        dropdown_menu = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"img[alt='{user_name}']")))
        dropdown_menu.click()
        time.sleep(1 * SPEED_MULTIPLIER)

        # Step 2: Click the 'Profile' link
        profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Profile']")))
        profile_link.click()
        print("Navigating to profile page...")
        wait.until(EC.url_contains('/profile/'))
        
        # Step 3: Click the 'Edit Profile' link
        print('Waiting for profile page to load...')
        edit_profile_link = wait.until(EC.element_to_be_clickable((By.ID, "EditProfile")))
        edit_profile_link.click()
        print("Navigating to edit profile page...")
        wait.until(EC.url_contains('/edit/'))
        print("Edit profile page loaded.")
        
        # Step 4: Change the name and submit
        name_field = wait.until(EC.presence_of_element_located((By.ID, "id_full_name")))
        name_field.clear()
        human_type(name_field, new_user_details["full_name"])
        time.sleep(0.5 * SPEED_MULTIPLIER)
        
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        submit_button.click()
        print("Profile updated successfully.")

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
        # Using the specific ID for the 'My Posts' section
        my_posts_section = wait.until(EC.visibility_of_element_located((By.ID, "MyPost")))
        
        # Scroll the element into the middle of the view for better visibility
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", my_posts_section)
        print("Successfully scrolled to 'My Posts' section.")
        time.sleep(3 * SPEED_MULTIPLIER) # Pause to view the new product
    except Exception as e:
        print(f"Could not find or scroll to the 'My Posts' section with ID 'MyPosts'. Error: {e}")

def search_for_product(driver, product_to_search):
    """
    Finds the search bar, types the product name, and initiates the search.

    Args:
        driver: The Selenium WebDriver instance.
        product_to_search (str): The name of the product to search for.
    """
    print(f"Searching for product: '{product_to_search}'...")
    wait = WebDriverWait(driver, 10)
    try:
        search_bar = wait.until(EC.presence_of_element_located((By.ID, "searchBar")))
        human_type(search_bar, product_to_search)
        time.sleep(0.5 * SPEED_MULTIPLIER)
        search_bar.send_keys(Keys.RETURN) # Simulate pressing Enter
        print("Search initiated.")
        # Add a pause to allow search results to load and be observed
        time.sleep(2 * SPEED_MULTIPLIER)
    except Exception as e:
        print(f"Could not find or interact with the search bar. Error: {e}")

def demonstrate_seller_flow(driver, user_data, product_data):
    """Orchestrates the entire demonstration for the seller."""
    home_url = "http://127.0.0.1:8000"
    signup_url = f"{home_url}/signup/"
    login_url_fragment = "login"
    create_post_selector = "a[href='#create-post']"

    driver.get(home_url)
    driver.maximize_window()
    time.sleep(1 * SPEED_MULTIPLIER)

    print(f"Navigating to signup page: {signup_url}")
    driver.get(signup_url)
    
    fill_signup_form(driver, user_data["seller"])
    
    wait = WebDriverWait(driver, 15)
    print(f"Waiting for redirect to a URL containing '{login_url_fragment}'...")
    wait.until(EC.url_contains(login_url_fragment))
    print("Redirected to login page successfully.")
    
    perform_login(driver, user_data["seller"])

    print("Waiting for seller homepage to load...")
    create_post_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, create_post_selector)))
    print("Homepage loaded. Starting scenic tour...")
    
    scroll_seller_homepage(driver)
    
    create_post_button.click()
    
    create_product_post(driver, product_data["candle_art"])

    scroll_to_my_products(driver)

    edit_product_post(driver, product_data["candle_art"]["title"], product_data["candle_art_updated"])
    wait.until(EC.url_contains('/seller')) # Wait for redirect after edit
    print("Returned to seller homepage after edit. Scrolling to 'My Posts'...")

    scroll_to_my_products(driver)

    # --- EDIT THE SELLER'S PROFILE ---
    edit_seller_profile(driver, user_data["seller"]["full_name"], user_data["seller_updated"])
    wait.until(EC.url_contains('/profile/')) # Wait for redirect after profile update
    print("Returned to profile page after edit. Pausing to observe.")
    time.sleep(5 * SPEED_MULTIPLIER)

    print("--- Seller Demonstration Finished ---")

def demonstrate_buyer_flow(driver, user_data, product_data):
    """Orchestrates the entire demonstration for the buyer."""
    home_url = "http://127.0.0.1:8000"
    signup_url = f"{home_url}/signup/"
    login_url_fragment = "login"

    driver.get(signup_url)
    driver.maximize_window()
    
    fill_signup_form(driver, user_data["buyer"])

    wait = WebDriverWait(driver, 15)
    print(f"Waiting for redirect to a URL containing '{login_url_fragment}'...")
    wait.until(EC.url_contains(login_url_fragment))
    print("Redirected to login page successfully.")
    
    perform_login(driver, user_data["buyer"])

    print("Waiting for buyer homepage to load...")
    wait.until(EC.presence_of_element_located((By.ID, "searchBar")))
    print("Buyer homepage loaded.")
    
    search_for_product(driver, product_data["candle_art"]["title"])
    
    view_product_details_and_seller_profile(driver, product_data["candle_art"]["title"])
    print("--- Buyer Demonstration Finished ---")


if __name__ == "__main__":
    all_user_data = None
    all_product_data = None
    
    try:
        with open('signup.json', 'r') as f:
            all_user_data = json.load(f)
        with open('products.json', 'r') as f:
            all_product_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Required JSON file not found - {e}. Please ensure both signup.json and products.json exist.")
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from a file. Please check for syntax errors. Details: {e}")

    if all_user_data and all_product_data:
        browser_choice = "chrome"
        while browser_choice.lower() not in ['chrome', 'firefox']:
            browser_choice = input("Which browser would you like to use? (chrome/firefox): ")

        # --- SELLER FLOW ---z
        seller_driver = None
        try:
            print("--- Initializing Seller Session ---")
            seller_driver = setup_driver(browser_choice)
            if seller_driver:
                demonstrate_seller_flow(seller_driver, all_user_data, all_product_data)
        except Exception as e:
            print(f"An unexpected error occurred during the seller demonstration: {e}")
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
        finally:
            if buyer_driver:
                print("Closing buyer browser.")
                buyer_driver.quit()
            
        print("\nFull demonstration complete.")

