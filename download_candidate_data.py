from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
)
import time
import random
import os

# Specify the download path
download_path = r"C:\Users\Acer\Downloads\resumes"  # Use raw string to avoid escape characters

# Ensure the directory exists
if not os.path.exists(download_path):
    os.makedirs(download_path)

# Configure Chrome options with download preferences
options = Options()
options.add_argument("--disable-notifications")

# Set Chrome preferences
prefs = {
    "download.default_directory": download_path,  # Set download path
    "download.prompt_for_download": False,  # Disable download prompts
    "directory_upgrade": True,  # Ensure the specified path is used
    "safebrowsing.enabled": True  # Enable safe browsing for automated downloads
}
options.add_experimental_option("prefs", prefs)

# Initialize the WebDriver with the configured options
driver = webdriver.Chrome(options=options)

def random_sleep(min_time=1, max_time=3):
    """Sleep for a random interval between min_time and max_time seconds."""
    time.sleep(random.uniform(min_time, max_time))

def login():
    """Log into the website using provided credentials."""
    url = "https://my.employer.seek.com"
    email = "email"
    password = "password"

    driver.get(url)

    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_field.send_keys(email)

    random_sleep(1, 2)  # Random delay before clicking

    email_submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/main/div/div[3]/div/div/div[2]/div/div/div[2]/div/div/form/div/div[2]/div/div[2]/div/div/div/div/button")
        )
    )
    email_submit_button.click()

    random_sleep(2, 4)  # Random sleep before next step

    sign_in_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/div/div/div[3]/div/div/div/div[3]/div/div/span/a")
        )
    )
    sign_in_href = sign_in_link.get_attribute("href")
    driver.get(sign_in_href)
    driver.implicitly_wait(10)

    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_field.send_keys(password)

    random_sleep(1, 2)

    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/div/div/div[3]/div/div/div/div[2]/form/div/div[3]/div/div[2]/button")
        )
    )
    sign_in_button.click()

    random_sleep(3, 5)  # Allow page to load

MAX_RETRIES = 3  # Number of retries for stale elements

def safe_click(xpath):
    """Safely click an element, even with DOM re-renders."""
    for attempt in range(MAX_RETRIES):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            random_sleep(1, 3)  # Random delay after click
            return
        except (StaleElementReferenceException, ElementClickInterceptedException) as e:
            print(f"Attempt {attempt + 1}/{MAX_RETRIES}: {type(e).__name__}. Retrying...")
            random_sleep(2, 4)  # Random delay before retrying

    print("Failed to click the element. Attempting JavaScript click...")
    element = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].click();", element)

def navigate_candidates_page():    
    candidate_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div/div[1]/div")
        )
    )

    if not candidate_box:
        print("Candidate box not found.")
        return

    print("Candidate box found. Searching for candidates...")

    candidates = []
    index = 2

    while True:
        try:
            xpath = f"/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div/div[1]/div/div[{index}]"
            candidate = driver.find_element(By.XPATH, xpath)
            candidates.append(candidate)
            index += 1
            random_sleep(0.5, 1.5)  # Random delay between interactions
        except Exception as e:
            print(f"Search complete. Total candidates found: {len(candidates)}")
            break

    for idx, candidate in enumerate(candidates, start=2):
        download_resume(idx)
        random_sleep(1, 3)  # Sleep between downloads

    # Clear the candidates list after processing
    candidates.clear()
    print("All candidates processed. The list has been cleared.")
    random_sleep(2, 4)  # Allow downloads to complete

def scroll_to_element(element):
    """Scroll to a specific element."""
    driver.execute_script("arguments[0].scrollIntoView();", element)
    random_sleep(1, 2)  # Wait a moment after scrolling

def download_resume(index):
    """Download the resume of a candidate."""
    action_button_xpath = f'/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div/div[1]/div/div[{index}]/div/div/div[2]/div/div/div/div/div[1]/div/div/button'

    # Function to safely click an element with retries for stale references
    def safe_click_with_retries(xpath):
        for attempt in range(3):  # Retry 3 times
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                scroll_to_element(element)  # Scroll to the element
                element.click()
                return True
            except StaleElementReferenceException:
                print(f"Attempt {attempt + 1}: StaleElementReferenceException. Retrying...")
                random_sleep(1, 2)  # Wait before retrying
            except Exception as e:
                print(f"Failed to click the element: {e}. Retrying...")
                random_sleep(1, 2)  # Wait before retrying
        print("Max retries reached. Element click failed.")
        return False

    # Try to click the action button to reveal the download button
    if not safe_click_with_retries(action_button_xpath):
        print(f"Could not click action button for candidate {index-1}. Skipping...")
        return  # Skip to the next candidate if unable to click the action button

    random_sleep(0.5, 1.5)  # Small delay after clicking action button

    # Define the parent XPath
    parent_xpath = f'/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div/div[1]/div/div[{index}]/div/div/div[2]/div/div/div/div[1]/div[2]/div[1]'

    # Check the number of children in the parent div
    child_count = driver.execute_script(
    """
       return document.evaluate("count(./*[contains(@role, 'menuitem')])", document.evaluate(arguments[0], document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue, null, XPathResult.NUMBER_TYPE, null).numberValue;
    """, parent_xpath
     )
    # Print the number of children found
    print(f"Candidate {index-1}: Found {child_count} child button(s) in the parent div.")

    # Determine the appropriate download button XPath based on the number of child elements
    if child_count == 3:
        download_button_xpath = f'{parent_xpath}/button[2]'  # XPath for when there are 3 children
        print(f"Candidate {index-1}: Using XPath for button[2]: {download_button_xpath}")
    elif child_count == 2:
        download_button_xpath = f'{parent_xpath}/button[1]'  # XPath for when there are not 3 children
        print(f"Candidate {index-1}: Using XPath for button[1]: {download_button_xpath}")
    else:
        print(f"Skipped for candidate {index-1}")
        return

    # Attempt to click the download button
    if not safe_click_with_retries(download_button_xpath):
        print(f"Could not click download button for candidate {index-1}. Trying JavaScript fallback...")

        # JavaScript fallback to find the button if the Selenium click fails
        download_button = driver.execute_script(
            """
            let buttons = document.querySelectorAll('button[role="menuitem"]');
            for (let button of buttons) {
                if (button.innerText.includes('Download resumé')) {
                    button.click(); // Click the button
                    return button;
                }
            }
            return null;
            """
        )

        if download_button is None:
            print(f"Download button for candidate {index-1} not found using JavaScript. Skipping...")
            return  # Skip to the next candidate if the button is not found
        else:
            print(f"Attempted to download resume for candidate {index-1} using JavaScript.")
            random_sleep(5, 8)  # Wait for the download to complete

    print(f"Downloaded resume for candidate {index-1}.")
    random_sleep(5, 8)  # Wait for the download to complete

def navigate_next_page():
    next_button = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Next"]')))

    if(next_button):
        print("Next button found")
        next_button.click()
        return True
    else:
        print("Next button not found")
        return False

def main():
    login()
    #navigate to the candidates page
    candidates_open_link = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/footer/div[1]/div/div/div/div[1]/div/div/div[2]/div/div[4]/span/a")))
    candidates_href = candidates_open_link.get_attribute("href")
    driver.get(candidates_href)

    #Scrape the first page
    navigate_candidates_page()

    #while the next page exists, we loop the navigate_candidates page
    while(navigate_next_page()):
        navigate_candidates_page()

main()

