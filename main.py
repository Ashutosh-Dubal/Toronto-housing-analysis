import csv

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

def clean_detail(text):
    """Cleans and converts price string to integer."""
    text = text.strip().lower()
    if text == '–' or text == '':
        return None
    return text.lower().replace('bed', '').replace('bath', '').replace('sqft', '')

# Configure headless browser
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

base_url = 'https://www.zolo.ca/toronto-real-estate'
driver.get(base_url)

all_data = []

def extract_listings_data(listings):
    try:
        address_elem = listings.select_one("a.address")
        address = address_elem.text.strip() if address_elem else None
        if not address:
            return None  # Skip listings with no address

        # Price
        price_elem = listings.select_one("li.price span[itemprop='price']")
        price = price_elem.text.strip().replace("$", "").replace(",", "") if price_elem else None

        # Details
        details = listings.select('ul.card-listing--values li')
        beds = clean_detail(details[1].text) if len(details) > 1 else None
        baths = clean_detail(details[2].text) if len(details) > 2 else None
        sqft = clean_detail(details[3].text) if len(details) > 3 else None

        return {
            "address": address,
            "price": price,
            "beds": beds,
            "baths": baths,
            "sqft": sqft
        }

    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

page = 1

while page < 395:
    time.sleep(3)
    print(f"Scraping page {page}...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all listings
    toronto_listings = soup.select("article.card-listing")

    if not toronto_listings:
        print("No listings found. Stopping")
        break

    for listing in toronto_listings:
        data = extract_listings_data(listing)
        if data:
            all_data.append(data)

    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="next page of results"]')
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        next_button.click()
        page += 1
    except NoSuchElementException:
        print("No more pages.")
        break

driver.quit()


# Save to CSV
with open("toronto_housing_data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
    writer.writeheader()
    writer.writerows(all_data)

print(f"Saved {len(all_data)} listings.")

