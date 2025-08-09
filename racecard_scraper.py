#!/usr/bin/env python3
"""
SMS Pariaz Racecard Scraper using Selenium (Headless Browser)
Extracts racecard information from https://www.smspariaz.com/local/
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import json
import re
import os
from typing import Dict, List, Optional
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RacecardScraper:
    def __init__(self, base_url: str = "https://www.smspariaz.com/local/", headless: bool = True):
        self.base_url = base_url
        self.headless = headless
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver with options to mimic real user"""
        try:
            chrome_options = Options()
            
            # Basic options
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # User agent to mimic real browser
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Additional options to avoid detection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set up the driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set up explicit wait
            self.wait = WebDriverWait(self.driver, 15)
            
            logger.info("✓ Chrome WebDriver setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome WebDriver: {e}")
            return False

    def mimic_human_behavior(self):
        """Add random delays and scrolling to mimic human behavior"""
        try:
            # Random scroll to simulate reading
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            for _ in range(3):
                # Scroll to random position
                scroll_to = random.randint(0, scroll_height // 2)
                self.driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                time.sleep(random.uniform(0.5, 1.5))
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            logger.warning(f"Error during human behavior simulation: {e}")

    def get_page_content(self) -> Optional[BeautifulSoup]:
        """Fetch and parse webpage content using Selenium"""
        try:
            logger.info(f"Loading page: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for page to load
            time.sleep(random.uniform(2, 4))
            
            # Wait for any dynamic content to load
            try:
                # Wait for common elements that indicate page is loaded
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                logger.info("✓ Page loaded successfully")
            except TimeoutException:
                logger.warning("Page load timeout, but continuing...")
            
            # Mimic human behavior
            self.mimic_human_behavior()
            
            # Get page source and create BeautifulSoup object
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            logger.info(f"✓ Page content extracted ({len(page_source)} characters)")
            return soup
            
        except Exception as e:
            logger.error(f"Error getting page content: {e}")
            return None

    def extract_race_date(self, soup: BeautifulSoup) -> str:
        """Extract the race date from the page"""
        try:
            # Look for date information in various possible locations
            date_selectors = [
                '.race-date',
                '.date',
                '.event-date',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '.header',
                '.title'
            ]

            # Common date patterns
            date_patterns = [
                r'\d{1,2}/\d{1,2}/\d{4}',
                r'\d{1,2}-\d{1,2}-\d{4}',
                r'\d{4}-\d{1,2}-\d{1,2}',
                r'\d{1,2}\s+\w+\s+\d{4}',
                r'\w+\s+\d{1,2},\s+\d{4}'
            ]

            # Check page title first
            title = soup.find('title')
            if title:
                title_text = title.get_text(strip=True)
                for pattern in date_patterns:
                    match = re.search(pattern, title_text, re.IGNORECASE)
                    if match:
                        logger.info(f"Found date in title: {match.group()}")
                        return self._normalize_date(match.group())

            # Check other elements
            for selector in date_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    for pattern in date_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            logger.info(f"Found date in {selector}: {match.group()}")
                            return self._normalize_date(match.group())

            # If no date found, return today's date as fallback
            today = datetime.now().strftime('%Y-%m-%d')
            logger.warning(f"No date found, using today's date: {today}")
            return today

        except Exception as e:
            logger.error(f"Error extracting race date: {e}")
            return datetime.now().strftime('%Y-%m-%d')

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format"""
        try:
            # Handle DD/MM/YYYY format (common in many countries)
            if re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
                parts = date_str.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # Handle DD-MM-YYYY format
            if re.match(r'\d{1,2}-\d{1,2}-\d{4}', date_str):
                parts = date_str.split('-')
                if len(parts) == 3:
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # Return as is if already in YYYY-MM-DD format or can't parse
            return date_str

        except Exception as e:
            logger.error(f"Error normalizing date {date_str}: {e}")
            return date_str

    def extract_races_info(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract race information using the specific HTML structure:
        <div class="header-row fixture-toggle" data-id="R1">
            <div class="left">R1</div>
            <div class="title"><i class="fa fa-angle-up"></i>12:45 - FASHION HEIGHTS - MIA BIJOUX CUP - [0 - 25] - 1400m</div>
        </div>
        """
        races = []

        try:
            # Look for race headers using the specific structure
            race_headers = soup.select('div.header-row.fixture-toggle')
            logger.info(f"Found {len(race_headers)} race headers with specific selector")
            
            # If not found, try broader selectors
            if not race_headers:
                logger.info("Trying broader selectors...")
                race_headers = soup.select('div[class*="header-row"]')
                logger.info(f"Found {len(race_headers)} race headers with broader selector")
                
                if not race_headers:
                    race_headers = soup.select('div[data-id*="R"]')
                    logger.info(f"Found {len(race_headers)} elements with R data-id")

            for header in race_headers:
                race_info = self._extract_race_from_header(header)
                if race_info:
                    races.append(race_info)

            # Sort races by race number
            races.sort(key=lambda x: x['race_number'])
            logger.info(f"Successfully extracted {len(races)} races")

        except Exception as e:
            logger.error(f"Error extracting races info: {e}")

        return races

    def _extract_race_from_header(self, header_element) -> Optional[Dict]:
        """Extract race information from a header element"""
        try:
            # Extract race index from data-id attribute
            race_index = header_element.get('data-id', '')
            
            # Extract race number from race index (e.g., "R1" -> 1)
            race_number = 1
            if race_index:
                match = re.search(r'R(\d+)', race_index, re.IGNORECASE)
                if match:
                    race_number = int(match.group(1))

            # Extract race title and time from the title div
            title_div = header_element.select_one('div.title')
            race_time = "TBD"
            race_title = f"Race {race_number}"
            
            if title_div:
                title_text = title_div.get_text(strip=True)
                
                # Extract time and title from format: "12:45 - FASHION HEIGHTS - MIA BIJOUX CUP - [0 - 25] - 1400m"
                time_match = re.search(r'^(\d{1,2}:\d{2})', title_text)
                if time_match:
                    race_time = time_match.group(1)
                    # Remove the time from the title to get the race name
                    race_title = title_text.replace(f"{race_time} - ", "").strip()
                else:
                    race_title = title_text

            return {
                'race_index': race_index or f'R{race_number}',
                'race_time': race_time,
                'race_title': race_title,
                'race_number': race_number
            }
            
        except Exception as e:
            logger.error(f"Error extracting race from header: {e}")
            return None

    def extract_horses_for_race(self, soup: BeautifulSoup, race_index: str) -> List[Dict]:
        """
        Extract horse information for a specific race using the structure:
        <div class="rows" data-id="R1">
            <div class="header">...</div>
            <div class="row">
                <div class="number">1</div>
                <div class="horse">CAPTAIN'S CONCORT<i class="fas fa-smile smiley"></i><i class="fas fa-smile smiley"></i></div>
                <div class="odds">310</div>
                <div class="odds">140</div>
            </div>
            ...
        </div>
        """
        horses = []

        try:
            # Look for horse rows using the specific structure
            horse_rows = soup.select(f'div.rows[data-id="{race_index}"] div.row')
            logger.info(f"Found {len(horse_rows)} horse rows for {race_index}")
            
            # If not found, try broader selectors
            if not horse_rows:
                horse_rows = soup.select(f'[data-id="{race_index}"] div.row')
                logger.info(f"Found {len(horse_rows)} horse rows with broader selector for {race_index}")

            for row in horse_rows:
                horse_info = self._extract_horse_from_row(row)
                if horse_info:
                    horses.append(horse_info)

            # Sort horses by number
            horses.sort(key=lambda x: x['horse_number'])
            logger.info(f"Successfully extracted {len(horses)} horses for {race_index}")

        except Exception as e:
            logger.error(f"Error extracting horses for race {race_index}: {e}")

        return horses

    def _extract_horse_from_row(self, row_element) -> Optional[Dict]:
        """Extract horse information from a row element"""
        try:
            # Extract horse number from the number div
            number_div = row_element.select_one('div.number')
            horse_number = 0
            if number_div:
                number_text = number_div.get_text(strip=True)
                try:
                    horse_number = int(number_text)
                except ValueError:
                    logger.warning(f"Could not parse horse number: {number_text}")

            # Extract horse name from the horse div
            horse_div = row_element.select_one('div.horse')
            horse_name = "Unknown"
            if horse_div:
                horse_name = horse_div.get_text(strip=True)
                # Clean up horse name (remove any extra whitespace)
                horse_name = re.sub(r'\s+', ' ', horse_name).strip()

            # Extract Win odds from the first odds div
            odds_divs = row_element.select('div.odds')
            horse_odds = 0.0
            if odds_divs and len(odds_divs) >= 1:
                # The first odds div is the "Win" odds, second is "Place"
                win_odds_text = odds_divs[0].get_text(strip=True)
                try:
                    # Convert odds to decimal format (e.g., "310" -> 3.10)
                    horse_odds = float(win_odds_text) / 100.0
                except ValueError:
                    logger.warning(f"Could not parse win odds: {win_odds_text}")

            return {
                'horse_number': horse_number,
                'horse_name': horse_name,
                'odds': horse_odds
            }
            
        except Exception as e:
            logger.error(f"Error extracting horse from row: {e}")
            return None

    def scrape_racecard(self) -> Dict:
        """Main method to scrape the complete racecard"""
        logger.info("Starting racecard scraping...")

        # Setup the driver
        if not self.setup_driver():
            return {}

        try:
            # Get page content
            soup = self.get_page_content()
            if not soup:
                logger.error("Failed to fetch page content")
                return {}

            # Extract race date
            race_date = self.extract_race_date(soup)
            logger.info(f"Race date: {race_date}")

            # Extract races information
            races = self.extract_races_info(soup)
            logger.info(f"Found {len(races)} races")

            # Extract horses for each race
            for race in races:
                horses = self.extract_horses_for_race(soup, race['race_index'])
                race['horses'] = horses
                logger.info(f"Race {race['race_index']}: {len(horses)} horses found")

            return {
                'race_date': race_date,
                'races': races,
                'scraped_at': datetime.now().isoformat(),
                'source_url': self.base_url,
                'method': 'headless_browser'
            }

        finally:
            # Always close the driver
            if self.driver:
                self.driver.quit()
                logger.info("✓ WebDriver closed")

    def save_to_csv(self, racecard_data: Dict, filename: str = "racecard.csv"):
        """Save racecard data to CSV files in organized structure"""
        try:
            # Ensure CSV directory exists
            csv_dir = "data/csv"
            os.makedirs(csv_dir, exist_ok=True)

            # Create main races table
            races_data = []
            for race in racecard_data['races']:
                races_data.append({
                    'Race_Index': race['race_index'],
                    'Race_Time': race['race_time'],
                    'Race_Title': race['race_title'],
                    'Number_of_Horses': len(race.get('horses', []))
                })

            races_df = pd.DataFrame(races_data)
            races_df.to_csv(f"{csv_dir}/races_{filename}", index=False, encoding='utf-8')
            logger.info(f"Races data saved to {csv_dir}/races_{filename}")

            # Create horses table for each race
            for race in racecard_data['races']:
                if race.get('horses'):
                    horses_data = []
                    for horse in race['horses']:
                        horses_data.append({
                            'Race_Index': race['race_index'],
                            'Horse_Number': horse['horse_number'],
                            'Horse_Name': horse['horse_name'],
                            'Odds': horse['odds']
                        })

                    horses_df = pd.DataFrame(horses_data)
                    horses_df.to_csv(f"{csv_dir}/horses_{race['race_index']}_{filename}",
                                   index=False, encoding='utf-8')
                    logger.info(f"Horses data for {race['race_index']} saved to {csv_dir}/horses_{race['race_index']}_{filename}")

            # Create combined horses table
            all_horses_data = []
            for race in racecard_data['races']:
                if race.get('horses'):
                    for horse in race['horses']:
                        all_horses_data.append({
                            'Race_Index': race['race_index'],
                            'Race_Time': race['race_time'],
                            'Race_Title': race['race_title'],
                            'Horse_Number': horse['horse_number'],
                            'Horse_Name': horse['horse_name'],
                            'Odds': horse['odds']
                        })

            if all_horses_data:
                all_horses_df = pd.DataFrame(all_horses_data)
                all_horses_df.to_csv(f"{csv_dir}/all_horses_{filename}", index=False, encoding='utf-8')
                logger.info(f"All horses data saved to {csv_dir}/all_horses_{filename}")

        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")

    def save_to_json(self, racecard_data: Dict, filename: str = "racecard.json"):
        """Save racecard data to JSON file in organized structure"""
        try:
            # Ensure JSON directory exists
            json_dir = "data/json"
            os.makedirs(json_dir, exist_ok=True)
            
            json_path = f"{json_dir}/{filename}"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(racecard_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Racecard data saved to {json_path}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")

    def print_racecard_summary(self, racecard_data: Dict):
        """Print a formatted summary of the racecard"""
        print(f"\n{'='*80}")
        print(f"RACECARD SUMMARY - {racecard_data['race_date']}")
        print(f"Source: {racecard_data.get('source_url', 'Unknown')}")
        print(f"Method: {racecard_data.get('method', 'Unknown')}")
        print(f"Scraped at: {racecard_data.get('scraped_at', 'Unknown')}")
        print(f"{'='*80}")

        if not racecard_data['races']:
            print("No races found!")
            return

        for race in racecard_data['races']:
            print(f"\n{race['race_index']}: {race['race_time']} - {race['race_title']}")
            print(f"{'-'*70}")

            if race.get('horses'):
                print(f"{'No.':<4} {'Horse Name':<35} {'Odds':<10}")
                print(f"{'-'*4} {'-'*35} {'-'*10}")
                for horse in race['horses']:
                    odds_str = f"{horse['odds']:.2f}" if horse['odds'] > 0 else "N/A"
                    print(f"{horse['horse_number']:<4} {horse['horse_name']:<35} {odds_str:<10}")
            else:
                print("No horse information available")

        print(f"\n{'='*80}")
        print(f"Total races: {len(racecard_data['races'])}")
        total_horses = sum(len(race.get('horses', [])) for race in racecard_data['races'])
        print(f"Total horses: {total_horses}")
        print(f"{'='*80}")


def main():
    """Main function to run the Selenium scraper"""
    print("SMS Pariaz Racecard Scraper")
    print("=" * 50)
    
    # Create scraper instance (headless by default)
    scraper = RacecardScraper(headless=True)

    # Scrape the racecard
    racecard_data = scraper.scrape_racecard()

    if racecard_data and racecard_data['races']:
        # Print summary
        scraper.print_racecard_summary(racecard_data)

        # Save to files
        scraper.save_to_csv(racecard_data, "racecard.csv")
        scraper.save_to_json(racecard_data, "racecard.json")

        print(f"\nScraping completed successfully!")
        print(f"Files created:")
        print(f"- races_racecard.csv (main races table)")
        print(f"- horses_R1_racecard.csv, horses_R2_racecard.csv, etc.")
        print(f"- all_horses_racecard.csv (combined horses table)")
        print(f"- racecard.json (complete data in JSON format)")
    else:
        print("Failed to scrape racecard data or no races found")
        print("This could be due to:")
        print("- Website being unavailable")
        print("- Changed website structure")
        print("- Network connectivity issues")
        print("- No races scheduled for today")


if __name__ == "__main__":
    main()