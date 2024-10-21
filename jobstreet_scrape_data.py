import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import re

options = Options()
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(options = options)

def login():
    url = "https://my.employer.seek.com"
    email = "email"
    password = "password"

    driver.get(url)

    email_field = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, "email")))
    email_field.send_keys(email)

    email_submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/main/div/div[3]/div/div/div[2]/div/div/div[2]/div/div/form/div/div[2]/div/div[2]/div/div/div/div/button")))
    email_submit_button.click()

    sign_in_link = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/div/div/div[3]/div/div/div/div[3]/div/div/span/a")))
    sign_in_href = sign_in_link.get_attribute("href")

    driver.get(sign_in_href)
    driver.implicitly_wait(10)

    password_field = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID, "password")))
    password_field.send_keys(password)

    sign_in_button = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/div/div/div[3]/div/div/div/div[2]/form/div/div[3]/div/div[2]/button")))
    sign_in_button.click()

def get_job_details():
    # Wait for the 'job open link' element and get the href attribute
    job_open_link = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/footer/div[1]/div/div/div/div[1]/div/div/div[2]/div/div[1]/span/a"))
    )
    job_open_href = job_open_link.get_attribute("href")

    # Navigate to the job open link
    driver.get(job_open_href)

    # Wait for the job box to load and find all job listings
    job_box = WebDriverWait(driver, 80).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/main/div/div/div/div[3]/div/div")))

    if job_box:
        print("Job box found.")
    else:
        print("Job box not found.")

    # Store the original window handle
    original_window = driver.current_window_handle

    # Loop through each job listing
    job_listings = job_box.find_elements(By.XPATH, "/html/body/div[1]/div/div/div/main/div/div/div/div[3]/div/div/div")
    for job in job_listings:
        navigate_job_page(job, original_window)

    print("Successfully processed all jobs.")

def get_expired_job_details():
    expired_job_link = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/footer/div[1]/div/div/div/div[1]/div/div/div[2]/div/div[2]/span/a")))
    expired_job_href = expired_job_link.get_attribute("href")

    driver.get(expired_job_href)

    expired_job_box = WebDriverWait(driver, 80).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/main/div/div/div/div[3]/div/div")))

    if expired_job_box:
        print("expired job box found")
    else:
        print("expired job box not found")

    # Store the original window handle
    original_window = driver.current_window_handle
    
    job_listings = expired_job_box.find_elements(By.XPATH, "/html/body/div[1]/div/div/div/main/div/div/div/div[3]/div/div/div")

    print(f"Total job listings detected: {len(job_listings)}")

    for job in job_listings:
        navigate_job_page(job, original_window)

    print("Successfully processed all jobs.")


def navigate_job_page(job, original_window):
    # Click the menu button to navigate to the job page
    navigate_button = WebDriverWait(job, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-labelledby="menu-label"]'))
    )
    navigate_button.click()

    # Click the job details button
    job_details_button = WebDriverWait(job, 50).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="view-job"]'))
    )
    job_details_button.click()

    # Wait for the new window to open and switch to it
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break

    print("Accessing job details page...")
    time.sleep(2)  # Allow the page to load

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract job details
    title = get_title(soup) or "N/A"
    description = str(get_job_description(soup)) 
    job_location = get_job_location(soup) or "N/A"
    work_type = get_job_work_type(soup) or "N/A"
    requirement = get_job_requirements(soup) or "N/A"
    currency, min_salary, max_salary = get_salary(soup)

    # Create a dictionary with job data
    job_data = {
        "title": title,
        "description": "Description: " + description + " | Location: " + job_location + " | Work type: " + work_type,
        "requirement": requirement,
        "salary": {
            "currency": currency or "N/A",
            "min": min_salary or "N/A",
            "max": max_salary or "N/A"
        }
    }

    # Convert the dictionary to a JSON string with indentation for readability
    job_data_json = json.dumps(job_data, indent=4)

    # Print the JSON string
    print(job_data_json)

    # Close the new window and switch back to the original one
    driver.close()
    driver.switch_to.window(original_window)

def get_title(soup):
    try:
        title = soup.find("h1", {"data-automation": "job-detail-title"}).text.strip()
    except AttributeError:
        title= "N/A"
    return title

def get_job_location(soup):
    try:
        job_location = soup.find("span", {"data-automation":"job-detail-location"}).text.strip()
    except AttributeError:
        job_location = "N/A"
    return job_location

def get_job_description(soup):
    try:
        job_description=soup.find("span", {"data-automation": "job-detail-classifications"}).text.strip()
    except AttributeError:
        job_description = "N/A"
    return job_description

def get_job_work_type(soup):
    try:
        job_work_type = soup.find("span", {"data-automation": "job-detail-work-type"}).text.strip()
    except AttributeError:
        job_work_type="N/A"
    return job_work_type

def get_job_requirements(soup):
    try:
        job_requirements_details = soup.find('div', {'data-automation': 'jobAdDetails'})
        requirements_section = job_requirements_details.find_all('ul')[1]
        job_requirements = [li.get_text(strip=True) for li in requirements_section.find_all('li')]
        job_requirements_string = " ".join(job_requirements)

    except (AttributeError, IndexError):
        job_requirements_string = "N/A"
    return job_requirements_string

def get_salary(soup):
    salary_element = soup.find('span', {'data-automation': 'job-detail-salary'})

    if salary_element:
        salary_text = salary_element.get_text(strip=True)  # Clean the text
        print(f"Raw Salary Text: {salary_text}")  # Debugging line

        # Initialize default currency as first word if salary starts with an alphabet
        if re.match(r'^[A-Za-z]', salary_text):
            first_word = salary_text.split()[0]

            # Handle RM-specific logic by hardcoding to MYR
            if first_word == "RM":
                currency = "MYR"
            else:
                # Check for currency abbreviation in parentheses (e.g., (SGD))
                currency_match = re.search(r'\((\w{2,3})\)', salary_text)
                if currency_match:
                    currency = currency_match.group(1)  # Use currency inside brackets
                else:
                    currency = first_word  # Fallback to first word (e.g., Rp)

            # Split salary text by dash/hyphen
            parts = re.split(r' – | - ', salary_text)

            # Extract minimum salary
            first_part = parts[0].strip()
            min_salary_str = re.sub(r'\D', '', first_part)  # Remove non-digit characters
            min_salary = int(min_salary_str) if min_salary_str else 0

            # Extract maximum salary, if available
            if len(parts) > 1:
                second_part = parts[1].strip()
                max_salary_str = re.sub(r'\D', '', second_part)  # Remove non-digit characters
                max_salary = int(max_salary_str) if max_salary_str else 0
            else:
                max_salary = 0

        else:
            # Handle other cases where salary doesn't start with an alphabet (fallback logic)
            currency_match = re.search(r'\((\w{2,3})\)', salary_text)
            currency = currency_match.group(1) if currency_match else "N/A"

            # Split salary text by dash/hyphen
            parts = re.split(r' – | - ', salary_text)

            # Extract minimum salary
            first_part = parts[0].strip()
            min_salary_str = re.sub(r'\D', '', first_part)  # Remove non-digit characters
            min_salary = int(min_salary_str) if min_salary_str else 0

            # Extract maximum salary, if available
            if len(parts) > 1:
                second_part = parts[1].strip()
                max_salary_str = re.sub(r'\D', '', second_part)  # Remove non-digit characters
                max_salary = int(max_salary_str) if max_salary_str else 0
            else:
                max_salary = 0

        return currency, min_salary, max_salary

    else:
        return "N/A", 0, 0

# Function calls
login()
get_expired_job_details()
get_job_details()
time.sleep(1000)