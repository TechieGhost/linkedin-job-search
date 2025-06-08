from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import urllib.parse
import csv
import os
import random


# Path to GeckoDriver
geckodriver_path = r"C:\\tools\\geckodriver-v0.36.0-win64\\geckodriver.exe"

# Path to your Firefox profile (from about:profiles)
firefox_profile_path = r"C:\\Users\\nayan\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\ih6lydi4.default-release"

# Setup Firefox options
options = Options()
options.profile = firefox_profile_path

# Setup and start the driver
service = Service(geckodriver_path)
driver = webdriver.Firefox(service=service, options=options)


def search_linkedin_jobs(job_keyword, index=0):
    """
    Search for jobs on LinkedIn based on the provided keyword and index.
    
    Args:
        job_keyword (str): The keyword to search for jobs.
        index (int): The starting index for pagination.
        
    Returns:
        tuple: Lists of job titles, company names, job locations, and job URLs.
    """

    # Parameter details
    # Last 24 hours jobs: f_TPR=r86400
    # Geo ID for Seattle, US: 104116203
    url = f"https://www.linkedin.com/jobs/search/?f_TPR=r86400&geoId=104116203&keywords={urllib.parse.quote(job_keyword)}&origin=JOB_SEARCH_PAGE_JOB_FILTER&start={index}"
    
    driver.get(url)
    time.sleep(4)  # Wait for the page to load

    job_urls = driver.execute_script("""
        var jobUrlAnchors = document.querySelectorAll('.job-card-list__title--link'); 
        return Array.from(jobUrlAnchors).map(link => link.href);
    """)

    job_titles = driver.execute_script("""
        var jobTitleDivs = document.querySelectorAll('.full-width.artdeco-entity-lockup__title.ember-view');
        return Array.from(jobTitleDivs).map(div => {
            const strong = div.querySelector('a strong');
            return strong ? strong.textContent.trim() : '';
        });
    """)

    company_names = driver.execute_script("""
        var companyNameDivs = document.querySelectorAll('.artdeco-entity-lockup__subtitle.ember-view');
        return Array.from(companyNameDivs).map(div => {
            var span = div.querySelector('span');
            return span ? span.textContent.trim() : '';
        });
    """)

    job_locations = driver.execute_script("""
        var jobLocationDivs = document.querySelectorAll('.artdeco-entity-lockup__caption.ember-view');
        return Array.from(jobLocationDivs).map(div => {
            const span = div.querySelector('ul li span');
            return span ? span.textContent.trim() : '';
        });
    """)

    return job_titles, company_names, job_locations, job_urls

# save the results to a CSV file
def save_to_csv(job_titles, company_names, job_locations, job_urls):
    file_exists = os.path.isfile('linkedin_jobs.csv')
    write_header = not file_exists or os.path.getsize('linkedin_jobs.csv') == 0

    with open('linkedin_jobs.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(['job_title', 'company_name', 'location', 'job_url'])
        
        for title, company, location, url in zip(job_titles, company_names, job_locations, job_urls):
            writer.writerow([title, company, location, url])

    print("Data appended to linkedin_jobs.csv")



def main():

    index = 0
    max_index = 100 # max can be 100
    keyword = "incident response"
    

    while index < max_index:  # Adjust the range as needed
        print(f"Searching for jobs index {index}...")

        job_titles, company_names, job_locations, job_urls = search_linkedin_jobs(keyword, index)

        print(f"Received {len(job_titles)} job titles, {len(company_names)} company names, {len(job_locations)} job locations, and {len(job_urls)} job URLs.")

        index += len(job_titles)

        
        # TODO: Move this outside the loop to avoid saving after every iteration
        print("saving the results to CSV...")
        save_to_csv(job_titles, company_names, job_locations, job_urls)

        # Wait for a random amount of time between 2 and 7 seconds
        wait_time = random.uniform(2, 5)
        print(f"Waiting for {wait_time:.2f} seconds before next iteration...")
        time.sleep(wait_time)


if __name__ == "__main__":
    main()
    driver.quit()  # Close the browser when done