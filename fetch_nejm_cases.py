from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
from datetime import datetime
from tqdm import tqdm
import pdb 
import os

# URL of the JAMA Network Clinical Challenges page
BASE_URL = "https://access.yonsei.ac.kr/link.n2s?url=//www.nejm.org/case-challenges" # 

# Function to scrape the clinical cases

def scrape_clinical_cases():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    #chrome_options.add_argument("--headless")
    chrome_options.binary_location = "/usr/bin/google-chrome"
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    cases_year = []
    page_number = 1
    
    while True:
        # Construct the URL for the current page
        url = f"{BASE_URL}?page={page_number}"
        driver.get(url)  # Use Selenium to open the URL
        
        # Optional: Wait for the page to load completely
        driver.implicitly_wait(10)  # Wait for up to 10 seconds

        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Locate each clinical case and extract the link
        case_elements = soup.find_all("li", class_="ng-curated_list-item")  # General class to capture all links of cases
        
        if not case_elements:
            print("No more cases found.")
            break
        
        for case in case_elements:
            link_tag = case.find("a", class_="issue-item_title") 
            link = link_tag['href'] if link_tag else None

            # Extract the publication date
            date_tag = case.find("div", class_="issue-item_date meta-item no-wrap")
            date_text = date_tag.text.strip() if date_tag else None
            
            # Parse the date and check the year
            if date_text:
                publication_date = datetime.strptime(date_text, "%B %d, %Y")
                # pdb.set_trace()
                if publication_date.year < 2013:
                    print("Reached articles older than 2013. Exiting.")
                    return cases_year  # Exit if the year is below 2013
            
            if link:
                cases_year.append((link,publication_date.year))

        print(f"Case URLs of page {page_number} fetched...")
        page_number += 1  # Move to the next page

    driver.quit()  # Close the browser
    return cases_year
    
# Function to extract answer_idx and answer from the clinical case page
def extract_answers(case_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(case_url, headers=headers)

    if response.status_code != 200:
        return None, None  # Return None if there's an error

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Locate the section for the diagnosis
    diagnosis_section = soup.find("div", class_="h4 cb section-type-section")
    
    # Extract the diagnosis title
    diagnosis_title = diagnosis_section.find("p", class_="para").text.strip() if diagnosis_section else None
    
    # Now, find all the answers following the diagnosis section
    answers = []
    for answer in soup.find_all("p", class_="para"):
        answer_text = answer.text.strip()
        if answer_text.startswith("A.") or answer_text.startswith("B.") or answer_text.startswith("C.") or answer_text.startswith("D."):
            answers.append(answer_text)

    # Assuming the first answer is the answer you want
    answer_idx = answers[0][0] if answers else None  # Get the first character (A, B, C, or D)
    answer = answers[0] if answers else None  # Get the full answer text
    answer = answer[3:] # convert 'D. Sternoclavicular sinus' to 'Sternoclavicular sinus'
    # pdb.set_trace()
    return answer_idx, answer

# Main execution
if __name__ == "__main__":
    clinical_cases_links = scrape_clinical_cases()
    
    compiled_results = []
    
    for idx, (link, year) in tqdm(enumerate(clinical_cases_links), total=len(clinical_cases_links)):
        answer_idx, answer = extract_answers(link)
        compiled_results.append({
            'id': idx,
            'link': link,
            'publication_year': year,
            'answer_idx': answer_idx,
            'answer': answer
        })
    
    # Save the results to a JSON file
    file_name = 'nejm_links_updated.json'
    with open(file_name, 'w') as json_file:
        json.dump(compiled_results, json_file, indent=4)

    print(f"Saved {len(compiled_results)} cases to {file_name}")
