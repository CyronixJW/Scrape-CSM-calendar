from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from ics import Calendar, Event
from datetime import datetime
import pytz
# Set up Chrome options for incognito mode
chrome_options = Options()
chrome_options.add_argument("--incognito")

# Set up WebDriver
driver = webdriver.Chrome(options=chrome_options)

try:
    inputUsername = input("Enter your username: ")
    inputPassword = input("Enter your password: ")
    inputTrimester = input("Enter the trimester: (Example: 2024/25 Trimester 2) ")
    # Navigate to the login page
    driver.get("https://fs.singaporetech.edu.sg/adfs/ls/?wtrealm=https%3A%2F%2Fcsm-students.singaporetech.edu.sg%2F&wa=wsignin1.0&wreply=https%3A%2F%2Fcsm-students.singaporetech.edu.sg%2Fsignin-wsfed&wctx=CfDJ8MsmBI02LqFDj4SUwbADhv2dOmOoyPErS_kPeGdPVkKo9DQhmsWaT7ymm1Kso7t2CpKSqVoTeJfMnb7uehaSgtDxQsJgKUPYC0WWw51JeHcrv_iVJhy0jM3luquhREvbz1_P5IXDrOvfgVVPp0xRyMPOEQZpURdlJYcZDRS93wL88E_3NqeVdtt6PBpHVy2SIKHBtKeW9hJuSqQFkactRus")

    # Wait for the page to load
    time.sleep(5)

    # Log in
    username = driver.find_element(By.ID, "userNameInput")  # Replace with the actual field ID
    password = driver.find_element(By.ID, "passwordInput")  # Replace with the actual field ID
    username.send_keys(inputUsername)  # Replace with your username
    password.send_keys(inputPassword)  # Replace with your password

    submit_button = driver.find_element(By.ID, "submitButton")  # Replace with the actual field ID
    submit_button.click()

    # Wait for login to complete
    time.sleep(5)

    # Navigate to the timetable page
    driver.get("https://csm-students.singaporetech.edu.sg/Timetable")

    # Wait for the timetable to load
    time.sleep(5)

    # Wait for the dropdown to load
    wait = WebDriverWait(driver, 10)

    # Locate the dropdown button and click to expand it
    dropdown_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "k-dropdownlist")))
    dropdown_button.click()

    # Wait for the dropdown options to be visible
    dropdown_list = driver.find_element(By.ID, "ddlTerm_listbox")

    # Locate the specific option (2024/25 Trimester 2) and click it
  # Locate the specific option (2024/25 Trimester 2) and wait until it is clickable
    desired_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[.//span[text()='{inputTrimester}']]")))
    desired_option.click()

    # Wait to ensure the selection is applied
    time.sleep(2)

    # Verify the selected value
    selected_value = driver.find_element(By.CLASS_NAME, "k-input-value-text").text
    print("Selected value:", selected_value)

  

    # Wait for the timetable to reload based on selection
    time.sleep(5)

    # Extract page source
    page_source = driver.page_source

finally:
    # Close the browser
    driver.quit()

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Locate the timetable table within the k-grid-header element
table_container = soup.find('div', {'class': 'k-grid-content'})
table = table_container.find('table') if table_container else None

# Create a new calendar
calendar = Calendar()

if table:
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        
        if len(cells) >= 9:
            event = Event()
            event.name = cells[0].get_text(strip=True) +" " + "(" + cells[2].get_text(strip = True) + ")"  # Type
            
            # Parse the date and time
            date_str = cells[4].get_text(strip=True)
            time_from_str = cells[5].get_text(strip=True)
            time_to_str = cells[6].get_text(strip=True)
            
            start_datetime = datetime.strptime(f"{date_str} {time_from_str}", "%d-%b-%Y %H:%M")
            end_datetime = datetime.strptime(f"{date_str} {time_to_str}", "%d-%b-%Y %H:%M")
            
            # Set timezone to GMT+8
            gmt_plus_8 = pytz.timezone('Asia/Singapore')
            start_datetime = gmt_plus_8.localize(start_datetime)
            end_datetime = gmt_plus_8.localize(end_datetime)
            
            event.begin = start_datetime
            event.end = end_datetime
            event.location = cells[7].get_text(strip=True)  # Location
            event.description = (
                f"CU Code: {cells[0].get_text(strip=True)}, "
                f"Type: {cells[2].get_text(strip=True)}, "
                f"Mode: {cells[1].get_text(strip=True)}, "
                f"Instructor: {cells[8].get_text(strip=True)}"
            )
            calendar.events.add(event)
else:
    print("Timetable table not found in the page source.")

# Export the calendar to an ICS file
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ics_filename = f'timetable_{current_datetime}.ics'
with open(ics_filename, 'w') as f:
    f.writelines(calendar)


print(f"ICS file created: {ics_filename} at {current_datetime}")