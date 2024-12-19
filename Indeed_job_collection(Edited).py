from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import csv
import time
from datetime import datetime
import sys # For logs
import os

date_time = datetime.now().strftime("%Y.%m.%d_%H_%M")

# Backup the original stdout - console/log file
original_stdout = sys.stdout

# =========================================================================== 
# =========================================================================== 
# =========================================================================== 
# ===== THE SECTION FOR YOU - SWITCH URLs ACCORDING TO YOUR NEED =====

# LAST 24hrs records
#URL = "https://www.indeed.com/jobs?q=&l=Washington+State&fromage=1"
#CSV = "1Day"

# LAST 3-days records
#URL = "https://www.indeed.com/jobs?q=&l=Washington+State&fromage=3"
#CSV = "3Days"

# LAST 7-days records
# URL = "https://www.indeed.com/jobs?q=&l=Washington+State&fromage=7"
# CSV = "7Days"

# # LAST 14-days records
# URL = "https://www.indeed.com/jobs?q=&l=Washington+State&fromage=14"
# CSV = "14Days"

# LAST 7-days records
URL = "https://www.indeed.com/jobs?q=&l=Washington+State&fromage=7"
CSV = "7Days"


# ALL-records records
#URL = "https://www.indeed.com/jobs?q=&l=Washington+State"
#CSV = "All_Time"


# WARNING!! DO NOT MODIFY/CHANGE/EDIT ANYTHING BELOW THIS LINE - IF GOT ERROR BECAUSE OF THIS SCRIPT, PLEASE CONTACT ME ()
# ================================================================================================================================
# ================================================================================================================================
# ================================================================================================================================

# Redirect stdout to a file
log_file = open(f"Script_1-{CSV}-Logs-{date_time}.txt", "w", encoding="utf-8")
sys.stdout = log_file

# CSV File Names
First_CSV_file = f"01-{CSV}-All_Data-{date_time}.csv" # CSV Generated from Process 1 

# # Function to initialize the web driver
# def initialize_driver():
#     chrome_options = uc.ChromeOptions()
#     #chrome_options.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")  
#     chrome_options.add_argument("--log-level=3")
#     driver = uc.Chrome(options=chrome_options)
#     return driver


def initialize_driver():
    # Initialize Chrome options
    chrome_options = uc.ChromeOptions()
    # Suppress logs for a cleaner output
    chrome_options.add_argument("--log-level=3")
    # Optionally, add a custom User-Agent (if needed, uncomment and customize)
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    
    # Automatically manage the ChromeDriver version
    driver_path = ChromeDriverManager().install()
    driver = uc.Chrome(driver_executable_path=driver_path, options=chrome_options)
    
    return driver

# Function to open the location dropdown on the Indeed job search page
def open_location_dropdown(driver):
    time.sleep(7)
    try:
        location_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button#filter-loc"))
        )
        location_dropdown.click()
    except Exception as e:
        pass
    
# Function to get links to specific job location pages
def get_location_links(driver): 
    time.sleep(7)
    try:
        location_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul#filter-loc-menu a"))
        )
        return [link.get_attribute("href") for link in location_links]
    except Exception as e:    
        return []

# Function to extract data from a job listing div element  
def extract_data_from_div(div):
    time.sleep(7)
    try:
        company_name = div.find_element(By.CSS_SELECTOR, "div.css-1afmp4o.e37uo190 span.css-1h7lukg.eu4oa1w0").text
    except:
        company_name = ""
    
    try:
        position = div.find_element(By.CSS_SELECTOR, ".jobTitle.css-14z7akl.eu4oa1w0").text # Extract the position
    except:
        try:
            position = div.find_element(By.CSS_SELECTOR, "h2.jobTitle.css-1psdjh5.eu4oa1w0").text
        except:
            position = ""

    location = div.find_element(By.CSS_SELECTOR, "div.css-1restlb.eu4oa1w0").text # Extract the location

    # Handle strings that might be misinterpreted by Excel
    for string in [company_name, position, location]:
        if string and string[0] in ['=', '+', '-', '@']:
            string = "'" + string
    
    # Extract the date posted, handling different possible formats        
    try:
        date_posted = div.find_element(By.CSS_SELECTOR, ".css-qvloho.eu4oa1w0").text 
    except:
        try:
            date_posted = div.find_element(By.CSS_SELECTOR, "span.myJobsState").text
        except:
            try:
                date_posted = div.find_element(By.CSS_SELECTOR, "span.date").text
            except:
                date_posted = ""
            
    date_posted = date_posted.replace("Posted", "").strip() # Remove the "Posted" text
    job_url = div.find_element(By.CSS_SELECTOR, "h2.jobTitle a").get_attribute("href") # Extract the job URL
    
    return [company_name, position, location, date_posted, job_url, CSV]

# Extract the date posted, handling different possible formats
def pause_and_wait():
    custom_print("CAPTCHA Challenge Detected! - NOT Resolved Automatically")
    input("Please Solve The CAPTCHA Challenge Manually And Press Enter To Continue Crawling...")
    time.sleep(10)
    
# Function to crawl and extract data from job listings on a specific location page
def crawl_data(driver, csv_writer):
    time.sleep(8)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
        )
    except Exception as e:
        return
    
    # Keep track of the unique data to avoid duplicates
    unique_data = set()

    divs = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
    
    initial_unique_data_count = len(unique_data)
    
    for div in divs:
        # Skip the div if it contains a dollar sign or "Job Expired" FROM THE JOB LISTING - PROCESS 1
        if "$" not in div.text and "job has expired" not in div.text:
            data = extract_data_from_div(div)
            if data:
                # Convert the list to a tuple before adding to the set
                data_tuple = tuple(data)
                if data_tuple not in unique_data:
                    csv_writer.writerow(data)
                    unique_data.add(data_tuple)

                    # Check if a CAPTCHA challenge is detected
                    if "fare" in driver.current_url.lower():
                        pause_and_wait()  # Pause and wait for user input
                        
    added_data_count = len(unique_data) - initial_unique_data_count
    return added_data_count

# Custom print function to print to the console and to the log file at the same time
def custom_print(*args, **kwargs):
    # Print to the original stdout (console)
    print(*args, **kwargs, file=original_stdout)
    
    # Append to the file - dynamic date_time
    with open(f"Script_1-{CSV}-Logs-{date_time}.txt", "a", encoding="utf-8") as log_file:
        print(*args, **kwargs, file=log_file)

def main():
    # try-except-finally block to handle exceptions - error handling
    try:
        driver = initialize_driver()
        driver.get(URL)
            
        time.sleep(10)
        
        custom_print("\n")
        custom_print("<<<<< ----- Script: 1 - Indeed Job Scraper by AHMAD S. (Ahmasoft) for DOMAINSTERS LLC ----- >>>>>")
        process_one_start_time = datetime.now().strftime("%Y.%m.%d_%H_%M")
        custom_print("\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        custom_print(f"Initiating The Process-1 at: {process_one_start_time} | For: {CSV} | URL: {URL}")
        custom_print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
        custom_print("****** ***** PROCESS-1 STARTED (FILTERING DATA FROM JOB WINDOWS) ***** ******")
        
        # Opening the location dropdown and getting the links to specific job location pages
        open_location_dropdown(driver)
        location_links = get_location_links(driver)
        
        # Create a CSV file and write the header row - PROCESS 1        
        with open(First_CSV_file, "w", newline="", encoding="utf-8") as file:
            csv_writer = csv.writer(file)
            
            # Header Row
            csv_writer.writerow(["Company Name", "Position", "Location", "Date Posted", "Job URL", "Time Span"])
            
            location_count = 1  
            
            # Loop through each location page   
            for location_link in location_links:
                
                # Apply a maximum of 3 retries if the page fails to load
                retries = 3
                for attempt in range(retries):
                    try:
                        driver.set_page_load_timeout(120)
                        driver.get(location_link)
                        
                        # If the page loads successfully, break out of the retry loop
                        break
                    except Exception as e:
                        # Log the exception for debugging purposes
                        custom_print(f"Error loading {location_link}: {e}")

                        # If it's the last retry, log the error and continue with the next URL
                        if attempt == retries - 1:
                            custom_print(f"Failed to load {location_link} after {retries} attempts. Moving on to the next URL.")
                            continue
                        custom_print(f"Attempt {attempt + 1} failed for {location_link}. Retrying...")
                        time.sleep(60)  # Wait for 2 seconds before retrying
                        custom_print(f"Retrying in 60 seconds...")

                page = 1
                while True: 
                    try:
                        added_data_count = crawl_data(driver, csv_writer)
                        
                        custom_print(f"Location: {location_count}/{len(location_links)} | Crawled Page: {page} | Found: {added_data_count} Filtered Jobs From Job Windows")
                        page += 1
                        
                        # Save the crawled data to CSV after processing each page
                        file.flush()  
                        
                        # Apply a maximum of 4 retries if the next page button is not found
                        retries = 4
                        next_page_found = False
                        for _ in range(retries):
                            try:
                                next_button = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-testid='pagination-page-next']"))
                                )
                                if next_button:
                                    next_button.click()
                                    time.sleep(5) 
                                    next_page_found = True
                                    break
                                time.sleep(6)
                            except:
                                if _ == retries - 1:  # If it's the last retry
                                    break
                        time.sleep(7)

                        if not next_page_found:
                            custom_print("<<<<<<<<<<<<<<<<<<<<<<< No Next Page For This Location >>>>>>>>>>>>>>>>>>>>>>\n")
                            break
                        
                    except Exception as e:
                        continue
                    
                location_count += 1
        
        process_one_completion_time = datetime.now().strftime("%Y.%m.%d_%H_%M")
        custom_print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        custom_print(f"Process-1 Completed at: {process_one_completion_time} | For: {CSV} | URL: {URL}")
        custom_print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n")  
             
        # Close the web driver
        driver.quit()
        
        custom_print("********** ******* ***** COMPLETED ******* ***** *******\n\n")
        
        custom_print("<<<<<<<<<<<<<<<<<<<<<<<< TimeStamps >>>>>>>>>>>>>>>>>>>>>>>>>>>")
        custom_print(f"Process 1 Started at: {process_one_start_time}")
        custom_print(f"Process 1 Completed at: {process_one_completion_time}")
        custom_print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    
    # If an error occurs, log the error
    except Exception as e:
        custom_print(f"*** ERROR OCCURRED *** | {e}")
       
    # Close the log file and restore the original stdout    
    finally:
        # This will always be executed, even if an exception occurs
        log_file.close()  # Close the log file
        sys.stdout = original_stdout  # Restore the original stdout
                             
if __name__ == "__main__":
    main()
