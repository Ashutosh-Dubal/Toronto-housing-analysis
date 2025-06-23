import csv
import time
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --- Paths ---
OUTPUT_CSV_PATH = Path("../Housing_Price_Analysis/data/raw/toronto_housing_data.csv")
OUTPUT_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

# --- Configure headless Chrome ---
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("window-size=1920x1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=chrome_options)

# --- Extract data from a single listing ---
def extract_listings_data(listing):
    try:
        address_elem = listing.select_one("a.address")
        address = address_elem.text.strip() if address_elem else None

        price_elem = listing.select_one("li.price span[itemprop='price']")
        price = price_elem.text.strip().replace("$", "").replace(",", "") if price_elem else None

        details = listing.select('ul.card-listing--values li')
        beds = details[1].text.strip() if len(details) > 1 else None
        baths = details[2].text.strip() if len(details) > 2 else None
        sqft = details[3].text.strip() if len(details) > 3 else None

        return {
            "address": address,
            "price": price,
            "beds": beds,
            "baths": baths,
            "sqft": sqft
        }
    except Exception as e:
        logging.warning(f"Error extracting listing: {e}")
        return None

# --- Main Scraper ---
def scrape_zolo(max_pages=395):
    logging.info("Starting Zolo scraper...")
    driver = get_driver()
    base_url = 'https://www.zolo.ca/toronto-real-estate'
    driver.get(base_url)

    all_data = []
    page = 1

    while page < max_pages:
        time.sleep(3)
        logging.info(f"Scraping page {page}...")

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings = soup.select("article.card-listing")

        if not listings:
            logging.warning("No listings found. Stopping.")
            break

        for listing in listings:
            data = extract_listings_data(listing)
            if data:
                all_data.append(data)

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="next page of results"]')
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            next_button.click()
            page += 1
        except NoSuchElementException:
            logging.info("No more pages found. Scraping complete.")
            break

    driver.quit()

    # --- Save data to CSV ---
    if all_data:
        with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
            writer.writeheader()
            writer.writerows(all_data)
        logging.info(f"✅ Saved {len(all_data)} listings to: {OUTPUT_CSV_PATH}")
    else:
        logging.warning("⚠ No data scraped. CSV not created.")

if __name__ == "__main__":
    scrape_zolo()

